"""User and UserRole database queries with exception handling."""

import random
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import database
import models
from exceptions import DatabaseError


def get_user_count(db: Session) -> int:
    """Return count of users. Raises DatabaseError on failure."""
    try:
        return db.query(models.User).count()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to count users", cause=e)


def get_all_users(db: Session) -> list:
    """Return all users. Raises DatabaseError on failure."""
    try:
        return db.query(models.User).all()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch users", cause=e)


def get_user_by_login_id(db: Session, login_id: str):
    """Return user by LoginId or None if not found. Raises DatabaseError on failure."""
    try:
        return db.query(models.User).filter(models.User.LoginId == login_id).first()
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to fetch user by login", cause=e)


def seed_users(db: Session) -> None:
    """
    Seeds the database with 3 random users and their roles if the users table is empty.
    Stores the insert queries into 'seed_users.sql'.
    Raises DatabaseError on failure.
    """
    first_names = ["John", "Jane", "Robert", "Emily", "Michael", "Sarah", "David", "Linda"]
    last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis"]
    ranks = ["MAJOR", "CAPTAIN", "LT COL", "COLONEL"]
    depts = ["ADMIN", "LOG", "OPS", "TECH"]
    stations = ['K', 'U', 'B', 'V', 'D', 'P', 'A', 'G']
    roles_pool = ["NLAO", "AUDITOR"]
    sql_queries = []

    try:
        for i in range(3):
            login_id = f"user{i+1}"
            user_id = f"ID{random.randint(1000, 9999)}"
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            rank = random.choice(ranks)
            dept = random.choice(depts)
            stn = random.choice(stations)
            joined_date = datetime.now() - timedelta(days=random.randint(100, 1000))

            new_user = models.User(
                LoginId=login_id,
                Id=user_id,
                Name=name,
                Rank=rank,
                Department=dept,
                DateTimeJoined=joined_date,
                StationCode=stn
            )
            db.add(new_user)
            sql_queries.append(
                f"INSERT INTO Users (LoginId, Id, Name, Rank, Department, DateTimeJoined, StationCode) "
                f"VALUES ('{login_id}', '{user_id}', '{name}', '{rank}', '{dept}', '{joined_date.strftime('%Y-%m-%d %H:%M:%S')}', '{stn}');"
            )

            num_roles = random.randint(1, 3)
            assigned_roles = random.sample(roles_pool, num_roles)
            for role_name in assigned_roles:
                activated_date = joined_date + timedelta(days=1)
                new_role = models.UserRole(
                    LoginId=login_id,
                    RoleName=role_name,
                    DateTimeActivated=activated_date,
                    StationCode=stn
                )
                db.add(new_role)
                sql_queries.append(
                    f"INSERT INTO UserRole (LoginId, RoleName, DateTimeActivated, StationCode) "
                    f"VALUES ('{login_id}', '{role_name}', '{activated_date.strftime('%Y-%m-%d %H:%M:%S')}', '{stn}');"
                )

        db.commit()

        with open("sql_scripts/seed_users.sql", "w") as f:
            f.write("\n".join(sql_queries))
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Failed to seed users", cause=e)
    except OSError as e:
        db.rollback()
        raise DatabaseError("Failed to write seed_users.sql", cause=e)


def sync_db_users(db: Session) -> None:
    """
    Ensures all users in the 'Users' table exist as Sybase database logins and users.
    Default password for new users is 'password'.
    Raises DatabaseError on failure.
    """
    try:
        users = db.query(models.User).all()
        engine = db.get_bind()

        for user in users:
            username = user.LoginId
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                login_exists = conn.execute(
                    text("SELECT name FROM master..syslogins WHERE name = :username"),
                    {"username": username}
                ).fetchone()

                if not login_exists:
                    conn.execute(
                        text("EXEC sp_addlogin :username, 'password', :dbname"),
                        {"username": username, "dbname": database.SYBASE_DB}
                    )

                user_exists = conn.execute(
                    text("SELECT name FROM sysusers WHERE name = :username"),
                    {"username": username}
                ).fetchone()

                if not user_exists:
                    conn.execute(
                        text("EXEC sp_adduser :username"),
                        {"username": username}
                    )
    except SQLAlchemyError as e:
        raise DatabaseError("Failed to sync database users", cause=e)
