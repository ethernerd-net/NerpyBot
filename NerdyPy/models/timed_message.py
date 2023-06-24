# -*- coding: utf-8 -*-
""" timed message database model """

from datetime import timedelta

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Index, asc

from utils import database as db


class TimedMessage(db.BASE):
    """database entity model for tags"""

    __tablename__ = "TimedMessage"
    __table_args__ = (
        Index("TimedMessage_GuildId", "GuildId"),
        Index("TimedMessage_Id_GuildId", "Id", "GuildId", unique=True),
    )

    Id = Column(Integer, primary_key=True)
    GuildId = Column(BigInteger)
    ChannelId = Column(BigInteger)
    CreateDate = Column(DateTime)
    Author = Column(String(30))
    Repeat = Column(Integer)
    Minutes = Column(Integer)
    LastSend = Column(DateTime)
    Message = Column(String(30))
    Count = Column(Integer)

    @classmethod
    def get(cls, timed_id, guild_id, session):
        """returns a tag with given name for given guild | session needed!"""
        return (
            session.query(TimedMessage)
            .filter(TimedMessage.Id == timed_id)
            .filter(TimedMessage.GuildId == guild_id)
            .first()
        )

    @classmethod
    def get_all_from_guild(cls, guild_id: int, session):
        """returns all tags for given guild | session needed!"""
        return session.query(TimedMessage).filter(TimedMessage.GuildId == guild_id).order_by(asc("Id")).all()

    @classmethod
    def delete(cls, timed_id, guild_id: int, session):
        """deletes a tag with given name for given guild"""
        session.delete(TimedMessage.get(timed_id, guild_id, session))

    def __str__(self):
        msg = f"==== {self.Id} ====\n\n"
        msg += f"Author: {self.Author}\n"
        msg += f"Created: {self.CreateDate.strftime('%Y-%m-%d %H:%M')}\n"
        msg += f"Next Message: {(self.LastSend + timedelta(minutes=self.Minutes.float())).strftime('%Y-%m-%d %H:%M')}\n"
        msg += f"Message: {self.Message}\n"
        msg += f"Hits: {self.Count}\n"
        return msg
