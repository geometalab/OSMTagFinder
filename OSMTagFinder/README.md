# 1   Installation Manual

This manual covers the installation on Microsoft Windows. However installation on other operating systems should be similar or is even easier.
It’s assumed, that the user has basic knowledge about Python.


## 1.1 Local installation

Requirements:
-   Administrator access
-   TagFinder projekt (e.g. from CD)
-   Python 2.7.8 is installed: https://www.python.org/download/releases/2.7.8/
-   PIP is installed:  https://pip.pypa.io/en/latest/installing.html
-   System environment variables are set to following folders (or according ones):
    -   `C:\Program Files (x86)\Python 2.7.8`
    -   `C:\Program Files (x86)\Python 2.7.8\Scripts`
-   virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/ (optional)

Steps:

1.  Create a project folder and copy the TagFinder projekt into it. The path to the root of the project, where you see all TagFinder files and packages, will be called `<projectpath>` from now on.
2.  Run the cmd console with admin rights (Right-click > Run as Administrator)
3.  Navigate to `<projectpath>`
4.  Install 3rd party libraries. Enter command: pip install –r requirements.txt
5.  TagFinder is now installed


## 1.2 Run local TagFinder server

Requirements:
-   Local installation

Steps:

1.  Check the the config file’s HOST variable. HOST should be set to 0.0.0.0 or localhost. You can also set your port with variable PORT.
2.  Run cmd console with admin rights
3.  Navigate to `<projectpath>`
4.  Run server with command: python tagfinder.py
5.  Open any browser and type localhost:5000 (default port) to see the website


## 1.3 Prepare Heroku and GIT

Requirements:
-  Local installation
-   Verified account on Heroku: https://www.heroku.com/
-   Heroku Toolbelt is installed: https://toolbelt.heroku.com/
-   GIT is installed: http://git-scm.com/downloads
-   System environment variables are set to following folders (or according ones):
-   C:\Program Files (x86)\Heroku\bin
-   C:\Program Files (x86)\git\cmd

Steps:

1.  Login to Heroku
2.  Create a new app: Dashboard > Plus sign at the upper right > give the app a name: The name will be called `<appname>` from now on >  choose region > Create App
    - Steps 1) and 2) can also be done with console commands:
		```
		heroku login
		heroku create -- stack cedar-14
		heroku apps:rename <appname> --app <previousname>
		```
		(previous name will be something like fast-lowlands-9257)
	
3.  Set config variables for the app: Personal Apps >  `<appname>`  > Settings > Reveal Config Vars > Set LANG to en_GB.UTF-8 and PYTHONIOENCODING to utf8.
4.  Run cmd console with admin rights
5.  Navigate to `<projectpath>`
6.  Create local GIT repository. Enter command: git init
7.  Add the project files to the repository. Enter command: git add –all
    (Check with command: git status)
8.  Commit the changes to repository. Enter command: git commit –m “init” (“init” is a message)
9.  Login to heroku in console (if not done so previously): Enter command: heroku login
    You will be asked to enter your login informations and probably need to create SSH keys (on new installation). Follow the procedure.

	
## 1.4 Deploy TagFinder on Heroku

Requirements:
-   Local installation
-   Your app `<appname>` is prepared on Heroku and you created a local GIT repository in `<projectpath>`

Steps:

1.  Run cmd console with admin rights
2.  Navigate to `<projectpath>`
3.  Add the project files to the repository. Enter command: git add –all
   (Check with command: git status)
4.  Commit the changes to repository. Enter command: git commit –m “init” (“init” is a message)
5.  Login to heroku in console (if not done so once before): Enter command: heroku login
    You will be asked to enter your login informations. Follow the procedure.
6.  Connect repositories. Enter command: heroku git:remote -a `<appname>`
7.  Upload files. Enter command: git push heroku master
8.  Scale dyno. Enter command: heroku ps:scale web=1
9.  Check state. Enter command: heroku ps. Check logs. Enter command: heroku logs


## 1.5 Run Thesaurus maintenance

Requirements:
-   Local installation

Steps:

1.  Run a console. It’s not recommended to run the maintenance on the Windows cmd console. Python ships with “IDLE Python”.
2.  Navigate to `<projectpath>`
3.  Run maintenance with command: python maintenance.py (or start it accordingly)


## 1.6 Run manual update for Thesaurus

Will update and then index the main thesaurus: `<projectpath>/data/tagfinder_thesaurus.rdf`
Should be done once in a while if you deployed on a free heroku dyno and therefor didn’t activate the scheduler. Redeploy after update is done (about 20 mins).
If you wan’t to perform maintenance on the update tagfinder_thesaurus.rdf just copy it to `<projectpath>/data/temp/`

Requirements:
-   Local installation

Steps:

1.  Run cmd console with admin rights
2.  Navigate to `<projectpath>`
3.  Run maintenance with command: python updater.py

## 1.7 Run inside docker

As an alternative to a local or heroku installation, you can also run
the entire service inside a docker container:

Requirements:
 - Git clone of this repository

Steps:

1. Build the image. From the root of this repo run:
   ```
   docker build -t osm-tagfinder .
   ```
2. Start a container from that image. Run:
   ```
   docker run -p 5000:5000 osm-tagfinder
   ```
3. After a couple of seconds, the tagfinder is available at
   http://localhost:5000

Alternatively, the following `docker-compose.yml` file achieves the
same:

```
services:
  osh:
    build: .
    ports:
      - "5000:5000"
```
