from database import Base, engine
from models import User, ChatMessage, Conversation  # import all models

# Drop all tables
Base.metadata.drop_all(bind=engine)

# Recreate all tables
Base.metadata.create_all(bind=engine)

print("✅ Database reset complete.")