# GfG Interactive Survey Module
This module serves interactive javascript surveys (such as cognitive tasks) for GenesforGood. This module was original based on psiTurk, and uses an identical javascript API to send data back to the server (here called dataHandler).

## Installation
Basic dependencies:

* Flask
* Flask-Migrate
* Flask-SQLAlchemy
* Alembic

If using Postgres:
* Psycopg2

If using MySQL:
* mysql-python

To install dependencies run the following command. It is reccomended you do this in a virtual environment (set up virtualenv one folder above this one). Make sure to also install the correct dependency for your DB manually.

    pip -r requirements.txt

### Configuration
The type of configuration is set using the config.ini file. By default, it is set to "HomeConfig" which is for local testing. Edit this file to match the appropriate configuration (e.g. Staging, Production).

The file wsgi/config.py specifies configuration details, such as the database URI and credentials to use.
COPY example_config.py to config.py and edit with the appropriate details. Ensure that you have credted a specific database to be used.

### Database set up and inital migration
We use Alembic to track database migrations. To initate the db and perform the first migration, run the following commands:

    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade


## Deployment and testing
### Local testing

To test locally, simply type the following:

    python wsgi/app.py

This should launch on localhost for your local testing pleasure.


### OpenShift 3 deployment
- Create a new "project" and add Python 2.7 (with this repo) and PostgresSQL deployments.
- Set up the environment variables required to match `config.py`. You need to set up `DATABASE_USER` `DATABASE_NAME` and `DATABASE_PASSWORD` from the secrets of the postgresql deployment.
- Use the terminal in for the Python deployment to init and migrate the database.

## Documentation
Here I will document various aspects of this project in order to allow you to edit the server and deploy new assesments.

The flask project has the following files/sections:

 * The basic app.py file. In this app this doesn't do much except link the rest of the following parts together
 * experiments.py - This file handles all routes to /exp and serves the individual experiments. **This is the most important section for actually serving experiments and collecting data**.
 * dashboard.py - This file handles routes to /dashboard and is used to display live summary statistics to the experiments. This allows you to keep an eye on your data. This is not very developed yet but it allows you to serve any matplotlib plots using mpld3 or bokeh plots.
 * errors.py - This file contains an error handler that routes to an appropriate error page when things go wrong
 * models.py - This file defines the data models.
 * manage.py - This file contains the logic for updating your database. See deployment for more info. Ensure to run the relevant commands when models.py is updated.

### Experiments
I will now focus on experiments.py and the exp/ subfolder as this is the core to serving experiments.

The experiments.py file serves the experiments set up in the app. Without editing more than a line of code, it is possible to add a new task to the server. In experiments.py there is a list that defines the experiments. Each experiment is a tuple of (experiment_folder, "Experiment Name").

Each experiment has its own folders under both /exp/static and /exp/templates. For example, the task "keep_track" has its javascript files under:
/exp/static/keep_track/js/
and its main html template under
/exp/static/keep_track/exp.html

To add an experiment to the server, ensure the experiments files are as above and that you edit the list of experiments. The server should now be serving your new experiment under the following. Note that to run without error the server expects you to also specify a user ID and optionally if the task is in debug mode (will be noted in the DB and allows you to refresh task)

	/exp/task?experimentName=YOUR_EXPERIMENT_NAME&uniqueId=1234&debug=True

If you have added multple tasks, you can send subjects to a landing page that lists the tasks yet to complete by the uniqueId and any custom instructions you want to add:

	/exp/?&uniqueId=1234

You can edit this landing page (/exp/templates/begin.html)

### Experiment setup and dataHandler.js API
This is how you set up your javascript experiment to work with this server.

The only real requirement is that an exp.html file exists under the right folder and that that file defines the following variable in javascript:

	<script type="text/javascript">
		// These fields provided by the psiTurk Server
		var uniqueId = "{{ uniqueId }}";  // a unique string identifying the worker/task
		var experimentName = "{{ experimentName }}"
		var debug = "{{ debug }}"
	</script>

and imports important libraries such as jQuery,  this app's dataHandler.js, and it's own js files, of course:

	<script src="static/js/dataHandler.js"></script>
	<script src="static/{{ experimentName }}/js/common.js"></script>
	<script src="static/{{ experimentName }}/js/kt.js"></script>
	<script src="static/{{ experimentName }}/js/kt_instructions.js"></script>
	<script src="static/{{ experimentName }}/js/task.js"></script>
	<script src="static/lib/jquery-min.js" type="text/javascript"> </script>

In the main Javascript file, define a dataHandler object and preload any pages you want.
In this example I'm preloading the post-questionnaire and debriefing file:

	dataHandler = DataHandler(uniqueId, experimentName);
	dataHandler.preloadPages(['postquestionnaire.html', experimentName + '/debriefing.html']);

You can then do the following things with the dataHandler object:

* Load preloaded page

	return $('body').html(dataHandler.getPage('postquestionnaire.html'));
* Save trial data (an array)

	dataHandler.recordTrialData(['500ms', 'trial1'])
- Record unstructured data (e.g. questionnaire info)

	dataHandler.recordUnstructuredData('openended', $('#openended').val());
* Save data to server (do this somewhat often and before quitting)

	dataHandler.saveData();
* Complete the task and get set back to landing page (edit this for the message you want to send after the task is done or edit the code to close window or navigate elsewhere)

	dataHandler.completeHIT();

Aside from that, its up to you to build whatever javascript assesment you want and this server should record the data and serve it appropriately.
