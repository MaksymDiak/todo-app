from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from src import db

from ..schemas.todo import TodoBase, TodoResponse, TodoUpdate

from ..models.todo import Todo
from ..models.user import User


todo_blueprint = Blueprint("todo_blueprint", __name__, url_prefix="/todos")


def get_current_user():
    username = get_jwt_identity()
    existing_user = User.query.filter(User.username == username).first()
    return existing_user


def get_current_user_id():
    return get_current_user().id


@todo_blueprint.route("/")
@jwt_required()
def get_my_todos():
    user = get_current_user()
    if user:
        todos = Todo.query.filter(Todo.owner_id == user.id).all()
        return jsonify([todo.to_dict() for todo in todos])
    return {"msg": "No user"}


@todo_blueprint.route("/<int:todo_id>")
@jwt_required()
def get_todo(todo_id: int):
    existing_todo = Todo.query.filter(Todo.id == todo_id).first()
    if existing_todo and existing_todo.owner_id == get_current_user_id():
        return jsonify(existing_todo.to_dict())

    return jsonify({"msg": "Can`t find todo with such id or it`s not your Todo!"})


@todo_blueprint.route("/add", methods=["POST"])
@jwt_required()
def add_todo():
    user_id = get_current_user_id()
    todo = TodoBase.model_validate(request.get_json())
    new_todo = Todo(title=todo.title, complete=todo.complete, owner_id=user_id)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({"msg": "Todo was created"}), 201


@todo_blueprint.route("/delete/<int:todo_id>", methods=["DELETE"])
@jwt_required()
def delete_todo(todo_id: int):
    existing_todo = Todo.query.filter(Todo.id == todo_id).first()
    if existing_todo and existing_todo.owner_id == get_current_user_id():
        db.session.delete(existing_todo)
        db.session.commit()
        return jsonify({"msg": "Todo was deleted!"})

    return jsonify({"msg": "Can`t delete this Todo!"}), 403


@todo_blueprint.route("/update/<int:todo_id>", methods=["PUT"])
@jwt_required()
def update_todo(todo_id: int):
    existing_todo = Todo.query.filter(Todo.id == todo_id).first()
    if existing_todo and existing_todo.owner_id == get_current_user_id():
        todo_data = TodoUpdate.model_validate(request.get_json())

        existing_todo.title = todo_data.title
        existing_todo.complete = todo_data.complete

        db.session.commit()
        return jsonify({"msg": "Todo was updated!"})

    return jsonify({"msg": "Can`t update this Todo!"}), 403
