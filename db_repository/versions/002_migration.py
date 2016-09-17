from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
data_log = Table('data_log', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('source', String(length=64)),
    Column('datatype', String(length=64)),
    Column('time', DateTime),
    Column('payload', String(length=2048)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['data_log'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['data_log'].drop()
