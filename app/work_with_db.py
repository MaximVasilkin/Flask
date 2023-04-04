from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Advertisment, User, Base


DSN = 'postgresql://postgres:pstpwd@localhost:5432/flask_db'
ENGINE = create_engine(DSN)
SESSION = sessionmaker(bind=ENGINE)


class DataBase:

    def __init__(self, DSN):
        self.DSN = DSN
        self.engine = ENGINE
        self.Session = SESSION

    def __get_query_request(self, model, item_id, session):
        request = session.query(model).filter(model.id == item_id)
        return request

    def create_object(self, model, **kwargs):
        with self.Session() as session:
            new_object = model(**kwargs)
            session.add(new_object)
            session.commit()

    def get_object(self, model, item_id, to_dict=False):
        with self.Session() as session:
            object_ = self.__get_query_request(model, item_id, session).first()
            if object_ and to_dict:
                return object_.to_dict()
            return object_

    def update_object(self, model, item_id, **kwargs):
        with self.Session() as session:
            session.query(model).filter(model.id == item_id).update(kwargs)
            session.commit()

    def delete_object(self, model, item_id):
        obj = self.get_object(model, item_id)
        with self.Session() as session:
            session.delete(obj)
            session.commit()

    def check_log_in(self, email, hashed_password):
        with self.Session() as session:
            result = session.query(User).filter(User.email == email,
                                                User.password == hashed_password).first()
            return result

    def check_rights_on_adv(self, user_id, adv_id):
        with self.Session() as session:
            result = session.query(User).join(Advertisment).filter(User.id == user_id,
                                                                   Advertisment.id == adv_id).first()
            return result


if __name__ == '__main__':
    Base.metadata.create_all(ENGINE)
else:
    db = DataBase(DSN)
