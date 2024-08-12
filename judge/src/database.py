from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dp_solutions_architecture_utils.logger import LoggerUtil


# Instantiate logger
logger = LoggerUtil(__name__)


sql_db_filepath = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "db", "sql_app.db"))
logger.info(sql_db_filepath)
SQLALCHEMY_DATABASE_URL = f'sqlite:///{sql_db_filepath}'
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
