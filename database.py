from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os


db_file = "sqlite:///%s/data/hybridius.sqlite" % (os.path.dirname(__file__))

engine = create_engine(db_file, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
	from database_models import Shortcode
	Base.metadata.create_all(bind=engine)
