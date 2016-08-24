from flask import Blueprint, render_template, request, jsonify, current_app
from errors import ExperimentError
from models import Session, CategorySwitch, EventData, KeepTrack, QuestionData
from sqlalchemy.exc import SQLAlchemyError
from database import db
import db_utils
import datetime
import json

import utils

# Status codes
NOT_ACCEPTED = 0
ALLOCATED = 1
STARTED = 2
COMPLETED = 3
QUITEARLY = 6

experiments = Blueprint('experiments', __name__,
                        template_folder='exp/templates', static_folder='exp/static')

experiment_list = {'28': 'keep_track', '29' : 'category_switch'}

@experiments.route('/', methods=['GET'])
def index():
    """ Welcome page, but there is none so right now its blank"""
    return render_template("default.html")

@experiments.route('/task/<exp_name>', methods=['GET'])
@utils.nocache
def start_exp(exp_name):
    """ Serves up the experiment applet. 
    If experiment is ongoing or completed, will not serve. 

    Querystring args (required):
    token: External token
    """

    if not utils.check_qs(request.args, ['token']):
        raise ExperimentError('improper_inputs')
    else:
        token = request.args['token']

    if current_app.config['DEVELOP'] is True:
        refer =  'https://agile-ratio-824.appspot.com/'
    else:
        refer = 'http://co-twins.appspot.com/'

    current_app.logger.info("Referrer: %s" %
                            (request.referrer))
    
    browser, platform = utils.check_browser_platform(request.user_agent)

    current_app.logger.info("Subject: %s entered with %s platform and %s browser" %
                            (token, platform, browser))

    session = Session(token=token, browser=browser, platform=platform,
                      status=1, exp_name=exp_name, begin_session=datetime.datetime.now())
    db.session.add(session)
    db.session.commit()

    return render_template(exp_name + "/exp.html", experimentname=exp_name, 
        sessionid=session.session_id, debug=current_app.config['EXP_DEBUG'],
        uniqueid=token, refer=refer)


@experiments.route('/inexp', methods=['POST'])
def enterexp():
    """
    AJAX listener that listens for a signal from the user's script when they
    leave the instructions and enter the real experiment. After the server
    receives this signal, it will no longer allow them to re-access the
    experiment applet (meaning they can't do part of the experiment and
    refresh to start over). This changes the current sessions's status to 2.

    Querystring args (required):
    sessionid: session identifier
    """

    if not utils.check_qs(request.form, ['sessionid']):
        return jsonify({"status": "improper_inputs"})
        current_app.logger.error("Improper inputs in /inexp")
    else:
        session_id = request.form['sessionid']

    session = Session.query.filter_by(session_id=session_id).first()

    if session:
        session.status = 2
        session.begin_experiment = datetime.datetime.now()
        db.session.commit()

        current_app.logger.info(
            "User has finished the instructions in session id: %s, experiment name: %s", 
            session_id, session.exp_name)
        resp = {"status": "success"}
    else:
        current_app.logger.error(
            "DB error: Unique user and experiment combination not found.")
        # it is the dictionary
        resp = {"status": "error, session not found"}

    return jsonify(**resp)

@experiments.route('/sync/<session_id>', methods=['GET'])
def load(session_id=None):
    """
    Return a few attributed of session back to Backbone.js.
    This is forced by Backbone, and doesn't do much.  """

    current_app.logger.info("GET /sync route with id: %s" % session_id)
    try:
        session = Session.query.filter_by(session_id=session_id).one()
    except SQLAlchemyError:
        resp = {"status": "bad request"}
        current_app.logger.error("DB error: Unique user not found.")
    else:
        resp = {
            "sessionid": session.session_id
        }

    return jsonify(**resp)


