from abc import ABCMeta, abstractmethod
from .connection import db


class CRUD(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    @db.connection_context()
    def save(self, vo):
        raise NotImplemented


    @abstractmethod
    @db.connection_context()
    def count(self):
        raise NotImplemented

    @abstractmethod
    @db.connection_context()
    def fetch_all(self):
        raise NotImplemented

    @abstractmethod
    @db.connection_context()
    def delete(self, id):
        raise NotImplemented
