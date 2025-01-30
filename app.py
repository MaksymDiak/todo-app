from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from src import create_app, db
from src.routes.auth import auth_blueprint
from src.routes.todo import todo_blueprint


app = create_app()


app.register_blueprint(auth_blueprint)
app.register_blueprint(todo_blueprint)

jwt = JWTManager(app)
migrate = Migrate(app, db)


if __name__ == "__main__":
    app.run(debug=True)
