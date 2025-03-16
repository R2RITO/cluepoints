from os import environ

from sqlmodel import Session, create_engine

DB_USERNAME = environ.get("DB_USERNAME", "arturo")
DB_PASSWORD = environ.get("DB_PASSWORD", "arturo")
DB_HOST = environ.get("DB_HOST", "localhost")

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/cluepoints"

connect_args = {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def get_db():
    with Session(engine) as session:
        yield session
