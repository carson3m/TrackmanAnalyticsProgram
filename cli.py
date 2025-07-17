import typer

# Force Typer into multi-command mode
app = typer.Typer(no_args_is_help=True)

@app.command()
def create_user():
    """
    Create a new user in the database.
    """
    from app.models.database import SessionLocal
    from app.models.user import User

    username = input("Username: ")
    password = input("Password: ")
    role = input("Role (admin/coach/viewer): ").strip().lower()

    if role not in ["admin", "coach", "viewer"]:
        print("❌ Invalid role. Use admin, coach, or viewer.")
        return

    db = SessionLocal()
    if db.query(User).filter(User.username == username).first():
        print("❌ User already exists.")
        db.close()
        return

    hashed_password = User.hash_password(password)
    user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.close()

    print(f"✅ Created user '{username}' with role '{role}'")

@app.command()
def list_users():
    """
    List all users in the database.
    """
    from app.models.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    users = db.query(User).all()
    if not users:
        print("⚠️ No users found.")
    else:
        print("📋 Users:")
        for user in users:
            print(f"- {user.username} ({user.role})")
    db.close()

@app.command()
def reset_password(username: str):
    """
    Reset a user's password.
    """
    from app.models.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ User '{username}' not found.")
        db.close()
        return

    new_password = input(f"Enter new password for '{username}': ")
    user.hashed_password = User.hash_password(new_password)
    db.commit()
    db.close()

    print(f"✅ Password for '{username}' has been reset.")

if __name__ == "__main__":
    app()
