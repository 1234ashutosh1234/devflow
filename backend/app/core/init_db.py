from app.core.database import Base, engine
from app.models import User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)