from app.db.session import SessionLocal
from app.db.models import User
from app.core.security import hash_password

db = SessionLocal()

email = "scolarite@test.com"
password = "Password123"

existing = db.query(User).filter(User.email == email).first()
if existing:
    print("❌ User already exists")
else:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role="SCOLARITE",
        is_active=True,
    )
    db.add(user)
    db.commit()
    print("✅ SCOLARITE user created")

db.close()
