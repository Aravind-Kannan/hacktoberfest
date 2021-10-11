from flask import Flask, request
from flask_restplus import Api, Resource, fields, reqparse
from werkzeug.contrib.fixers import ProxyFix
from datetime import datetime, date

import sqlite3
# Database name (location - local)
db_loc = 'todo_storage.db'

app = Flask(__name__)
app.config['ERROR_404_HELP'] = False

# Helps to fix bugs in web servers
app.wsgi_app = ProxyFix(app.wsgi_app)

# Documentation purposes -> Swagger UI
api = Api(app, version='1.0', title='TodoMVC API',
          description='A simple TodoMVC API',
          )

ns = api.namespace('todos', description='TODO operations')

# Response and requests model parser
todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'descr': fields.String(required=True, description='The task details'),
    'due_date': fields.String(required=True, description='The deadline of task'),
    'status': fields.String(required=True, description='The current status of task')
})

todo_patch = api.model('Todo for Patch', {
    'status': fields.String(required=True, description='The current status of task')
})


class TodoDAO(object):
    @staticmethod
    def check(status):
        return status in ['NOT STARTED', 'IN PROGRESS', 'FINISHED']

    @staticmethod
    def convert(task):
        task_data = {}
        task_data['id'] = task[0]
        task_data['descr'] = task[1]
        task_data['status'] = task[2]
        task_data['due_date'] = task[3]
        return task_data

    def get_all(self):
        conn = sqlite3.connect(db_loc)
        c = conn.cursor()

        c.execute("SELECT * FROM todo_tasks")
        tasks = c.fetchall()

        output = []
        for task in tasks:
            output.append(TodoDAO.convert(task))

        conn.close()

        print("Server response: Fetched all todo_data")
        return output

    def get(self, id):
        conn = sqlite3.connect(db_loc)
        c = conn.cursor()

        c.execute("SELECT * FROM todo_tasks WHERE id= ? ", (id,))
        task = c.fetchone()

        conn.close()

        if task == None:
            api.abort(404, "Todo {} doesn't exist".format(id))

        task_data = TodoDAO.convert(task)
        print("Server response: Fetched required todo_data")
        return task_data

    def create(self, data):
        params = (str(data['descr']),
                  str(data['due_date']),
                  str(data['status']))

        # Value-Check
        try:
            datetime.strptime(data['due_date'], "%Y-%m-%d")
        except:
            api.abort(
                400, "Error: Please format your 'due_date' : 'YYYY-MM-DD' appropriately.")

        if not TodoDAO.check(data.get('status')):
            api.abort(
                400, "Error: status should be one among 'NOT STARTED' or 'IN PROGRESS' or 'COMPLETE' ")

        # Database Connection
        conn = sqlite3.connect(db_loc)
        c = conn.cursor()

        c.execute(
            "INSERT INTO todo_tasks(descr, due_date, status) VALUES (?, ?, ?)", params)
        c.execute(
            "SELECT * FROM todo_tasks WHERE id = (SELECT MAX(id) FROM todo_tasks)")

        task = c.fetchone()
        task_data = TodoDAO.convert(task)

        conn.commit()
        conn.close()

        print("Server response: Created new todo")
        return task_data

    def update(self, id, data):
        params = (data['descr'], data['due_date'], data['status'], id)

        # Value-Check
        try:
            datetime.strptime(data['due_date'], "%Y-%m-%d")
        except:
            api.abort(
                400, "Error: Please format your 'due_date' : 'YYYY-MM-DD' appropriately.")

        if not TodoDAO.check(data.get('status')):
            api.abort(
                400, "Error: status should be one among 'NOT STARTED' or 'IN PROGRESS' or 'COMPLETE' ")

        # Database Connection
        conn = sqlite3.connect(db_loc)
        c = conn.cursor()

        if data.get('status') != None:
            c.execute(
                "UPDATE todo_tasks SET descr=(?), due_date=(?), status=(?) WHERE id=(?)",  params)

        c.execute("SELECT changes()")
        res = c.fetchone()[0]

        conn.commit()
        conn.close()

        if res == 0:
            api.abort(404, "Todo {} doesn't exist".format(id))
        else:
            print("Server response: Updated new todo")

        return

    def update_status(self, id, data):
        params = (data['status'], id)
        if not TodoDAO.check(data.get('status')):
            api.abort(
                400, "Error: status should be one among 'NOT STARTED' or 'IN PROGRESS' or 'COMPLETE' ")

        conn = sqlite3.connect(db_loc)
        c = conn.cursor()

        c.execute("UPDATE todo_tasks SET status = ? WHERE id = ?", params)
        c.execute("SELECT changes()")
        res = c.fetchone()[0]

        conn.commit()
        conn.close()

        if res == 0:
            api.abort(404, "Todo {} doesn't exist".format(id))
        else:
            print("Server response: Updated new todo")

        return

    def delete(self, id):
        conn = sqlite3.connect(db_loc)

        c = conn.cursor()

        c.execute("DELETE FROM todo_tasks WHERE id = ?", (id,))
        c.execute("SELECT changes()")

        res = c.fetchone()[0]

        conn.commit()
        conn.close()

        if res == 0:
            api.abort(404, "Todo {} doesn't exist".format(id))
        else:
            print("Server response: Deleted a todo")

        return


