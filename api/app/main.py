from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo.collection import Collection
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.app.db import get_db
from api.app.models import Event, Team, Tip, User
from api.app.mongo import get_activity_collection

app = FastAPI(title="MSB Backend Lab API")

DatabaseSession = Annotated[Session, Depends(get_db)]
ActivityCollection = Annotated[Collection, Depends(get_activity_collection)]


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=2, max_length=10)


class EventCreate(BaseModel):
    home_team_id: int = Field(gt=0)
    away_team_id: int = Field(gt=0)
    starts_at: datetime
    status: Literal["scheduled", "live", "completed", "cancelled"]


class UserCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)


class TipCreate(BaseModel):
    user_id: int = Field(gt=0)
    event_id: int = Field(gt=0)
    predicted_winner_team_id: int = Field(gt=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/teams")
def get_teams(db: DatabaseSession):
    return db.scalars(select(Team)).all()


@app.get("/teams/{team_id}")
def get_team(team_id: int, db: DatabaseSession):
    team = db.get(Team, team_id)

    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


@app.post("/teams", status_code=201)
def create_team(team: TeamCreate, db: DatabaseSession):
    new_team = Team(name=team.name, code=team.code)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team


@app.post("/events", status_code=201)
def create_event(event: EventCreate, db: DatabaseSession):
    new_event = Event(
        home_team_id=event.home_team_id,
        away_team_id=event.away_team_id,
        starts_at=event.starts_at,
        status=event.status,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@app.get("/events")
def get_events(db: DatabaseSession):
    return db.scalars(select(Event)).all()


@app.get("/events/{event_id}")
def get_event(event_id: int, db: DatabaseSession):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@app.put("/events/{event_id}")
def update_event(event_id: int, updated_event: EventCreate, db: DatabaseSession):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    event.home_team_id = updated_event.home_team_id
    event.away_team_id = updated_event.away_team_id
    event.starts_at = updated_event.starts_at
    event.status = updated_event.status
    db.commit()
    db.refresh(event)
    return event


@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: DatabaseSession):
    new_user = User(display_name=user.display_name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users")
def get_users(db: DatabaseSession):
    return db.scalars(select(User)).all()


@app.get("/users/{user_id}")
def get_user(user_id: int, db: DatabaseSession):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/tips", status_code=201)
def create_tip(
    tip: TipCreate,
    db: DatabaseSession,
    collection: ActivityCollection,
):
    new_tip = Tip(
        user_id=tip.user_id,
        event_id=tip.event_id,
        predicted_winner_team_id=tip.predicted_winner_team_id,
    )
    db.add(new_tip)
    db.commit()
    db.refresh(new_tip)

    collection.insert_one(
        {
            "event_type": "tip.created",
            "user_id": new_tip.user_id,
            "tip_id": new_tip.id,
            "event_id": new_tip.event_id,
            "metadata": {"source": "api"},
            "created_at": datetime.now(timezone.utc),
        }
    )
    return new_tip


@app.get("/tips/{tip_id}")
def get_tip(tip_id: int, db: DatabaseSession):
    tip = db.get(Tip, tip_id)

    if tip is None:
        raise HTTPException(status_code=404, detail="Tip not found")

    return tip


@app.get("/users/{user_id}/tips")
def get_user_tips(user_id: int, db: DatabaseSession):
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db.scalars(select(Tip).where(Tip.user_id == user_id)).all()


@app.get("/activity-events")
def get_activity_events(
    collection: ActivityCollection,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    documents = collection.find().sort("_id", -1).limit(limit)
    results = []

    for document in documents:
        serialized = dict(document)
        serialized["id"] = str(serialized.pop("_id"))
        results.append(serialized)

    return results
