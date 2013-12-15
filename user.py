from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def init_sqlalchemy():
    db_uri = "sqlite:///" + "profile.db"
    engine = create_engine(db_uri)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    base = declarative_base()
    base.query = db_session.query_property()
    return engine, base, db_session

engine, Base, db_session = init_sqlalchemy()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))
    groups_string = Column(String(200))

    def __init__(self, name, email, openid, groups_string):
        self.name = name
        self.email = email
        self.openid = openid
        self.groups_string = groups_string
    def get_groups(self):
        return self.groups_string.split()

class UserList():
    def __init__(self):
        global db_session
        self.db_session = db_session
    def get_by_openid(self, openid):
        return User.query.filter_by(openid=openid).first()
    def get_by_id(self, id):
        return User.query.filter_by(id=id).first()
    def get_all(self):
        return User.query.all()
    def init_db(self):
        global engine
        global Base
        Base.metadata.create_all(bind=engine)
    def close(self):
        self.db_session.remove()
    def commit(self):
        self.db_session.commit()
    def add(self, user):
        self.db_session.add(user)
        self.commit()
    def delete(self, user):
        self.db_session.delete(user)
        self.commit()
    def db_created(self):
        try:
            User.query.filter_by(openid="foobar").first()
            return True
        except:
            return False
    def total(self):
        return len(User.query.all())
