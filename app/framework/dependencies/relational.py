from app.application.interfaces.relational import SessionMaker
from app.infrastructure.relational_db.connection import async_session_maker


def get_session_maker() -> SessionMaker:
    return async_session_maker
