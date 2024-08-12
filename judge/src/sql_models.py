from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    created = Column(DateTime, default=datetime.now(tz=timezone.utc), index=True)

    cookies = relationship("Cookie", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")


class Cookie(Base):
    __tablename__ = "cookies"

    id = Column(Integer, primary_key=True, index=True)
    cookie = Column(String, unique=True, index=True, nullable=False)
    cookie_source = Column(String, nullable=False)
    username = Column(String, ForeignKey("users.username"))
    created = Column(DateTime, default=datetime.now(tz=timezone.utc), index=True)

    user = relationship("User", back_populates="cookies")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    chunk_id = Column(String, nullable=False)
    search_type = Column(String, nullable=False)
    keyword_search_field = Column(String, nullable=True)
    keyword_search_type = Column(String, nullable=True)
    asset_type = Column(String, nullable=False)
    k = Column(Integer, nullable=False)
    results_idx = Column(Integer, nullable=False)
    n_results = Column(Integer, nullable=False)

    # 1==upvote (relevant), 0==downvote (irrelevant)
    vote_value = Column(Integer, nullable=False)

    username = Column(String, ForeignKey("users.username"))
    created = Column(DateTime, default=datetime.now(tz=timezone.utc), index=True)

    user = relationship("User", back_populates="feedback")
