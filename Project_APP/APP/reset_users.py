import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db import User, hash_password, Role, SessionLocal, Base

# Only keep these users
TARGET_USERS = [
    {"username": "Nithin", "password": "password", "role": "user"},
    {"username": "standard", "password": "password", "role": "user"},
    {"username": "admin", "password": "password", "role": "admin"},
]

def main():
    with SessionLocal() as session:
        # Delete all users except the target ones
        session.query(User).filter(~User.username.in_([u["username"] for u in TARGET_USERS])).delete(synchronize_session=False)
        session.commit()

        # Ensure each target user exists with correct password and role
        for user in TARGET_USERS:
            db_user = session.query(User).filter_by(username=user["username"]).first()
            if db_user:
                setattr(db_user, "password_hash", hash_password(user["password"]))
                # Assign correct role
                role_obj = session.query(Role).filter_by(name=user["role"]).first()
                if role_obj:
                    db_user.roles.clear()
                    db_user.roles.append(role_obj)
            else:
                # Create user if missing
                from db import register_user
                register_user(user["username"], user["password"], user["role"])
        session.commit()
    print("User database reset: only Nithin, standard, and admin exist, all with password 'password'.")

if __name__ == "__main__":
    main()