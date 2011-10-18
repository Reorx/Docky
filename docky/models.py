#coding=utf8

import logging

from tornado.options import options

from mongoengine import *

__all__ = ['User', 'Team', 'Project', 'Section', 'Resource']

connect(options.mongodb.name,
        host = options.mongodb.host,
        port = options.mongodb.port)

class User(Document):
    email = StringField(max_length=75, required=True)
    password = StringField(max_length=40, required=True)

    status = StringField(max_length=16, default='active')

    nickname = StringField(max_length=32)
    bio = StringField(max_length=256)

    meta = {
        'indexes': ['email', ]
    }

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

class Team(Document):
    pass

class Resource(Document):
    url = StringField()
    method = StringField()
    description = StringField()
    authentication_required = BooleanField()
    paramenters = ListField(DictField())
    example = DictField()
    update_log = ListField(DictField())

class Section(Document):
    name = StringField()
    description = StringField()
    resources = ListField(ReferenceField(Resource))

class Project(Document):
    name = StringField()
    description = StringField()
    sections = ListField(ReferenceField(Section))
