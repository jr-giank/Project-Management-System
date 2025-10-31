
import pytest

from config import TestConfig
from app import app_init
from app.extensions import db

@pytest.fixture(scope='session')
def app():
    app = app_init(config_object=TestConfig)

    with app.app_context():
        from app import models
        db.create_all()
        
    yield app

    with app.app_context():
        db.drop_all()
    
@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Provides a clean, transactional session for each test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        db.session.bind = connection
        db.session.begin_nested()
        yield db.session

        try:
            db.session.rollback()
        except Exception:
            pass
        db.session.bind = None

        try:
            transaction.rollback()
        except Exception:
            pass
        connection.close()