# Toolbox
A web application to provide a toolbox of automation solutions.

## Development Requirements
A virtual environment for python is **strongly** recommended!

### Ubuntu Packages
The following command (and packages) were used for installing on Ubuntu 16.04 LTS. For newer distributions slight changes may be necessary.
```
apt-get install git python3 python3-dev python3-virtualenv nodejs-legacy npm postgresql-9.5 postgresql-server-dev-9.5 redis-server redis-tools libsasl2-dev libldap2-dev libssl-dev libxml2-dev libxslt1-dev screen
```

### Shell Environment
Using some custom variables will go a long way to making development of steward easier. Put the following in your ~/.bashrc file.
```
# Development Paths
export PATH=$PATH:./node_modules/.bin
# Load screen files from Projects
SCREEN_FILES=`ls -a ~/Projects/*/.screenrc-*`
for FILE in $SCREEN_FILES;
do
        NAME=`echo $FILE | rev | cut -d- -f1 | rev`;
        alias $NAME="screen -c $FILE"
done
```
You should then login again or type source ~/.bashrc in all of your current terminals before the changes will take place. Once this has taken place a custom screen alias has been made such that you can run 'steward' and a screen will open with all your development processes running.

It would also be benefitial to setup your screenrc (~/.screenrc) file so that you can easily see what windows are open and can easily switch between them. Look at the following gist for that file: https://git.ops.cspirevoice.com/snippets/2


### Virtual Environment
```
virtualenv -p python3 venv
source venv/bin/activate
```

### NPM Packages
```
npm install
```

### Local Docker Setup
TBD?

### Python Packages
```
pip install -r requirements.txt
```

### PostgreSQL
Create a database.
Grant the user permissions to the database.

### Execute Migrations
python manage.py migrate
