from flask_script import Manager
from app import create_app
from flask_migrate import Migrate, MigrateCommand
from app import db
from app.models import CallLOG

app = create_app()

manager = Manager(app)

migrate = Migrate(app, db)


@manager.command
def init():
    db.drop_all()
    db.create_all()

    calllog = CallLOG()
    db.session.add(calllog)
    db.session.commit()


manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
