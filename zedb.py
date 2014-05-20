import os

from mongoengine import *

class User(Document):
    jid = StringField(required=True, primary_key=True)


class Challange(Document):
    c_id = SequenceField(primary_key=True)
    description = StringField(required=True, unique=True)
    user_jid = ReferenceField(User, required=True)

class OperationsDB(object):

    @staticmethod
    def connect():
        bd_name = os.environ.get("BOT_DB_NAME", "")
        connect(bd_name)

    @staticmethod
    def insert(user_jid, challange):
        if not Challange.objects(description=challange):
            User(jid=user_jid).save()
            owner = User.objects.get(jid=user_jid)
            Challange(description=challange, user_jid=owner).save()
        else:
            pass #TODO: Description duplicated trigger a exception, return a error message?

    @staticmethod
    def get_challanges(user=""):
        challanges,list_cha = Challange(),[]
        if user:
            challanges = Challange.objects(user_jid=user).only('description')
        else:
            challanges = Challange.objects.only('description')
        for challange in challanges:
            list_cha.append(challange.description.encode('UTF-8'))
        return list_cha
