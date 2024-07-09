
from faker import Faker
from random import randint
from app import app
from flask import Flask
from models import User, Project, Task, UserProject, db




fake = Faker()

def seed_users(num_users=10):
    for _ in range(num_users):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            password_hash=fake.password(length=12),
            bio=fake.text(max_nb_chars=200)
        )
        db.session.add(user)

    db.session.commit()

def seed_projects(num_projects=5):
    for _ in range(num_projects):
        project = Project(
            name=fake.company(),
            description=fake.text(max_nb_chars=500),
            start_date=fake.date_between(start_date='-1y', end_date='today'),
            end_date=fake.date_between(start_date='today', end_date='+1y')
        )
        db.session.add(project)

    db.session.commit()

def seed_tasks(num_tasks=20):
    projects = Project.query.all()
    for _ in range(num_tasks):
        task = Task(
            name=fake.bs(),
            description=fake.text(max_nb_chars=300),
            due_date=fake.date_between(start_date='today', end_date='+6M'),
            project_id=randint(1, len(projects))
        )
        db.session.add(task)

    db.session.commit()

def seed_user_projects():
    users = User.query.all()
    projects = Project.query.all()
    roles = ['Manager', 'Developer', 'Designer', 'Tester']

    for user in users:
        num_projects = randint(1, 3)  # Assign user to 1-3 projects randomly
        selected_projects = fake.random_elements(elements=projects, length=num_projects, unique=True)
        
        for project in selected_projects:
            user_project = UserProject(
                user_id=user.id,
                project_id=project.id,
                role=fake.random_element(elements=roles)
            )
            db.session.add(user_project)

    db.session.commit()

def main():
    with app.app_context():
        db.drop_all()
        db.create_all()

        seed_users()
        seed_projects()
        seed_tasks()
        seed_user_projects()

        print("Database seeded successfully!")

if __name__ == '__main__':
    main()
