
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Group(Base):

    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship("User")

    def __init__(self, chatId):
        pass

    def __repr__(self):
        return "Group: {}".format(name)


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    idGroup = (Integer, ForeignKey("groups.id"))
    name = Column(String)

    def __init__(self):
        pass
