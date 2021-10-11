# Simple Todo API

API created to simulate a simple todo task manager using Flask microservice framework. `api.py` contains the REpresentational State Transfer API implementing a simple TODO app using the Flask framework.

- Package manager: `pipenv`
- Documentation: Provided by Swagger UI
- Database used: Sqlite3

> Note: `flask_restplus` is unmaintained and moved to `flask-restx`

## Setup environment

- To bash into <em>pipenv</em>: `pipenv shell`
- To setup required libraries using <em>pipenv</em>: `pip install -r requirements.txt`

## Create database

- Run the python script inside virtual environment created using <em>pipenv</em>: `python init.py`
- This creates a `todo_storage.db` file used as simple database storage with a `todo_tasks` table

# Running the API

- Run the API using `python api.py` for simple local deployment inside virtual environment created using <em>pipenv</em>
- To exit out of <em>pipenv</em>: `exit`
