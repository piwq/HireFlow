"""
Seed database with test data for demo.
Run from backend/ directory:
    docker-compose exec backend python seed.py
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models.user import User, UserRole
from app.models.candidate import CandidateProfile
from app.models.vacancy import Vacancy
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview
from app.security import get_password_hash

engine = create_async_engine(settings.database_url)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with Session() as db:
        print("Starting database seed...")
        
        # 1. Users
        users_data = [
            ("admin@example.com", "admin", UserRole.admin),
            ("hr@example.com", "hr_pass", UserRole.hr),
            ("manager@example.com", "mgr_pass", UserRole.manager),
            ("petr@example.com", "candidate", UserRole.candidate),
            ("anna@example.com", "candidate", UserRole.candidate),
            ("maria@example.com", "candidate", UserRole.candidate),
        ]
        
        users_map = {}
        for email, password, role in users_data:
            user = await db.scalar(select(User).where(User.email == email))
            if not user:
                user = User(email=email, hashed_password=get_password_hash(password), role=role)
                db.add(user)
                await db.flush()
            users_map[email] = user
            
        manager = users_map["manager@example.com"]
        hr = users_map["hr@example.com"]

        # 2. Profiles
        profiles_data = [
            (users_map["petr@example.com"], "Петров Пётр", "Python, FastAPI", "Senior", 250000),
            (users_map["anna@example.com"], "Сидорова Анна", "Vue 3, JS, CSS", "Middle", 150000),
            (users_map["maria@example.com"], "Козлова Мария", "DevOps, Docker", "Middle", 180000),
        ]
        profiles = []
        for user, name, skills, level, salary in profiles_data:
            p = await db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
            if not p:
                p = CandidateProfile(
                    user_id=user.id, full_name=name, skills=skills, level=level,
                    salary_from=salary, salary_to=salary+50000, city="Екатеринбург",
                    work_format="remote", employment_type="full-time",
                    desired_position=skills.split(',')[0] + " Developer",
                    experience=f"Опыт работы больше 3 лет. Стек: {skills}"
                )
                db.add(p)
                await db.flush()
            profiles.append(p)

        # 3. Vacancies
        vacs_data = [
            ("Senior Python Developer", "Требуется сильный бекендер на FastAPI."),
            ("Middle Vue.js Developer", "Ищем мастера компонентов Vue 3."),
            ("Middle DevOps Engineer", "Настройка CI/CD, Kubernetes."),
        ]
        vacancies = []
        for title, desc in vacs_data:
            v = await db.scalar(select(Vacancy).where(Vacancy.title == title))
            if not v:
                v = Vacancy(title=title, description=desc)
                db.add(v)
                await db.flush()
            vacancies.append(v)

        # 4. Applications
        apps_data = [
            (profiles[0], vacancies[0], ApplicationStatus.interview),
            (profiles[1], vacancies[1], ApplicationStatus.manager_interview),
            (profiles[2], vacancies[2], ApplicationStatus.new),
        ]
        apps = []
        for profile, vacancy, status in apps_data:
            a = await db.scalar(select(Application).where(
                Application.candidate_id == profile.id, Application.vacancy_id == vacancy.id))
            if not a:
                a = Application(candidate_id=profile.id, vacancy_id=vacancy.id, status=status)
                db.add(a)
                await db.flush()
            apps.append(a)

        # 5. Interviews
        for i, app in enumerate(apps[:2]):
            iv = await db.scalar(select(Interview).where(Interview.application_id == app.id))
            if not iv:
                iv = Interview(
                    application_id=app.id,
                    manager_id=manager.id,
                    scheduled_at=datetime.utcnow() + timedelta(days=1, hours=i),
                    room_code=uuid.uuid4().hex[:8],
                    format="online",
                    comment="Техническое онлайн собеседование"
                )
                db.add(iv)

        await db.commit()
        print("✅ Seed complete!")
        for e, p, _ in users_data:
            print(f"  {e} / {p}")

if __name__ == "__main__":
    asyncio.run(seed())
