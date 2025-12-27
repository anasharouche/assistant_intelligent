from datetime import date, time, timedelta

from app.db.session import SessionLocal
from app.core.security import hash_password
from app.db.models import User, Filiere, Groupe, Student, Teacher, Module, TimetableSession


def run():
    db = SessionLocal()
    try:
        # Clean (dev only)
        db.query(TimetableSession).delete()
        db.query(Module).delete()
        db.query(Student).delete()
        db.query(Teacher).delete()
        db.query(Groupe).delete()
        db.query(Filiere).delete()
        db.query(User).delete()
        db.commit()

        # Filiere + Groupe
        filiere = Filiere(name="MIAGE")
        db.add(filiere)
        db.commit()
        db.refresh(filiere)

        g1 = Groupe(name="MIAGE-5A-G1", filiere_id=filiere.id, niveau="5A")
        db.add(g1)
        db.commit()
        db.refresh(g1)

        # Users
        u_student = User(
            email="student1@test.com",
            hashed_password=hash_password("Password123"),
            role="STUDENT",
            is_active=True,
        )
        u_teacher = User(
            email="teacher1@test.com",
            hashed_password=hash_password("Password123"),
            role="TEACHER",
            is_active=True,
        )
        db.add_all([u_student, u_teacher])
        db.commit()
        db.refresh(u_student)
        db.refresh(u_teacher)

        # Profiles
        student = Student(
            user_id=u_student.id,
            code_apogee="A12345",
            cin="CIN12345",
            filiere_id=filiere.id,
            groupe_id=g1.id,
            niveau="5A",
        )
        teacher = Teacher(
            user_id=u_teacher.id,
            department="Informatique",
            grade="Professeur",
        )
        db.add_all([student, teacher])
        db.commit()
        db.refresh(student)
        db.refresh(teacher)

        # Modules
        m1 = Module(code="MIAGE501", name="IA & Data Science", filiere_id=filiere.id, niveau="5A")
        m2 = Module(code="MIAGE502", name="Cloud & DevOps", filiere_id=filiere.id, niveau="5A")
        db.add_all([m1, m2])
        db.commit()
        db.refresh(m1)
        db.refresh(m2)

        # Timetable sessions (next 5 days)
        base = date.today()
        sessions = []
        for i in range(5):
            d = base + timedelta(days=i)
            sessions.append(
                TimetableSession(
                    date=d,
                    start_time=time(9, 0),
                    end_time=time(10, 30),
                    room="B101",
                    module_id=m1.id,
                    groupe_id=g1.id,
                    teacher_id=teacher.id,
                )
            )
            sessions.append(
                TimetableSession(
                    date=d,
                    start_time=time(11, 0),
                    end_time=time(12, 30),
                    room="B202",
                    module_id=m2.id,
                    groupe_id=g1.id,
                    teacher_id=teacher.id,
                )
            )

        db.add_all(sessions)
        db.commit()
        print("Seed OK: data inserted.")

    finally:
        db.close()


if __name__ == "__main__":
    run()
