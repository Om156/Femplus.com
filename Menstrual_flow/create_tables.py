from app.database import Base, engine
from app.storage.model import FlowReading, User, Feedback

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
