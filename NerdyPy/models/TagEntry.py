# -*- coding: utf-8 -*-
""" tag entry database model """

from sqlalchemy import Integer, Column, ForeignKey, LargeBinary, String, Index
from sqlalchemy.orm import relationship

from utils import database as db


class TagEntry(db.BASE):
    """Database Entity Model for tag entries"""

    __tablename__ = "TagEntry"
    __table_args__ = (Index("TagEntry_TagId", "TagId"),)

    Id = Column(Integer, primary_key=True)
    TagId = Column(Integer, ForeignKey("Tag.Id"))
    TextContent = Column(String(255))
    ByteContent = Column(LargeBinary(16777215))

    tag = relationship("Tag", back_populates="entries")
