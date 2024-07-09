from sqlalchemy_serializer import SerializerMixin
#from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from config import db, bcrypt

# Models go here!
class UserProject(db.Model, SerializerMixin):
    __tablename__ = 'user_project_association'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    role = db.Column(db.String(50)) 
    
class User(db.Model, SerializerMixin):
    __tablename__= 'users'

    id= db.Column(db.Integer, primary_key=True) 

    #lets remove the constraint unique=True since different users may share the same name
    # and in addition we have email set to unique.
    username= db.Column(db.String, nullable=False)
    email= db.Column(db.String, unique=True, nullable=False)
    password_hash= db.Column(db.String, unique=True, nullable=False)
    bio= db.Column(db.String, nullable=False)


    @hybrid_property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash= bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('username must be not empty')
        return username

class Project(db.Model, SerializerMixin):
    __tablename__= 'projects'

    id= db.Column(db.Integer, primary_key=True) 
    name= db.Column(db.String, nullable=False)
    description= db.Column(db.String)
    start_date= db.Column(db.Date, nullable=False)
    end_date= db.Column(db.Date, nullable=False)

    tasks= db.relationship('Task', backref='project', lazy=True)

    serialize_rules = ('-tasks',)


class Task(db.Model, SerializerMixin):
    __tablename__= 'tasks'

    id= db.Column(db.Integer, primary_key=True) 
    name= db.Column(db.String, nullable=False)
    description= db.Column(db.String, nullable=False)
    due_date= db.Column(db.Date, nullable=False)
    project_id= db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    serialize_rules = ('-project',)

    



    


