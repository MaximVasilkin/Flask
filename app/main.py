from flask import Flask, jsonify, request
from flask.views import MethodView
from pydantic import ValidationError
from app.app_errors import HttpError, IntegrityError
from models import User, Advertisment
from validators import PostAdv, PatchAdv, PostUser, PatchUser
from work_with_db import db


class Status:
    __message = 'status'
    ok = {__message: 'ok'}
    error = {__message: 'error'}


app = Flask('my_app')
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False


def validate(json, validate_model_class):
    try:
        model = validate_model_class(**json)
        return model.dict(exclude_none=True)
    except ValidationError as error:
        raise HttpError(400, error.errors())


def __error_message(message, status_code):
    response = jsonify({'message': message} | Status.error)
    response.status_code = status_code
    return response


@app.errorhandler(HttpError)
def http_error_handler(error):
    return __error_message(error.message, error.status_code)


@app.errorhandler(IntegrityError)
def integrity_error_handler(error):
    return __error_message('Error of existance', 409)


def get_object_and_check(model, item_id, object_name, to_dict=True):
    object = db.get_object(model, item_id, to_dict=to_dict)
    if object is None:
        raise HttpError(404, f'{object_name} not found')
    return object


def main_view():
    return jsonify({'message': 'hi!'})


class UserView(MethodView):
    def get(self, user_id):
        user = get_object_and_check(User, user_id, 'user')
        return jsonify(user | Status.ok)

    def post(self):
        json = request.json
        validated_json = validate(json, PostUser)
        db.create_object(User, **validated_json)
        return jsonify(validated_json | Status.ok)


    def patch(self, user_id):
        json = request.json
        validated_json = validate(json, PatchUser)
        user = get_object_and_check(User, user_id, 'user')
        db.update_object(User, user_id, **validated_json)
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
        json = request.json
        validated_json = validate(json, PostAdv)
        db.create_object(Advertisment, **validated_json)
        return jsonify(validated_json | Status.ok)

    def patch(self, adv_id):
        json = request.json
        validated_json = validate(json, PatchAdv)
        adv = get_object_and_check(Advertisment, adv_id, 'advertisment')
        db.update_object(Advertisment, adv_id, **validated_json)
        return jsonify(validated_json | Status.ok)

    def delete(self, adv_id):
        adv = get_object_and_check(Advertisment, adv_id, 'advertisment')
        db.delete_object(Advertisment, adv_id)
        return jsonify(adv | Status.ok)


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


if __name__ == '__main__':
    app.run()
