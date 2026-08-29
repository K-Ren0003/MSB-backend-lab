from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    display_name: str
    email: str

users= []

class TeamCreate(BaseModel):
    name: str
    code: str

class EventCreate(BaseModel):
    home_team_id: int
    away_team_id: int
    starts_at: str
    status: str

events = []

class TipCreate(BaseModel):
    user_id: int
    event_id: int
    predicted_winner_team_id: int

tips = []

@app.get("/health")
def health():
    return{"status": "ok"}

teams = [ 
    {"id": 1, "name": "Brisbane Broncos", "code": "BRI"},
    {"id": 2, "name": "Melbourne Storm", "code": "MEL"},
]

@app.get("/teams") #get all teams
def get_teams():
    return teams

@app.get("/teams/{team_id}")
def get_teams(team_id: int):
    for team in teams:
        if team["id"] == team_id:
            return team
        
    raise HTTPException(status_code=404, detail="Team not found")

@app.post("/teams", status_code=201)
def create_team(team: TeamCreate):
    new_team = {
        "id": len(teams) + 1,
        "name": team.name,
        "code": team.code
    }

    teams.append(new_team)
    return new_team

@app.post("/events", status_code=201)
def create_event(event: EventCreate):
    new_event = {
        "id": len(events)+1,
        "home_team_id": event.home_team_id,
        "away_team_id": event.away_team_id,
        "starts_at": event.starts_at,
        "status": event.status     
    }

    events.append(new_event)
    return new_event

@app.get("/events") # get all events
def get_events():
    return events

@app.get("/events/{event_id}")
def get_event(event_id: int):
    for event in events:
        if event["id"] == event_id:
            return event

    raise HTTPException(status_code=404, detail="Event not found")

@app.put("/events/{event_id}")
def update_event(event_id: int, updated_event: EventCreate):
    for event in events:
        if event["id"] == event_id:
            event["home_team_id"] = updated_event.home_team_id,
            event["away_team_id"] = updated_event.away_team_id,
            event["starts_at"] = updated_event.starts_at,
            event["status"] = updated_event.status

            return event

    raise HTTPException(status_code=404, detail="Event not found")

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    new_user = {
        "id": len(users) + 1,
        "display_name": user.display_name,
        "email": user.email
    }

    users.append(new_user)
    return new_user

@app.get("/users")
def get_users():
    return users

@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
        
    raise HTTPException(status_code=404, detail="user not found")

@app.post("/tips", status_code=201)
def create_tips(tip: TipCreate):
    new_tip = {
    "id": len(tips) + 1,
    "user_id": tip.user_id,
    "event_id": tip.event_id,
    "predicted_winner_team_id": tip.predicted_winner_team_id
    }

    users.append(new_tip)
    return new_tip

@app.get("/tips/{tip_id}")
def get_tip(tip_id: int):
    for tip in tips:
        if tip["id"] == tip_id:
            return tip

    raise HTTPException(status_code=404, detail="Tip not found")

@app.get("/users/{user_id}/tips")
def get_user_tips(user_id: int):
    user_exists = False

    for user in users:
        if user["id"] == user_id:
            user_exists = True
            break

    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    user_tips = []

    for tip in tips:
        if tip["user_id"] == user_id:
            user_tips.append(tip)

    return user_tips