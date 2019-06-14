# -*- coding: utf-8 -*-
"""Concept dictionary models."""
import datetime as dt
import uuid
import jwt
from app.database import Column, Model, SurrogatePK, db, reference_col, relationship
from app.extensions import bcrypt


class Concept_class(SurrogatePK, Model):
    """ defines how concept will be represented """

    __tablename__ = 'concept_class'
    name = Column(db.String(255), unique=True, nullable=False)
    description = Column(db.String(255), unique=True, nullable=False)
    creator = Column(db.String(255), nullable=False)
    date_created = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    retired = Column(db.Boolean, nullable=True)
    retired_by = Column(db.String(255), nullable=True)
    date_retired = Column(db.DateTime, nullable=True)
    retire_reason = Column(db.String(255), nullable=True)
    uuid = Column(db.String(255), unique=True, nullable=False, default=str(uuid.uuid4()))


    def __init__(self, name, description, creator, uuid, **kwargs):
        """ Create instance """
        db.Model.__init__(self, name=name, description=description, creator=creator, uuid = uuid, **kwargs)
         