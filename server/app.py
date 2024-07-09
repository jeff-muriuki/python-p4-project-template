from flask import Flask, request, jsonify, make_response, session
from flask_restful import Resource, Api
from datetime import datetime
from models import db, User, Project, Task, UserProject
from config import app, bcrypt

@app.route('/')
def index():
    return '<h1>Wozza</h1p>'
# Utility functions
def authenticate(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return make_response(jsonify({"error": "Unauthorized access"}), 401)
        return func(*args, **kwargs)
    return wrapper

# Resources
class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return make_response(jsonify({"message": "No input data provided"}), 400)
            
            new_user = User(
                username=data['username'],
                email=data['email'],
                bio=data.get('bio', '')
            )
            new_user.password=data['password']
            db.session.add(new_user)
            db.session.commit()
            return make_response(jsonify(new_user.to_dict()), 201)
        except Exception as e:
            return make_response(jsonify({"message": str(e)}), 400)
        
class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            session.permanent = True
            return make_response(jsonify({"message": "Login successful"}), 200)
        return make_response(jsonify({"error": "Invalid username or password"}), 401)

class Logout(Resource):
    @authenticate
    def post(self):
        session.pop('user_id', None)
        return make_response(jsonify({"message": "Logout successful"}), 200)

class UserResource(Resource):
    @authenticate
    def get(self):
        users_dict = [user.to_dict() for user in User.query.all()]
        return make_response(users_dict, 200)

class UserResourceById(Resource):
    @authenticate
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return make_response(user.to_dict(), 200)

class UsersResource(Resource):
    def get(self):
        users = User.query.all()
        return make_response(jsonify([user.to_dict() for user in users]), 200)
    
class ProjectResource(Resource):
    @authenticate
    def get(self):
        projects_dict = [project.to_dict() for project in Project.query.all()]
        return make_response(projects_dict, 200)

    @authenticate
    def post(self):
        data = request.get_json()
        new_project = Project(
            name=data['name'],
            description=data['description'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d')
        )
        db.session.add(new_project)
        db.session.commit()
        return make_response(new_project.to_dict(), 201)

    @authenticate
    def put(self, project_id):
        data = request.get_json()
        project = Project.query.get_or_404(project_id)
        project.name = data['name']
        project.description = data['description']
        project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        db.session.commit()
        return make_response(project.to_dict(), 200)

    @authenticate
    def delete(self, project_id):
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return make_response(jsonify({"message": "Project deleted"}), 200)
    
class ProjectResourceById(Resource):
    @authenticate
    def get(self, project_id):
        project = Project.query.get_or_404(project_id)
        return make_response(project.to_dict(), 200)
    

class ProjectsResource(Resource):
    @authenticate
    def get(self):
        projects = Project.query.all()
        return make_response(jsonify([project.to_dict() for project in projects]), 200)

class TaskResource(Resource):
    @authenticate
    def get(self):
        tasks_dict = []
        for task in Task.query.all():
            task_dict = task.to_dict()
            tasks_dict.append(task_dict)
        return make_response(tasks_dict, 200)

    @authenticate
    def post(self):
        data = request.get_json()
        new_task = Task(
            name=data['name'],
            description=data['description'],
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d'),
            project_id=data['project_id']
        )
        db.session.add(new_task)
        db.session.commit()
        return make_response(new_task.to_dict(), 201)

    @authenticate
    def put(self, task_id):
        data = request.get_json()
        task = Task.query.get_or_404(task_id)
        task.name = data['name']
        task.description = data['description']
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        task.project_id = data['project_id']
        db.session.commit()
        return make_response(task.to_dict(), 200)

    @authenticate
    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return make_response(jsonify({"message": "Task deleted"}), 200)

api = Api(app)
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(ProjectResource, '/projects', '/projects/<int:project_id>')
api.add_resource(TaskResource, '/tasks', '/tasks/<int:task_id>')

if __name__ == '__main__':
    app.run(debug=True)
