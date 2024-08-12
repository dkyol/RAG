from fastapi import FastAPI, Body, Query, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from typing import List, Union
import datetime as dt
import os
import time
import httpx
import asyncio

# import json

import crud
import sql_models as models
import sql_schemas as schemas
from database import SessionLocal, engine
import docs


from dp_solutions_architecture_utils.logger import LoggerUtil

#########################################################
################## LOAD ENV VARIABLES ###################
#########################################################


#########################################################
################ END LOAD ENV VARIABLES #################
#########################################################


##############################
### BOILERPLATE CODE START ###
##############################

models.Base.metadata.create_all(bind=engine)

# Instantiate logger
logger = LoggerUtil(__name__)

# Instantiate FastAPI with some info needed for docs
logger.info("Instantiating FastAPI app")
logger.info("Formatting uvicorn loggers before app startup")
LoggerUtil.format_uvicorn()
app = FastAPI(
    title="Judge",
    description=docs.description,
    openapi_tags=docs.tags_metadata,
)
docs.clear_openapi_responses(app)


# Enables CORS
logger.info("Enabling CORS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# path to directory containing this Python file
src_dir_path = os.path.dirname(os.path.realpath(__file__))

# Point app to static files (fonts, images, etc.)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(src_dir_path, "static")),
    name="static",
)

# Point app to Jinja templates (html, css, js, etc.)
templates = Jinja2Templates(directory=os.path.join(src_dir_path, "templates"))


# Connect to SQL
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clean_username(username):
    cleaned = username.strip().lower()
    if cleaned.endswith("@nvidia.com"):
        cleaned = cleaned[: cleaned.index("@nvidia.com")]
    return cleaned


logger.info("FastAPI Setup Complete")


# Need to re-format loggers because app startup overwrites what we set earlier
@app.on_event("startup")
async def startup_event():
    logger.info("Re-formatting uvicorn loggers on startup")
    LoggerUtil.format_uvicorn()


##############################
#### BOILERPLATE CODE END ####
##############################


##############################
##### API ENDPOINTS START ####
##############################


"""
Health Check Endpoint
"""


@app.get("/health", tags=["health"])
async def health():
    return JSONResponse(status_code=200, content={"success": True})


"""
Users Endpoints
"""


@app.post("/v1/users/", response_model=schemas.User, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    cleaned = clean_username(user.username)
    db_user = crud.get_user_by_username(db, username=cleaned)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/v1/users/", response_model=List[schemas.User], tags=["users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/v1/users/{username}", response_model=schemas.User, tags=["users"])
def read_user(username: str, db: Session = Depends(get_db)):
    cleaned = clean_username(username)
    db_user = crud.get_user_by_username(db, username=cleaned)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


"""
Adobe Cookies Endpoints
"""


@app.post(
    "/v1/users/{username}/cookies/", response_model=schemas.Cookie, tags=["cookies"]
)
def create_cookie_for_user(
    username: str, cookie: schemas.CookieCreate, db: Session = Depends(get_db)
):
    cleaned = clean_username(username)
    db_cookie = crud.get_cookie(db, cookie=cookie.cookie)
    if db_cookie is None:
        return crud.create_user_cookie(db=db, cookie=cookie, username=cleaned)
    return crud.update_user_cookie(db=db, cookie=cookie.cookie, username=cleaned)


@app.get("/v1/cookies/", response_model=List[schemas.Cookie], tags=["cookies"])
def read_cookies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cookies = crud.get_cookies(db, skip=skip, limit=limit)
    return cookies


@app.get("/v1/cookies/{cookie}", response_model=schemas.Cookie, tags=["cookies"])
def read_cookie(cookie: str, db: Session = Depends(get_db)):
    db_cookie = crud.get_cookie(db, cookie=cookie)
    if db_cookie is None:
        raise HTTPException(status_code=404, detail="Cookie not found")
    logger.info(jsonable_encoder(db_cookie.user))
    return db_cookie


"""
Feedback Endpoints
"""


@app.post("/v1/feedback/", response_model=schemas.Feedback, tags=["feedback"])
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    cleaned = clean_username(feedback.username)
    feedback.username = cleaned

    # delete older vote if it already exists
    if _delete_feedback(feedback, db):
        logger.info("DELETED EXISTING OLDER VOTE")

    # delete opposite vote if it exists
    opposite_vote = feedback.model_copy(deep=True)
    if opposite_vote.vote_value == 0:
        opposite_vote.vote_value = 1
    else:
        opposite_vote.vote_value = 0
    if _delete_feedback(opposite_vote, db):
        logger.info("DELETED OPPOSITE VOTE")

    return crud.create_feedback(db=db, feedback=feedback)


def _delete_feedback(feedback: schemas.FeedbackDelete, db: Session):
    cleaned = clean_username(feedback.username)
    feedback.username = cleaned
    db_feedback = crud.get_feedback(db=db, feedback=feedback)
    if db_feedback is not None:
        logger.info("DELETING FEEDBACK")
        # delete existing
        crud.delete_feedback(db=db, feedback=db_feedback)
        return True
    return False


@app.delete("/v1/feedback/", tags=["feedback"])
def delete_feedback(feedback: schemas.FeedbackDelete, db: Session = Depends(get_db)):
    if _delete_feedback(feedback, db):
        return {"detail": "Feedback deleted"}
    raise HTTPException(status_code=404, detail="Feedback not found")


@app.get("/v1/feedback/", response_model=List[schemas.Feedback], tags=["feedback"])
def read_feedback(
    vote_value: Union[int, None] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    feedback = crud.get_all_feedback(db, vote_value=vote_value, skip=skip, limit=limit)
    return feedback


# """
# Utils Endpoints
# """


##############################
###### API ENDPOINTS END #####
##############################


##############################
###### TEMPLATES START #######
##############################

"""
Home Page
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


"""
Feedback Page - Leaderboard and Past Submissions
"""


@app.get("/feedback", response_class=HTMLResponse, include_in_schema=False)
async def feedback_page(request: Request):
    return templates.TemplateResponse("feedback.html", {"request": request})


##############################
######## TEMPLATES END #######
##############################
