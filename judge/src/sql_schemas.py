from typing import List, Union
from datetime import datetime
from pydantic import BaseModel


"""
Feedback Schema
"""


# base class for both create and read
class FeedbackBase(BaseModel):
    query: str
    chunk_id: str
    search_type: str
    keyword_search_field: Union[str, None] = None
    keyword_search_type: Union[str, None] = None
    asset_type: str
    k: int
    results_idx: int
    n_results: int
    vote_value: int
    username: str


# only create (We won't know about id during creation)
# useful if we need to separate out sensitive info
# (like a password) that we don't want read to have
class FeedbackCreate(FeedbackBase):
    pass


class FeedbackDelete(FeedbackBase):
    pass


# only read
# reason id and created are here is because FeedbackCreate will handle them internally
class Feedback(FeedbackBase):
    id: int
    created: datetime

    class Config:
        orm_mode = True


"""
Cookie Schema
"""


# base class for both create and read
class CookieBase(BaseModel):
    cookie: str
    cookie_source: str


# only create (We won't know about id during creation)
# useful if we need to separate out sensitive info
# (like a password) that we don't want read to have
class CookieCreate(CookieBase):
    pass


# only read
# username is here because it is not passed in as JSON
# like cookie and cookie_source during create
class Cookie(CookieBase):
    id: int
    username: str
    created: datetime

    class Config:
        orm_mode = True


"""
User Schema
"""


# base class for both create and read
class UserBase(BaseModel):
    username: str


# only create (We won't know about id during creation)
# useful if we need to separate out sensitive info
# (like a password) that we don't want read to have
class UserCreate(UserBase):
    pass


# only read
class User(UserBase):
    id: int
    cookies: List[Cookie] = []
    # feedback: List[Feedback] = []
    created: datetime

    class Config:
        orm_mode = True
