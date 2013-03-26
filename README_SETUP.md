Setting up Your Class2Go Dev Environment
========================================

These instructions should help you get started setting up a dev
environment.  You should be able to do most of your development on
your laptop by running a local database (mysqld) and storing files
locally instead of in S3.

The majority of our dev team uses Macs, so the Mac instructions are
generally the most up to date.  But we do have some developers who
have had windows or Ubuntu Linux as their day-to-day dev machines, so
we know it works.

If you have suggestions how to improve these notes, please improve
them and send us a pull request!

* [Mac OS X](#mac)
* [Windows](#windows)
* [Linux](#linux)
* [Configuring Django](#config)
* [Generating Test Data](#testdata)

It is a big step to go from a dev instance to a full-on deployed
cloud instance.  Instructions for that are forthcoming.

<a name="mac"></a>
For Mac
-------------

General Instructions:

* Set-up Python
* Set-up Python's virtual env
* Set-up Django
* Set-up Mysql
* Set-up test suite

For MAC OS-X Lion: Instructions mainly taken from
http://www.tlswebsolutions.com/mac-os-x-lion-setting-up-django-pip-virtualenv-and-homebrew/

Some people don't have their normal user set up with write permissions
for all these commands that modify the environment (brew, easy_install,
pip).  For all of those you should plan on running your own sudo
prefix for these.

1. Install XCode from the Apple App Store Version 4.5 or later

1. Within XCode, add the command line tools: Preferences -> Download ->
"Command Line Tools" -> Install button

1. Install Homebrew:

        /usr/bin/ruby -e "$(curl -fsSkL http://raw.github.com/mxcl/homebrew/go)"

1. Install Python (we are expecting 2.7.x):

        brew install readline sqlite gdbm

1. If you plan on running in a virtual environment, then you probably 
want to instally your own python.  But if not, then you already have 
python on your machine (in /usr/bin/python), in which case you *shouldn't* 
install another copy of python (in /usr/local/bin/python).  
But if you want to do it with:

        brew install python --universal --framework

1. Install mysql

    Download mysql: dev.mysql.com/downloads/mysql
    Look for the DMG of the latest 64-bit version (10.6 will work)

    Install the mysql-5.x-osx10.x-x86_64.pkg
    Install the MySQLStartupItem.pkg
    Install the MySQL.prefpane
    – Start MySQL Server
    – Check Automatically Start on startup

1. Install Sequel Pro (optional)
    
    www.sequelpro.com

1. Install pip, a python package manager

        easy_install pip

1. Install python's virtual env 

        pip install virtualenv

1. Install virtualenvwrapper: (optional)

        sudo pip install virtualenvwrapper

    a. Verify installation location of virtualenv and virtualenvwrapper:

        ls /usr/local/bin/

    a. Check out your PATH to see if /usr/local/bin comes before /usr/bin:

        echo $PATH
    (If not, add `export PATH=/usr/local/bin:$PATH` to your .bashrc)

    a. Edit login script:

        vim .bashrc

    a. ...and add the following:

        # virtualenv setup -- use Distribute by default
        export VIRTUALENV_DISTRIBUTE=true

        # virtualenvwrapper setup
        export WORKON_HOME=~/class2go-venv
        export PROJECT_HOME=~/class2go-projects
        export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'
        export VIRTUALENVWRAPPER_VIRTUALENV=`which virtualenv`
        source /usr/local/bin/virtualenvwrapper.sh

    a. Source login script so env vars take effect:

        source ~/.bashrc
    (Sourcing should auto-create your virtual environment base dir)

    a. Check out new virtual base directory:

        ls class2go-venv/

    a. Make sure PROJECT_HOME is defined

        echo $PROJECT_HOME

    a. Make new project directory:

        mkdir -p $PROJECT_HOME

    a. Issue command to set up new project subdirectory and link it to virtual env:

        mkproject class2go

1. Start using the virtual environment that we just created.

        . ./class2go-venv/bin/activate

    WARNING:  You need to do this from whatever shell you're using.
    You can tell this because is puts an environment indicator at
    the beginning of your prompt.

1. Install all the dependencies with this command:

    pip install -r requirements.txt

And subsequently all of the optional dependencies with this command:
 
    pip install -r suggested_requirements.txt

If you aren't using pip or want to install packages manually, just open the
requirements files and run the local equivalent of 

        pip install <packagename>

for each package listed therein.

1. [Nota Bene] [Optional] Install chrome for Selenium testing

        # chromedriver - list of options available here:
        # https://code.google.com/p/chromedriver/downloads/list
        curl -O http://chromedriver.googlecode.com/files/chromedriver_mac_23.0.1240.0.zip
        unzip chromedriver_mac_23.0.1240.0.zip
        # move onto your path
        sudo mv ./chromedriver /usr/local/bin/
        # install Chrome -- download from https://www.google.com/intl/en/chrome/browser/

[NB:] If instead you wish to use firefox, you can use the default Selenium firefox
driver by setting the environment variable C2G_SELENIUM_WEBDRIVER=firefox. For 
flash tests to pass, you will have to have the flash player plugin installed. 

1. [Optional] Install dependenices to run selenium tests "headless"

        # TODO: Figure out how to run headless on Mac OSX (see Linux section for starters)

1. Setup the account and database in MySql (Sequel Pro)

        create database class2go;
        grant all on class2go.* to class2go@'localhost' identified by 'class2gopw';
        grant all on class2go.* to class2go@'127.0.0.1' identified by 'class2gopw';

1. Set up some folders for logs and the celery database.

    Put them somewhere writable. Make sure the django settings.py entry for LOGGING_DIR and the database.py entry for DATABASES.celery.NAME match these locations.

        mkdir /home/account/django-logs/
        mkdir /home/account/sqlite3/

1. In the main folder, make a copy of database_example.py to database.py
and edit the DATABASES strings as follows substituting proper values for your system.

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'class2go',
                'USER': 'class2go',
                'PASSWORD': 'class2gopw',
                'HOST': '',
                'PORT': '',
            },
            'celery': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/Users/account/sqlite3/celerydb.sqlite',
            },
        }

1. Setup initial db from the main folder

        ./manage.py syncdb  ######## answer no to the superuser question for now
        ./manage.py migrate
        ./manage.py syncdb --database=celery
        ./manage.py migrate --database=celery

    At this point you should be able to look at the django database in
    your local mysql and see a bunch of c2g_* tables. Now you should create the super user

        ./manage.py createsuperuser

	Yay. :)

1. From the main folder, run server on whatever port you want:

        python manage.py runserver 8100

1. Visit localhost:8100 in your web browser and confirm that you get a C2G page.


<a name="windows"></a>
For Windows
----------------

[NB] While we try to keep these instructions up to date, the majority of the
developers working on Class2Go are using MacOS or Linux. You may have the 
best luck if you follow the directions in one of those sections in parallel 
with the directions here.

Eclipse Users and/or WAMP users:

The following versions seem to be compatible:

- Python: 2.7.3
- Eclipse for PHP: Helios (http://download.eclipse.org/releases/helios)
- PyDev plugin for Eclipse: 2.5.0 (http://pydev.org/updates)
- Egit plugin for Eclipse: (http://download.eclipse.org/egit/updates)
- WAMPServer: 2.1


Steps:

2. Install Eclipse

2. Install Egit and configure it to the github repos (https://github.com/Stanford-Online/class2go)
    For this you would need someone to set you up with access to this repos.
    Note, when configuring the Remote Push Url you'll need to add ".git" on the end:
    (git clone https://github.com/Stanford-Online/class2go.git)

**Requirements**

2. Prereqs:
	If you do not have the following, install them:
		python 2.7
		django
		easy_install
		pip
		python image library (pip install PIL)
        django_storages
        boto

2. Install South, the database schema migration tool: (this will be inside the virtualenv)
    easy_install South

2. Install the other libraries listed in the requirements.txt and suggested_requirements.txt

2. Create a database called c2g (for example).

2. Copy database.example.py to database.py.

2. In database.py, append 'mysql' to ENGINE, and enter the name of the database you created in step 1, and the credentials of an authorized user of the database (user 'root' and empty password may work on MySQL unless you specified otherwise during the MySQL setup)

2. Make sure you're in the src/class2go/main directory (wherever that is for you)

2. 'python manage.py syncdb' followed by 'python manage.py migrate' to create the required database tables and make sure the schema is up to date.You will be asked to create your admin account on the way. Skip it. You will later be able to create a user and promote it to admin manually using your DBMS client.

        ./manage.py syncdb  ######## answer no to the superuser question for now
        ./manage.py migrate
        ./manage.py syncdb --database=celery
        ./manage.py migrate --database=celery

At this point you should be able to look at the django database in your local mysql and see a bunch of c2g_* tables. Now you should create the super user

    ./manage.py createsuperuser

Yay. :)

2. XX -- 'python manage.py collectstatic' to copy all static files to the directory specified in settings.py.

2. 'python manage.py runserver xxxx' to run a dev server on port number xxxx. Example: xxxx = 8000

2. Visit localhost:xxxx in your web browser and confirm that you get a C2G page.




<a name="linux"></a>
For Linux
-----------------

This assumes you have mysql and python installed.  These instructions
also include info for virtualenvwrapper, which contains useful tools
for virtualenv. virtualenvwrapper can also be installed for Mac (and
probably Windows too).  If you will be using the Firefox driver for
Selenium web tests, make sure you have the Flash plugin installed. If you 
wish to install the Chrome driver, instructions for doing so can be found
below.

3. Create the database (perhaps with different username and password):

        sudo mysql mysql
        create database c2g;
        CREATE USER 'c2g_username'@'localhost' IDENTIFIED BY 'c2g_passwd';
        GRANT ALL PRIVILEGES ON c2g . * TO 'c2g_username'@'localhost';
        FLUSH PRIVILEGES;

3. Install pip:

        sudo apt-get install python-pip

3. Install virtualenv:

        sudo pip install virtualenv

3. Install virtualenvwrapper:

        sudo pip install virtualenvwrapper

3. Verify installation location of virtualenv and virtualenvwrapper:

        ls /usr/local/bin/

3. Check out your PATH to see if /usr/local/bin comes before /usr/bin:

        echo $PATH
    (If not, add `export PATH=/usr/local/bin:$PATH` to your .bashrc)

3. Edit login script:

        vim .bashrc

3. ...and add the following:

        # virtualenv setup -- use Distribute by default
        export VIRTUALENV_DISTRIBUTE=true

        # virtualenvwrapper setup
        export WORKON_HOME=~/DevEnvs
        export PROJECT_HOME=~/DevProjects
        export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'
        export VIRTUALENVWRAPPER_VIRTUALENV=`which virtualenv`
        source /usr/local/bin/virtualenvwrapper.sh

3. Source login script so env vars take effect:

        source ~/.bashrc
    (Sourcing should auto-create your virtual environment base dir)

3. Check out new virtual base directory:

        ls DevEnvs/

3. Make sure PROJECT_HOME is defined

        echo $PROJECT_HOME

3. Make new project directory:

        mkdir -p $PROJECT_HOME

3. Issue command to set up new project subdirectory and link it to virtual env:

        mkproject class2go

3. Once inside virtual env/project directory, install django:

        pip install django

3. Clone class2go repo from github:

        git clone https://github.com/Stanford-Online/class2go.git .

3. Check out where your mysql is installed, make sure mysql_config exists in the dir:

        ls `which mysql`

3. Need to install mysql_config if it's not there:

        sudo apt-get install libmysqlclient-dev

3. Might need some extra python developer stuff:

        sudo apt-get install python-dev

3. Install all the dependencies with this command:

    pip install -r requirements.txt

And subsequently all of the optional dependencies with this command:
 
    pip install -r suggested_requirements.txt

If you aren't using pip or want to install packages manually, just open the
requirements files and run the local equivalent of 

        pip install <packagename>

for each package listed therein.

3. [Nota Bene] [Optional] Install chrome for Selenium testing

        # chromedriver - list of options available here:
        # https://code.google.com/p/chromedriver/downloads/list
        curl -O http://chromedriver.googlecode.com/files/chromedriver_linux32_23.0.1240.0.zip
        unzip chromedriver_linux32_23.0.1240.0.zip
        # move onto your path
        sudo mv ./chromedriver /usr/local/bin/
        # install Chrome -- download from https://www.google.com/intl/en/chrome/browser/

[NB:] If instead you wish to use firefox, you can use the default Selenium firefox
driver by setting the environment variable C2G_SELENIUM_WEBDRIVER=firefox. For 
flash tests to pass, you will have to have the flash player installed. On recent 
64-bit Ubuntus, this comes from 'flashplugin-installer'

3. [Optional] Install dependenices to run selenium tests "headless"

        pip install pyvirtualdisplay
        sudo apt-get install xvfb xserver-xephyr

Note that to use this, you will have to set the environment variable C2G_HEADLESS_TESTS=1.

3. [Optional] Install wkhtmltopdf for statement generation. xhtmltopdf can be
   used, but it has poor CSS support. For nice CSS support, you can use
   embedded webkit with wkhtmltopdf:

        sudo apt-get install wkhtmltopdf

Note that this pulls in number of dependencies. It's generally not recommended
to install all of this anywhere it's not strictly needed. You will also require
the suggested python-pdfkit library from pypi.

3. Go to "main" dir and copy over database settings file:

        cd main
        cp database_example.py database.py

3. Edit file and add db name, username and password (see mac instructions)

        vim database.py

3. Run syncdb to create database tables

        ./manage.py syncdb  ######## answer no to the superuser question for now
    Might need to issue "syncdb" command a couple times if there are errors. The
    first time, it will ask you for username and password for the database

3. Migrate user stuff over:

        ./manage.py migrate

Now you should create the super user

        ./manage.py createsuperuser

Yay. :)


3. Update settings file and change STATIC\_ROOT to "static/":

        vim settings.py

3. Make sure directory exists, or create it:

        mkdir static

3. Run collectstatic to copy stuff into your dir:

        ./manage.py collectstatic

3. Run server on whatever port you want:

        python manage.py runserver 8100


When you want to start working on your project, just do the following:

        # this should change to the correct virtualenv and cd you to project dir
        workon class2go
        python ./manage.py runserver 8100


<a name="config"></a>
Configuring Django
------------------

The "main" dir is where the django project lives.  You will spend
most of your time in there.  All the runtime application source is
under main, and the manage.py script is the interface to runtime
command line tools.

We partition our django project settings into two settings files:

* **settings.py** - Most of the project settings are in here.  This
    should be familiar to any django dev.

* **database.py** - Anything that should *not* be checked in, i.e.
    secret keys or local configuration, should be in the database.py
    file.  Upon setting up your project one of the first things you
    have to do is create your own database.py.  There is an example
    file to get you started, database_example.py.



<a name="testdata"></a>
Generating Test Data
-----------------------

1. Some schema mods were made so run: manage.py migrate

2. Take a look in c2g/views.py as there are some parameters that
    affect which data gets created. Note, if you choose the delete\_current\_data
    option it will delete your current django users so you'll have to
    recreate those users if you want.

3. To run the script that populates the data do "manage.py help db_populate" first.
    This will tell you where to setup the params for the test data.

A helper script for this exists at main/repave\_dev\_database.sh.  It
drops/recreates your dev database and then does the syncdb / migrate
/ db_populate steps so you end up with a clean database.  It requires
a ~/.my.cnf file to know what database to talk to.
