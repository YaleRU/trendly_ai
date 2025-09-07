from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy import UniqueConstraint, Index

from ..base import Base

# Ассоциативная таблица для связи многие-ко-многим между пользователями и источниками
user_source_association = Table(
    'user_sources',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('source_id', Integer, ForeignKey('sources.id', ondelete='CASCADE'), primary_key=True),
    UniqueConstraint('user_id', 'source_id', name="uq_user_sources_association"),
    Index('idx_source_user_id_association', 'user_id'),
)
