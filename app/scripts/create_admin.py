"""Create or promote an admin user.

Usage (inside the container or venv):
    uv run python -m app.scripts.create_admin admin@example.com StrongPass123

If a user with that email already exists, it is promoted to admin.
Otherwise a new admin user is created with no employer/candidate profile.
"""
import sys

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.security import hash_password


def create_admin(email: str, password: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = UserRole.ADMIN
            user.is_active = True
            db.commit()
            print(f"Promoted existing user {email} to admin.")
            return

        user = User(email=email, hashed_password=hash_password(password), role=UserRole.ADMIN)
        db.add(user)
        db.commit()
        print(f"Created admin user {email}.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: uv run python -m app.scripts.create_admin <email> <password>")
        sys.exit(1)
    create_admin(sys.argv[1], sys.argv[2])
