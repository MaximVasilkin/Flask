from flask import Flask, jsonify, request
from flask.views import MethodView
from pydantic import ValidationError
from app.app_errors import HttpError, IntegrityError
from app.response_statuses import Status
from models import User, Advertisment
from validators import PostAdv, PatchAdv, PostUser, PatchUser
from work_with_db import db
from hashlib import md5


# settings

app = Flask('my_app')
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False


# error handlers

@app.errorhandler(HttpError)
def http_error_handler(error):
    return __error_message(error.message, error.status_code)


@app.errorhandler(IntegrityError)
def integrity_error_handler(error):
    return __error_message('Error of existance', 409)


# work with objects, validate, authenticate

def validate(json, validate_model_class):
    try:
        model = validate_model_class(**json)
        validated_json = model.dict(exclude_none=True)
        if not validated_json:
            raise HttpError(400, 'Validation error')
        return validated_json
    except ValidationError as error:
        raise HttpError(400, error.errors())


def __error_message(message, status_code):
    response = jsonify({'message': message} | Status.error)
    response.status_code = status_code
    return response


def get_object_and_check(model, item_id, object_name, to_dict=True):
    object = db.get_object(model, item_id, to_dict=to_dict)
    if object is None:
        raise HttpError(404, f'{object_name} not found')
    return object


def get_hashed_password(password):
    password = password.encode()
    hashed_password = md5(password).hexdigest()
    return hashed_password


def authenticate(request):
    email = request.headers.get('email')
    password = request.headers.get('password')
    if not email or not password:
        raise HttpError(410, 'Empty email or password')
    hashed_password = get_hashed_password(password)
    user = db.check_log_in(email, hashed_password)
    if not user:
        raise HttpError(410, 'Invalid authenticate')
    return user


def get_user_checked_request(request, validate_model):
    json = request.json
    validated_json = validate(json, validate_model)
    if 'password' in validated_json:
        hashed_password = get_hashed_password(validated_json['password'])
        validated_json['password'] = hashed_password
    return validated_json


def get_adv_checked_request(request, validate_model):
    user = authenticate(request)
    json = request.json
    validated_json = validate(json, validate_model)
    return user, validated_json


def check_adv_owner(user_id, adv_id):
    if not db.check_rights_on_adv(user_id, adv_id):
        raise HttpError(404, 'Can not manipulate with this advertisment')


# views

def main_view():
    return jsonify({'message': 'hi!'})


class UserView(MethodView):
    def get(self, user_id):
        user = get_object_and_check(User, user_id, 'user')
        return jsonify(user | Status.ok)

    def post(self):
        validated_json = get_user_checked_request(request, PostUser)
        db.create_object(User, **validated_json)
        del validated_json['password']
        return jsonify(validated_json | Status.ok)

    def patch(self, user_id):
        validated_json = get_user_checked_request(request, PatchUser)
        user = get_object_and_check(User, user_id, 'user')
        db.update_object(User, user_id, **validated_json)
        if 'password' in validated_json:
            del validated_json['password']
        return jsonify(validated_json | Status.ok)

    def delete(self, user_id):
        user = get_object_and_check(User, user_id, 'user')
        db.delete_object(User, user_id)
        return jsonify(user | Status.ok)


class AdvView(MethodView):
    def get(self, adv_id):
        adv = get_object_and_check(Advertisment, adv_id, 'advertisment')
        return jsonify(adv | Status.ok)

    def post(self):
        user, validated_json = get_adv_checked_request(request, PostAdv)
        validated_json['owner_id'] = user.id
        db.create_object(Advertisment, **validated_json)
        return jsonify(validated_json | Status.ok)

    def patch(self, adv_id):
        user, validated_json = get_adv_checked_request(request, PatchAdv)
        check_adv_owner(user.id, adv_id)
        db.update_object(Advertisment, adv_id, **validated_json)
        return jsonify(validated_json | Status.ok)

    def delete(self, adv_id):
        user = authenticate(request)
        check_adv_owner(user.id, adv_id)
        db.delete_object(Advertisment, adv_id)
        message = {'advertisment': adv_id}
        return jsonify(message | Status.ok)


# urls

app.add_url_rule('/',
                 view_func=main_view,
                 methods=['GET'])

app.add_url_rule('/user',
                 view_func=UserView.as_view('user_add'),
                 methods=['POST'])

app.add_url_rule('/user/<int:user_id>',
                 view_func=UserView.as_view('user_existed'),
                 methods=['GET', 'PATCH', 'DELETE'])

app.add_url_rule('/advertisment',
                 view_func=AdvView.as_view('advertisment_add'),
                 methods=['POST'])

app.add_url_rule('/advertisment/<int:adv_id>',
                 view_func=AdvView.as_view('advertisment_existed'),
                 methods=['GET', 'PATCH', 'DELETE'])

# Start project

if __name__ == '__main__':
    app.run()