DAO = TodoDAO()

# todos ENDPOINT ------------------------------------------


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.get_all(), 200

    @ns.doc('create_todo')
    @ns.expect(todo, validate=True)
    @ns.marshal_with(todo, code=201)
    @ns.response(400, 'Bad Request: Payload')
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id), 200

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo, validate=True)
    @ns.marshal_with(todo)
    @ns.response(204, 'Todo updated')
    @ns.response(400, 'Bad Request: Payload')
    def put(self, id):
        '''Update a task given its identifier'''
        DAO.update(id, api.payload)
        return '', 204

    @ns.expect(todo_patch, validate=True)
    @ns.response(204, 'Todo status changed')
    @ns.response(400, 'Bad Request: Payload')
    def patch(self, id):
        '''Update status of a task'''
        DAO.update_status(id, api.payload)
        return '', 204


# due ENDPOINT ------------------------------------------


ns_due = api.namespace('due', description='TODO querying')

# Query parameters
due_params = reqparse.RequestParser()
due_params.add_argument('due_date', type=str, required=True)


@ns_due.route('')
@ns_due.response(200, 'Success')
@ns_due.response(400, 'Bad request')
@ns_due.response(404, 'Todo not found')
class Due(Resource):
    @ns_due.expect(due_params, validate='True')
    @ns_due.doc('get_due')
    def get(self):
        '''Fetches a list of tasks which are due to be finished on that specified date'''
        compareDate = request.args.get('due_date')  # query params
        try:
            datetime.strptime(compareDate, "%Y-%m-%d")
        except:
            api.abort(
                400, "Error: - Query parameter - Bad Date Formatting (Modify to 'due_date=YYYY-MM-DD')")

        conn = sqlite3.connect(db_loc)

        c = conn.cursor()
        c.execute("SELECT * FROM todo_tasks WHERE status!=(?) AND due_date=(?)",
                  ("FINISHED", compareDate))
        tasks = c.fetchall()

        output = []

        for task in tasks:
            task_data = TodoDAO.convert(task)
            output.append(task_data)

        if len(output) == 0:
            api.abort(404, f"No due todos on {compareDate}")

        print("Server response: Fetched required todo_data")
        conn.close()

        return output, 200

# overdue ENDPOINT ------------------------------------------


ns_overdue = api.namespace('overdue', description='Overdue TODO tasks')


@ns_overdue.route('')
class Overdue(Resource):
    @ns_overdue.doc('get_overdue')
    def get(self):
        ''' gets all tasks which are past their due date, as of today '''
        today = date.today()
        cur_date = today.strftime('%Y-%m-%d')
        print(cur_date, type(cur_date))

        conn = sqlite3.connect(db_loc)
        c = conn.cursor()

        c.execute("SELECT * FROM todo_tasks WHERE date(due_date) < ? AND status != ?",
                  (cur_date, "FINISHED"))
        tasks = c.fetchall()

        output = []
        for task in tasks:
            output.append(TodoDAO.convert(task))

        if len(output) == 0:
            output = {"message": "No overdue todos"}

        conn.commit()
        conn.close()

        return output, 200

# finished ENDPOINT ------------------------------------------


ns_finished = api.namespace('finished', description="Completed TODO tasks")


@ns_finished.route('')
class Finished(Resource):
    @ns_finished.doc('get_finished')
    def get(self):
        '''gets all tasks which are finished'''

        conn = sqlite3.connect(db_loc)
        c = conn.cursor()

        c.execute("SELECT * FROM todo_tasks WHERE status = ?", ("FINISHED",))
        tasks = c.fetchall()

        output = []
        for task in tasks:
            output.append(TodoDAO.convert(task))

        if len(output) == 0:
            output = {"message": "No finished todos"}

        conn.commit()
        conn.close()

        return output, 200


if __name__ == '__main__':
    app.run(debug=True)
