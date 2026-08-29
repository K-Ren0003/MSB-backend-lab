from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.app.db import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(10))

    home_events: Mapped[list[Event]] = relationship(
        foreign_keys="Event.home_team_id",
        back_populates="home_team",
    )
    away_events: Mapped[list[Event]] = relationship(
        foreign_keys="Event.away_team_id",
        back_populates="away_team",
    )
    predicted_tips: Mapped[list[Tip]] = relationship(
        foreign_keys="Tip.predicted_winner_team_id",
        back_populates="predicted_winner_team",
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))

    tips: Mapped[list[Tip]] = relationship(back_populates="user")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    home_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id")
    )

    away_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id")
    )

    starts_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20))

    home_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    away_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    home_team: Mapped[Team] = relationship(
        foreign_keys=[home_team_id],
        back_populates="home_events",
    )
    away_team: Mapped[Team] = relationship(
        foreign_keys=[away_team_id],
        back_populates="away_events",
    )
    tips: Mapped[list[Tip]] = relationship(back_populates="event")


class Tip(Base):
    __tablename__ = "tips"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id")
    )

    predicted_winner_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id")
    )

    user: Mapped[User] = relationship(back_populates="tips")
    event: Mapped[Event] = relationship(back_populates="tips")
    predicted_winner_team: Mapped[Team] = relationship(
        foreign_keys=[predicted_winner_team_id],
        back_populates="predicted_tips",
    )
