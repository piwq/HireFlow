"""
Seed database with comprehensive test data for demo.
Run from backend/ directory:
    docker-compose exec backend python seed.py
"""
import asyncio
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext

from app.config import settings
from app.models.user import User, UserRole
from app.models.candidate import CandidateProfile
from app.models.vacancy import Vacancy
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview
from app.models.feedback import Feedback
from app.models.status_history import StatusHistory
from app.models.note import Note

# Locally defined password hashing logic matching app/routers/auth.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_async_engine(settings.database_url)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with Session() as db:
        print("🚀 Starting comprehensive database seed...")
        
        # 1. Create Users
        users_data = [
            ("admin@hireflow.ru", "admin123", UserRole.admin),
            ("hr_expert@hireflow.ru", "hr_pass", UserRole.hr),
            ("tech_lead@hireflow.ru", "mgr_pass", UserRole.manager),
            ("cto@hireflow.ru", "mgr_pass", UserRole.manager),
            ("alex_dev@mail.ru", "candidate", UserRole.candidate),
            ("vera_design@ya.ru", "candidate", UserRole.candidate),
            ("ivan_qa@gmail.com", "candidate", UserRole.candidate),
            ("elena_pm@mail.ru", "candidate", UserRole.candidate),
            ("dmitry_devops@ya.ru", "candidate", UserRole.candidate),
        ]
        
        users_map = {}
        for email, password, role in users_data:
            user = await db.scalar(select(User).where(User.email == email))
            if not user:
                user = User(
                    email=email, 
                    password_hash=pwd_context.hash(password), 
                    role=role
                )
                db.add(user)
                await db.flush()
                print(f"  + User created: {email} ({role})")
            users_map[email] = user
            
        admin = users_map["admin@hireflow.ru"]
        hr = users_map["hr_expert@hireflow.ru"]
        tech_lead = users_map["tech_lead@hireflow.ru"]
        cto = users_map["cto@hireflow.ru"]

        # 2. Create Vacancies
        vacs_data = [
            ("Senior Python/FastAPI Developer", 
             "Ищем опытного бэкенд-разработчика для развития ядра HireFlow. Стек: Python 3.11, FastAPI, PostgreSQL, Redis, Docker.\n"
             "Требования: опыт от 5 лет, знание асинхронности, умение проектировать архитектуру."),
            
            ("Frontend Architect (Vue.js)", 
             "Нужен эксперт по Vue 3 для построения масштабируемой фронтенд-архитектуры. \n"
             "Ожидаем: глубокое знание Composition API, Vite, Pinia, Tailwind CSS. Опыт разработки дизайн-систем будет плюсом."),
            
            ("QA Automation Engineer (Python)", 
             "Роль для тех, кто любит качество. Написание автотестов для API и UI (Playwright/Pytest).\n"
             "Контроль качества release candidate, настройка CI пайплайнов."),
            
            ("Project Manager (HR-Tech)", 
             "Управление циклом разработки продукта. Взаимодействие со стейкхолдерами, планирование спринтов, фасилитация встреч."),
        ]
        
        vacancies = []
        for title, desc in vacs_data:
            v = await db.scalar(select(Vacancy).where(Vacancy.title == title))
            if not v:
                v = Vacancy(title=title, description=desc)
                db.add(v)
                await db.flush()
                print(f"  + Vacancy created: {title}")
            vacancies.append(v)

        # 3. Create Candidate Profiles
        profiles_data = [
            ("alex_dev@mail.ru", "Александр Кузнецов", "Python, FastAPI, Django, K8s", "Senior", 280000, "Москва", "Senior Software Engineer"),
            ("vera_design@ya.ru", "Вера Соколова", "Vue 3, JS, UI/UX, Figma", "Middle", 160000, "Санкт-Петербург", "Frontend Developer"),
            ("ivan_qa@gmail.com", "Иван Морозов", "Python, Pytest, Playwright, SQL", "Middle", 190000, "Екатеринбург", "QA Automation Lead"),
            ("elena_pm@mail.ru", "Елена Новикова", "Agile, Scrum, Jira, Roadmap", "Senior", 220000, "Удаленно", "Product & Project Manager"),
            ("dmitry_devops@ya.ru", "Дмитрий Волков", "Terraform, Ansible, AWS, K8s", "Middle", 210000, "Казань", "DevOps Engineer"),
        ]
        
        profiles = []
        for email, name, skills, level, salary, city, pos in profiles_data:
            user = users_map[email]
            p = await db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
            if not p:
                p = CandidateProfile(
                    user_id=user.id, full_name=name, skills=skills, level=level,
                    salary_from=salary, salary_to=salary+40000, city=city,
                    work_format="remote" if city == "Удаленно" else "hybrid",
                    employment_type="full-time", desired_position=pos,
                    experience=f"Более {random.randint(3, 8)} лет опыта в {pos}. Работал в крупных финтех проектах."
                )
                db.add(p)
                await db.flush()
                print(f"  + Profile created: {name}")
            profiles.append(p)

        # 4. Create Applications & Status History
        apps_data = [
            (profiles[0], vacancies[0], ApplicationStatus.interview_done),
            (profiles[1], vacancies[1], ApplicationStatus.interview),
            (profiles[2], vacancies[2], ApplicationStatus.screening),
            (profiles[3], vacancies[3], ApplicationStatus.new),
            (profiles[4], vacancies[0], ApplicationStatus.rejected),
        ]
        
        apps = []
        for profile, vacancy, status in apps_data:
            a = await db.scalar(select(Application).where(
                Application.candidate_id == profile.id, Application.vacancy_id == vacancy.id))
            if not a:
                a = Application(candidate_id=profile.id, vacancy_id=vacancy.id, status=status)
                db.add(a)
                await db.flush()
                
                stages = [ApplicationStatus.new]
                if status != ApplicationStatus.new:
                    stages.append(ApplicationStatus.screening)
                if status in [ApplicationStatus.interview, ApplicationStatus.interview_done, ApplicationStatus.rejected]:
                    stages.append(status)
                
                prev_status = None
                for idx, s in enumerate(stages):
                    h = StatusHistory(
                        application_id=a.id, 
                        from_status=prev_status.value if prev_status else None,
                        to_status=s.value,
                        changed_by=hr.id,
                        changed_at=datetime.utcnow() - timedelta(days=5-idx)
                    )
                    db.add(h)
                    prev_status = s
                print(f"  + Application: {profile.full_name} -> {vacancy.title} ({status.value})")
            apps.append(a)

        # 5. Create Interviews
        alex_iv = await db.scalar(select(Interview).where(Interview.application_id == apps[0].id))
        if not alex_iv:
            alex_iv = Interview(
                application_id=apps[0].id,
                manager_id=tech_lead.id,
                scheduled_at=datetime.utcnow() - timedelta(days=1),
                room_code=uuid.uuid4().hex[:8],
                format="online",
                comment="Техническое интервью с техлидом бэкенда",
                invitation_status="confirmed"
            )
            db.add(alex_iv)
            await db.flush()
            print(f"  + Interview scheduled (Past): Alex")

        vera_iv = await db.scalar(select(Interview).where(Interview.application_id == apps[1].id))
        if not vera_iv:
            vera_iv = Interview(
                application_id=apps[1].id,
                manager_id=cto.id,
                scheduled_at=datetime.utcnow() + timedelta(days=2, hours=10),
                room_code=uuid.uuid4().hex[:8],
                format="online",
                comment="Финальное интервью с CTO",
                invitation_status="pending"
            )
            db.add(vera_iv)
            await db.flush()
            print(f"  + Interview scheduled (Future): Vera")

        # 6. Create Feedback for Completed Interview
        if alex_iv:
            fb = await db.scalar(select(Feedback).where(Feedback.interview_id == alex_iv.id))
            if not fb:
                fb = Feedback(
                    interview_id=alex_iv.id,
                    manager_id=tech_lead.id,
                    score_overall=5,
                    score_technical=5,
                    score_communication=4,
                    score_fit=5,
                    strengths="Глубокое понимание asyncio и архитектуры БД. Отличный опыт с K8s.",
                    weaknesses="Немного медленно отвечал на вопросы по алгоритмам.",
                    recommendation="recommend",
                    text="Кандидат очень сильный, рекомендую брать на Senior позицию как можно быстрее."
                )
                db.add(fb)
                print(f"  + Feedback added for Alex")

        # 7. Add some notes for HR
        for profile in profiles:
            result = await db.execute(select(Note).where(Note.candidate_id == profile.id))
            note = result.scalar_one_or_none()
            if not note:
                db.add(Note(
                    candidate_id=profile.id,
                    author_id=hr.id,
                    text=f"Кандидат {profile.full_name} очень перспективен. Обратить внимание на {profile.skills.split(',')[0]}.",
                    created_at=datetime.utcnow() - timedelta(days=2)
                ))

        await db.commit()
        print("\n✅ SEED COMPLETE! Use these credentials to test roles:")
        print("-" * 50)
        print(f"  🚀 ADMIN:    admin@hireflow.ru / admin123")
        print(f"  🏢 HR:       hr_expert@hireflow.ru / hr_pass")
        print(f"  💼 MANAGER:  tech_lead@hireflow.ru / mgr_pass")
        print(f"  🧑 CANDIDATE: alex_dev@mail.ru / candidate")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(seed())
