"""
Seed database with test data for demo.
Run from backend/ directory:
    python seed.py
Or inside Docker:
    docker-compose exec backend python seed.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from passlib.context import CryptContext

from app.config import settings
from app.models.user import User, UserRole
from app.models.candidate import CandidateProfile
from app.models.vacancy import Vacancy
from app.models.application import Application, ApplicationStatus

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_async_engine(settings.database_url)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def seed():
    async with Session() as db:
        # Users
        users_data = [
            ("petr@example.com", "candidate", UserRole.candidate),
            ("anna@example.com", "candidate", UserRole.candidate),
            ("maria@example.com", "candidate", UserRole.candidate),
            ("hr@example.com", "hr_pass", UserRole.hr),
            ("manager@example.com", "mgr_pass", UserRole.manager),
        ]
        users = []
        for email, password, role in users_data:
            u = User(email=email, password_hash=pwd.hash(password), role=role)
            db.add(u)
            users.append(u)
        await db.flush()

        # Candidate profiles
        profiles_data = [
            (users[0], "Петров Пётр Петрович", "Python, FastAPI, PostgreSQL", "3 года backend-разработчик в ООО Технологии"),
            (users[1], "Сидорова Анна Ивановна", "React, TypeScript, Node.js", "2 года frontend-разработчик"),
            (users[2], "Козлова Мария Сергеевна", "DevOps, Docker, Kubernetes, CI/CD", "4 года DevOps-инженер"),
        ]
        profiles = []
        for user, name, skills, exp in profiles_data:
            p = CandidateProfile(user_id=user.id, full_name=name, skills=skills, experience=exp)
            db.add(p)
            profiles.append(p)
        await db.flush()

        # Vacancies
        vacancies_data = [
            ("Backend Python Developer", "FastAPI, SQLAlchemy, PostgreSQL. Опыт от 2 лет."),
            ("Frontend React Developer", "React 18, TypeScript, Tailwind. Опыт от 1 года."),
        ]
        vacancies = []
        for title, desc in vacancies_data:
            v = Vacancy(title=title, description=desc)
            db.add(v)
            vacancies.append(v)
        await db.flush()

        # Applications with different statuses
        apps_data = [
            (profiles[0], vacancies[0], ApplicationStatus.interview),
            (profiles[1], vacancies[1], ApplicationStatus.screening),
            (profiles[2], vacancies[0], ApplicationStatus.new),
        ]
        for profile, vacancy, status in apps_data:
            a = Application(candidate_id=profile.id, vacancy_id=vacancy.id, status=status)
            db.add(a)

        await db.commit()
        print("✅ Seed complete!")
        print("  hr@example.com / hr_pass")
        print("  manager@example.com / mgr_pass")
        print("  petr@example.com / candidate")
        print("  anna@example.com / candidate")
        print("  maria@example.com / candidate")


asyncio.run(seed())
