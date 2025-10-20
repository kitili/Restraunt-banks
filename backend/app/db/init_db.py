from .session import Base, engine
from ..models import models  # noqa: F401  # ensure models are imported for metadata

Base.metadata.create_all(bind=engine)
