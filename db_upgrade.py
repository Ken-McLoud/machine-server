#!flask/bin/python
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI as URI
from config import SQLALCHEMY_MIGRATE_REPO as REPO
api.upgrade(URI,REPO)
v=api.db_version(URI,REPO)
print('Current database version: '+str(v))
