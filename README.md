# COTwins Server
This is the repository for COTwins, serving executive functions tasks on Openshift. The codebase here reflects the live code on assesment-cotwins.rhcloud.com 


To give credit where credit is due, this is a heavily modified version of the awesome psiTurk project. I stripped all the stuff I didn't need and added other functionality. 

Below, I describe the organization of the project, how to add tasks to the project, and how to deploy the server. 

## Installation
This project has a few dependencies, but  not all are necessary for serving the tasks. The more complex dependencies are for the dashboard.

Basic dependencies:

* Flask
* Flask-Migrate
* Flask-SQLAlchemy
* Alembic
* Psycopg2
* PostgreSQL database

Most of these are quite easy to install using pip. The easiest way to install a PostgreSQL database on a mac is using postgres.app. 

## Testing & Deployment
### Local testing
To test this app localy, install the dependencies and set the URI of your database using the 'DATABASE_URL' environment variable. E.g.:

    export DATABASE_URL="postgresql://localhost/gfg_dev"
This is automatically set up for you if you launch the virtualenv in this repo:

    source bin/activate

Next, you must initiate the database and migrate it for the first time using the following commands

    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    
Any time you change the data model in models.py, run the last two commands again to update your SQL database. 

If you've done everything right, you should be able to launch flask locally to test:

    python wsgi/app.py
   
This should launch on localhost for your local testing pleasure. 
	
### OpenShift deployment
OpenShift is a great platform-as-a-service (PaaS) that enables rapid deployment using Github. The easiest way to launch this service is to create a new app on OpenShift that has both "Python 2.7" and "PostgreSQL" installed as cartridges. OpenShift allows you to use a Github repository as a starting point for your app. Simply point it to this repo and it should install everything correctly. 

The PostgreSQL cartridge has a URI that includes the authentication information and is saved as a environment variable. This app will automatically read it (in accordance with config.py) as long as you tell it that you are testing on OpenShift. Do so by setting the environment variable APP_SETTINGS to config.StagingConfig using the rhc command line tools:

    rhc env set APP_SETTINGS="config.StagingConfig" -a App_Name
    
 If everything went well, your app should be up and running on rhcloud. 

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
