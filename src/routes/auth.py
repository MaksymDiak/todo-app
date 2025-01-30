from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from src import db
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    set_access_cookies,
    get_jwt_identity,
)
from datetime import timedelta

from ..models.user import User
from ..models.todo import Todo
from ..models.token import TokenBlacklist
from ..schemas.user import UserBase, UserCreate


auth_blueprint = Blueprint("auth_blueprint", __name__, url_prefix='/auth')


def add_token_to_blacklist(token):
    new_blacklist_entry = TokenBlacklist(token=token)
    db.session.add(new_blacklist_entry)
    db.session.commit()


def is_token_blacklisted(token):
    return TokenBlacklist.query.filter_by(token=token).first() is not None


@auth_blueprint.route("/register", methods=["POST"])
def register():
    try:
        user = UserCreate.model_validate(request.get_json())

        existing_user = User.query.filter((User.username == user.username) | (User.email == user.email)).first()
        if existing_user:
            return jsonify({"error": "User with such username or email already exists"}), 400
            
        new_user = User(
            username=user.username,
            email=user.email,
            password=generate_password_hash(user.password),
            created_at=datetime.now(timezone.utc),
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify(user.model_dump()), 201

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error, please try again"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_blueprint.route("/login", methods=["POST"])
def login():
    requested_user = UserBase.model_validate(request.get_json())

    existing_user = User.query.filter(User.username == requested_user.username).first()

    if existing_user and check_password_hash(existing_user.password, requested_user.password):
        response = jsonify({"msg": "login successful"})
        access_token = create_access_token(identity=requested_user.username)
        set_access_cookies(response, access_token)
        return response

    return jsonify({"msg": "Incorrect username or password"}), 401


@auth_blueprint.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    add_token_to_blacklist(jti)
    return jsonify({"msg": "Logout success"}), 200


@auth_blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=15))

    response = jsonify({"access_token": new_access_token})
    set_access_cookies(response, new_access_token)

    return response
