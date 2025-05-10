from sqlalchemy import Column, Integer, String, ForeignKey # Removed DateTime and func
from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func # Removed func as created_at is removed
from .user import db # Assuming db is initialized in user.py or a shared models base

class ClonedVoice(db.Model):
    # Removed __tablename__ = "cloned_voices" as it was part of a later fix, reverting to implicit naming
    id = Column(Integer, primary_key=True, autoincrement=True)
    voice_id_elevenlabs = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False) # Reverted to user.id based on earlier working state
    # created_at = Column(DateTime(timezone=True), server_default=func.now()) # This line is now removed

    user = relationship("User", back_populates="voices")

    def __repr__(self):
        return f"<ClonedVoice {self.name} (ID: {self.voice_id_elevenlabs})>"