@experiments.route('/sync/<session_id>', methods=['PUT'])
def update(session_id=None):
    """ Sync backbone model with appropriate database.  """

    current_app.logger.info("PUT /sync route with id: %s" % session_id)
    resp = None

    try:
        session = Session.query.filter_by(session_id=session_id).one()
    except SQLAlchemyError:
        resp = {"status": "bad request"}
        current_app.logger.error("DB error: Unique user not found.")

    # Check JSON validity
    if utils.check_valid_json(request.get_data()):
        valid_json = json.loads(request.get_data())
    else:
        resp = {"status": "bad request"}
        current_app.logger.error("Invalid JSON")

    current_app.logger.info(
        "Current trial: %s, session id: %s " % (valid_json['currenttrial'],
            valid_json['sessionid']))

    # For each trial, pass to appropriate parser, if not in db
    for json_trial in valid_json['data']:
        if session.exp_name == "category_switch":
            experiment_class = CategorySwitch
        elif session.exp_name == "keep_track":
            experiment_class = KeepTrack

        db_trial, new = db_utils.get_or_create(db.session,
            experiment_class, token=session.token, session_id=session.session_id,
            trial_num=json_trial['current_trial'])

        # If the trial is new, add data
        if new:
            db_trial.add_json_data(json_trial)
            db.session.commit()

    # For each event, pass to parser, if not in db
    for json_event in valid_json['eventdata']:
        db_event, new = db_utils.get_or_create(db.session, EventData,
            token=session.token, session_id=session.session_id, exp_name=session.exp_name, 
            timestamp = utils.convert_timestamp(json_event['timestamp']))

        if new:
            db_event.add_json_data(json_event)
            db.session.commit()

    if valid_json['questiondata'] != {}:
        # For the QuestionData, pass to parser, if not in db
        db_ques, new = db_utils.get_or_create(db.session, QuestionData,
                    token=session.token, session_id=session.session_id, exp_name=session.exp_name)
        db_ques.add_json_data(valid_json['questiondata']) 
        db.session.commit()

    if resp is None:
        resp = {"status": "success"}

    return jsonify(**resp)


@experiments.route('/quitter', methods=['POST'])
def quitter():
    """ Mark quitter as such. """
    if not utils.check_qs(request.form, ['sessionid']):
        resp = {"status": "bad request"}

    else:
        session_id = request.form['sessionid']

        try:
            # pull records from Session table to update
            session = Session.query.filter(
                Session.session_id == session_id).one()
            session.status = 6
            db.session.commit() 
            resp = {"status": "marked as quitter"}

        except SQLAlchemyError:
            resp = {"status": "bad request"}

    return jsonify(**resp)


@experiments.route('/worker_complete', methods=['POST'])
def worker_complete():
    """Complete worker."""

    if not utils.check_qs(request.form, ['sessionid']):
        resp = {"status": "bad request"}
    else:
        session_id = request.form['sessionid']
        current_app.logger.info(
            "Completed experiment %s" % (session_id))
        try:
            # pull records from Session table to update
            session = Session.query.filter(
                Session.session_id == session_id).one()
            session.status = 3
            db.session.commit()
            resp = {"status": "marked as done"}
            current_app.logger.info("Subject: %s marked as done" %
                        str(session.token))

        except SQLAlchemyError:
            raise ExperimentError('unknown_error', session_id=request.args['sessionid'])
            resp = {"status": "db error"}

        return jsonify(**resp)

# Generic route
@experiments.route('/<pagename>')
@experiments.route('/<foldername>/<pagename>')
def regularpage(foldername=None, pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    from jinja2.exceptions import TemplateNotFound

    try:

        if foldername is None and pagename is not None:
            return render_template(pagename)
        else:
            return render_template(foldername+"/"+pagename)
    except TemplateNotFound:
        return render_template("error.html", errornum=404)


@experiments.errorhandler(ExperimentError)
def handle_exp_error(exception):
    """Handle errors by sending an error page."""
    current_app.logger.error(
        "%s (%s) %s", exception.value, exception.errornum, str(dict(request.args)))
    return exception.error_page(request, "support@cotwins.org") ## Update this email
