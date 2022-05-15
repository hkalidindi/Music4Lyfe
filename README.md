## Setup

For development setup, create a virtual environment and install all dependencies:

```bash
cd path/to/project/folder

# create virtual environment
python -m venv venv

# activate virtual environment
source venv/bin/activate # if on unix
.\venv\Scripts\activate  # if on windows

# install dependencies
pip install -r requirements.txt
```

## Interacting with the database

For our backend, we use an Amazon RDS instance running MySQL. In order to connect to the MySQL server instance, make sure that the fields under ``database`` in the ``mysql-config.toml`` file are all filled out and correct according to the contents of ``AWS-credentials.txt`` (in the shared Google Drive).

To connect to the database with ``mysql-server`` use
```bash
mysql -u <user> -h <host> -p
```
where ``<user>``, ``<host>``, and the password you will be prompted for are again from ``AWS-credentials.txt``. 

## Starting the Flask app

From within the ``src`` directory, run ``views.py`` with the configured virtual environment.
