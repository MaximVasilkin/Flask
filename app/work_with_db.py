from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Подправить под контейнер
from app.models import Advertisment, User

DSN = 'postgresql://postgres:pstpwd@localhost:5432/flask_db'


class DataBase:

    def __init__(self, DSN):
        self.DSN = DSN
        self.engine = create_engine(self.DSN)
        self.Session = sessionmaker(bind=self.engine)

    def __get_object_request(self, model, item_id, session):
        request = session.query(model).filter(model.id == item_id)
        return request

    def create_object(self, model, **kwargs):
        with self.Session() as session:
            new_object = model(**kwargs)
            session.add(new_object)
            session.commit()

    def get_object(self, model, item_id, to_dict=False):
        with self.Session() as session:
            object_ = self.__get_object_request(model, item_id, session).first()
            if object_ and to_dict:
                return object_.to_dict()
            return object_

    def update_object(self, model, item_id, **kwargs):
        with self.Session() as session:
            self.__get_object_request(model, item_id, session).update(kwargs)
            session.commit()

    def delete_object(self, model, item_id):
        with self.Session() as session:
            session.query(model).filter(model.id == item_id).delete()
            session.commit()


db = DataBase(DSN)

# engine = create_engine(DSN)
# Session = sessionmaker(bind=engine)
# with Session() as session:
#     request = session.query(Advertisment).filter(Advertisment.id == 7).first()
#     print(request.to_dict())
from app_errors import IntegrityError

try:
    db.create_object(Advertisment,
                     owner_id=10,
                     title='hhhhhhhhhhhhhh',
                     description='dddddddddd')
except IntegrityError:
    print('ыыыы')


