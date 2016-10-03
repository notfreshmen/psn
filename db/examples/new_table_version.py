from sqlalchemy import *
from migrate import *


meta = MetaData()
# Column('XXXX', String(120)),
XXXX = Table(
    'XXXX', meta,
    Column('id', Integer, primary_key=True),
    Column('XXXX', String(80), unique=False),
    Column('XXXX', String(128), unique=False),
    Column('date_created', DateTime, unique=False),
    Column('date_modified', DateTime, unique=False)
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    XXXX.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    XXXX.drop()
