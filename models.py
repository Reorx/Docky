#coding=utf8

import logging

from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy import Integer, String, Text, Boolean, Date, DateTime, Float
from sqlalchemy.orm import relationship

import config
from core.databases import SQLAlchemy, MongoDB

db = SQLAlchemy(config.db_config)
mongodb = MongoDB(config.mongodb_config)

# SQL - Relation Model
# user --  the center of all services
class User(db.Model):
    email = Column(String(75), unique=True, index=True)
    password = Column(String(40))

    status = Column(String(16), default='active')

    nickname = Column(String(32), nullable=True)
    bio = Column(String(256), nullable=True)

    def __unicode__(self):
        return self.email

    @staticmethod
    def create_password(raw):
        from utils.hashs import RandomString, Md5
        pw_salt = RandomString(length=7)
        pw_hash = Md5(pw_salt + raw)
        return '%s$%s' % (pw_salt, pw_hash)

    def set_password(self, raw):
        self.password = self.create_password(raw)
    
    def check_password(self, raw):
        from utils.hashs import Md5
        pw_salt, pw_hash = self.password.split('$')
        return pw_hash == Md5(pw_salt + raw)

"""Structure
Doc
    document, specially api-document, gathering of doc_entrys, guider of a product
DocEntry
    doc_entry, containing the details of an api, including it's required-parameters, ease-paramenters, response-data and so on
"""
class Doc(db.Model):
    name = Column(String(32), unique=True, index=True)
    description = Column(String(128))

    def set_resource(self, name):
        pass

    def get_resource(self, name):
        pass

    def get_resources(self):
        pass

    def set_entry(self, data):
        pass

    def get_entry(self, name):
        pass

    def get_entries(self):
        pass

DocResource = mongodb.get_collection('doc_resource')

DocEntry = mongodb.get_collection('doc_entry')
