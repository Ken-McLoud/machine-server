from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
cell_info = Table('cell_info', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=256)),
    Column('shifts', PickleType),
)

machines = Table('machines', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=256)),
    Column('ident', String(length=256)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cell_info'].create()
    post_meta.tables['machines'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cell_info'].drop()
    post_meta.tables['machines'].drop()
