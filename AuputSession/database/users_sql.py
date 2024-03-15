from env import DATABASE_URL

from sqlalchemy import Column, BigInteger

if DATABASE_URL !="":
    from AuputSession.database import BASE, SESSION
else:
    BASE = object


class Users(BASE):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    user_id = Column(BigInteger, primary_key=True)

    def __init__(self, user_id, channels=None):
        if DATABASE_URL == "":
            return
        self.user_id = user_id
        self.channels = channels


if DATABASE_URL !="":
    Users.__table__.create(checkfirst=True)


async def num_users():
    if DATABASE_URL !="":
        try:
            return SESSION.query(Users).count()
        finally:
            SESSION.close()
