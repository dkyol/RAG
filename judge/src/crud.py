from sqlalchemy.orm import Session
import sql_models as models
import sql_schemas as schemas
from typing import Union

"""
User CRUD
"""


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


"""
Cookie CRUD
"""


def get_cookies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cookie).offset(skip).limit(limit).all()


def create_user_cookie(db: Session, cookie: schemas.CookieCreate, username: str):
    db_cookie = models.Cookie(**cookie.dict(), username=username)
    db.add(db_cookie)
    db.commit()
    db.refresh(db_cookie)
    return db_cookie


def get_cookie(db: Session, cookie: str):
    return db.query(models.Cookie).filter(models.Cookie.cookie == cookie).first()


def update_user_cookie(db: Session, cookie: str, username: str):
    db_cookie = db.query(models.Cookie).filter(models.Cookie.cookie == cookie).first()
    if db_cookie is None:
        return None
    db_cookie.username = username
    db.add(db_cookie)
    db.commit()
    db.refresh(db_cookie)
    return db_cookie


"""
Feedback CRUD
"""


def get_all_feedback(
    db: Session, vote_value: Union[int, None] = None, skip: int = 0, limit: int = 100
):
    if vote_value is not None:
        return (
            db.query(models.Feedback)
            .filter(models.Feedback.vote_value == vote_value)
            .offset(skip)
            .limit(limit)
            .all()
        )
    return db.query(models.Feedback).offset(skip).limit(limit).all()


def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_feedback(db: Session, feedback: schemas.Feedback):
    return (
        db.query(models.Feedback)
        .filter(
            models.Feedback.query == feedback.query,
            models.Feedback.chunk_id == feedback.chunk_id,
            models.Feedback.search_type == feedback.search_type,
            models.Feedback.keyword_search_field == feedback.keyword_search_field,
            models.Feedback.keyword_search_type == feedback.keyword_search_type,
            models.Feedback.asset_type == feedback.asset_type,
            models.Feedback.k == feedback.k,
            models.Feedback.username == feedback.username,
            models.Feedback.vote_value == feedback.vote_value,
        )
        .first()
    )


def delete_feedback(db: Session, feedback: schemas.Feedback):
    db.delete(feedback)
    db.commit()
    return None
