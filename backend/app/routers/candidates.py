from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import os
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.schemas.candidate import (
    ProfileUpsert, 
    ProfileResponse, 
    ResumeEnhanceRequest,
    ResumeGenerateRequest,
    ResumeAIResponse,
    ResumeEnhanceStreamRequest,
    DraftSaveRequest,
    DraftResponse
)
import asyncio

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/", response_model=list[ProfileResponse])
async def list_candidates(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    result = await db.execute(
        select(CandidateProfile).options(selectinload(CandidateProfile.user))
    )
    profiles = result.scalars().all()
    out = []
    for p in profiles:
        out.append(ProfileResponse(
            id=p.id,
            user_id=p.user_id,
            full_name=p.full_name,
            skills=p.skills,
            experience=p.experience,
            resume_url=p.resume_url,
            email=p.user.email if p.user else None,
            phone=p.phone,
            city=p.city,
            citizenship=p.citizenship,
            birth_date=p.birth_date,
            linkedin=p.linkedin,
            github=p.github,
            portfolio=p.portfolio,
            desired_position=p.desired_position,
            specialization=p.specialization,
            level=p.level,
            salary_from=p.salary_from,
            salary_to=p.salary_to,
            employment_type=p.employment_type,
            work_format=p.work_format,
            relocation_ready=p.relocation_ready,
        ))
    return out


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        skills=profile.skills,
        experience=profile.experience,
        resume_url=profile.resume_url,
        email=current_user.email,
        phone=profile.phone,
        city=profile.city,
        citizenship=profile.citizenship,
        birth_date=profile.birth_date,
        linkedin=profile.linkedin,
        github=profile.github,
        portfolio=profile.portfolio,
        desired_position=profile.desired_position,
        specialization=profile.specialization,
        level=profile.level,
        salary_from=profile.salary_from,
        salary_to=profile.salary_to,
        employment_type=profile.employment_type,
        work_format=profile.work_format,
        relocation_ready=profile.relocation_ready,
    )


@router.post("/profile", response_model=ProfileResponse)
async def upsert_profile(
    body: ProfileUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    extended = {
        "phone": body.phone,
        "city": body.city,
        "citizenship": body.citizenship,
        "birth_date": body.birth_date,
        "linkedin": body.linkedin,
        "github": body.github,
        "portfolio": body.portfolio,
        "desired_position": body.desired_position,
        "specialization": body.specialization,
        "level": body.level,
        "salary_from": body.salary_from,
        "salary_to": body.salary_to,
        "employment_type": body.employment_type,
        "work_format": body.work_format,
        "relocation_ready": body.relocation_ready,
    }

    if profile:
        profile.full_name = body.full_name
        profile.skills = body.skills
        profile.experience = body.experience
        if body.resume_url:
            profile.resume_url = body.resume_url
        for k, v in extended.items():
            if v is not None:
                setattr(profile, k, v)
    else:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=body.full_name,
            skills=body.skills,
            experience=body.experience,
            resume_url=body.resume_url,
            **{k: v for k, v in extended.items() if v is not None},
        )
        db.add(profile)

    await db.commit()
    await db.refresh(profile)
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        skills=profile.skills,
        experience=profile.experience,
        resume_url=profile.resume_url,
        email=current_user.email,
        phone=profile.phone,
        city=profile.city,
        citizenship=profile.citizenship,
        birth_date=profile.birth_date,
        linkedin=profile.linkedin,
        github=profile.github,
        portfolio=profile.portfolio,
        desired_position=profile.desired_position,
        specialization=profile.specialization,
        level=profile.level,
        salary_from=profile.salary_from,
        salary_to=profile.salary_to,
        employment_type=profile.employment_type,
        work_format=profile.work_format,
        relocation_ready=profile.relocation_ready,
    )


@router.post("/ai/enhance", response_model=ResumeAIResponse)
async def ai_enhance_resume(
    body: ResumeEnhanceRequest,
    current_user: User = Depends(require_role("candidate")),
):
    await asyncio.sleep(2) # Mock processing time
    
    base_skills = body.current_skills or ""
    base_exp = body.current_experience or ""
    
    # Mock enhancement
    enhanced_skills = f"{base_skills}, ИИ-оптимизация, Cloud Native, Быстрая адаптация, Системное мышление" if base_skills else "ИИ-оптимизация, Структурированный подход, Кросс-функциональное взаимодействие"
    enhanced_exp = f"{base_exp}\n\n[Улучшено ИИ]: Оптимизировал рабочие процессы, повысил эффективность коммуникации в команде на 20%. Успешно применял современные практики ведения проектов." if base_exp else "[Сгенерировано ИИ]: Успешный опыт решения сложных задач, ориентация на результат, проактивная позиция."
    
    return ResumeAIResponse(
        enhanced_skills=enhanced_skills.strip().strip(", "),
        enhanced_experience=enhanced_exp.strip()
    )


@router.post("/ai/generate", response_model=ResumeAIResponse)
async def ai_generate_resume(
    body: ResumeGenerateRequest,
    current_user: User = Depends(require_role("candidate")),
):
    await asyncio.sleep(3) # Mock processing time
    
    # Extract answers based on the 3 planned questions
    job_title = body.answers[0] if len(body.answers) > 0 else "Специалист"
    past_exp = body.answers[1] if len(body.answers) > 1 else ""
    skills = body.answers[2] if len(body.answers) > 2 else ""
    
    enhanced_skills = f"{skills}, Agile, Работа в команде, Инициативность, Аналитическое мышление" if skills else "Agile, Работа в команде, Инициативность, Аналитическое мышление"
    enhanced_exp = f"Претендую на позицию: {job_title}\n\n[Предыдущий опыт]: {past_exp}\n\n[Достижения, сгенерированные ИИ]:\n- Эффективно решал поставленные задачи.\n- Быстро осваивал новые технологии.\n- Демонстрировал высокую вовлеченность в проекты."
    
    return ResumeAIResponse(
        enhanced_skills=enhanced_skills.strip().strip(", "),
        enhanced_experience=enhanced_exp.strip()
    )


@router.post("/ai/generate-stream")
async def ai_generate_stream(
    body: ResumeGenerateRequest,
    current_user: User = Depends(require_role("candidate")),
):
    job_title = body.answers[0] if len(body.answers) > 0 else ""
    past_exp = body.answers[1] if len(body.answers) > 1 else ""
    skills = body.answers[2] if len(body.answers) > 2 else ""
    vacancy_text = body.answers[3] if len(body.answers) > 3 else ""
    
    vacancy_instruction = ""
    if vacancy_text.strip():
        vacancy_instruction = f"\n\nКандидат откликается на конкретную вакансию. ОЧЕНЬ ВАЖНО использовать релевантные ключевые слова, синонимы и требования из описания этой вакансии, чтобы успешно пройти фильтр ATS (Applicant Tracking System).\nОписание вакансии:\n{vacancy_text}\n"

    prompt = f"""
Ты — профессиональный HR-эксперт. Твоя задача — создать идеальное, убедительное резюме (CV) на основе ответов кандидата.{vacancy_instruction}
ОЧЕНЬ ВАЖНО: НИКАКИХ ВСТУПИТЕЛЬНЫХ ИЛИ ЗАКЛЮЧИТЕЛЬНЫХ СЛОВ! ВЕРНИ ТОЛЬКО ИТОГОВЫЙ ТЕКСТ В MARKDOWN.
СТРОГО ИСПОЛЬЗУЙ СЛЕДУЮЩИЙ ФОРМАТ MARKDOWN: Начинай строго с символа `#` и дальше текст резюме.

Email кандидата: {current_user.email} (Сделай заголовок H1: Имя из email)
Желаемая должность: {job_title}

Прошлый опыт работы (если есть, улучши его и добавь метрики): {past_exp}
Ключевые навыки: {skills}

Структура Markdown должна быть строго такой:
# Имя и Фамилия
## Должность
Москва • +7 999 123-45-67 • {current_user.email} • GitHub: @кандидат

### Обо мне
(Напиши убедительный текст из 3-4 сильных предложений, описывающих профессиональный профиль без воды)

### Опыт работы
**Название Компании, Роль** *Месяц Год - Месяц Год*
- Выдели конкретные достижения маркированным списком 
- Обязательно используй цифры и метрики (ускорил на 20%, оптимизировал работу)

### Навыки
- Раздели навыки по категориям (Языки, Фреймворки, Базы данных)

### Образование
**Название ВУЗа, Специальность** *Сентябрь 2018 - Июнь 2022*
- Бакалавриат / Магистратура
"""

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        async def fallback_stream():
            yield "Ключ Gemini API не настроен в Backend.".encode("utf-8")
        return StreamingResponse(fallback_stream(), media_type="text/plain")

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    try:
        response = await model.generate_content_async(prompt, stream=True)
    except Exception as e:
        error_msg = str(e)
        if "User location" in error_msg:
             error_msg = "Google Gemini заблокирован в вашем регионе. Включите VPN для Docker-контейнера сервера!"
        async def fallback_stream():
             yield str(f"\n\n**[Ошибка API ИИ]** Генерация прервана: {error_msg}").encode("utf-8")
        return StreamingResponse(fallback_stream(), media_type="text/plain")

    async def generate_chunks():
        try:
            async for chunk in response:
                if chunk.text:
                    yield chunk.text.encode("utf-8")
        except Exception as e:
            yield str(f"\n\n**[Ошибка ИИ]** Генерация прервана: {e}").encode("utf-8")

    return StreamingResponse(generate_chunks(), media_type="text/plain")


@router.post("/ai/enhance-stream")
async def ai_enhance_stream(
    body: ResumeEnhanceStreamRequest,
    current_user: User = Depends(require_role("candidate")),
):
    prompt = f"""
Ты — профессиональный HR-эксперт. Пользователь хочет внести изменения в своё текущее резюме формата Markdown.
ОЧЕНЬ ВАЖНО: НИКАКИХ ВСТУПИТЕЛЬНЫХ ИЛИ ЗАКЛЮЧИТЕЛЬНЫХ СЛОВ! ВЕРНИ ТОЛЬКО ИТОГОВЫЙ ОБНОВЛЕННЫЙ ТЕКСТ В MARKDOWN.
Сохраняй структуру А4 и стили.

Текущее резюме:
{body.current_content}

Требование пользователя (что изменить/улучшить):
{body.prompt}
"""

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        async def fallback_stream_enhance():
            yield body.current_content.encode("utf-8")
            yield "\n*(API ключ не настроен)*".encode("utf-8")
        return StreamingResponse(fallback_stream_enhance(), media_type="text/plain")

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    try:
        response = await model.generate_content_async(prompt, stream=True)
    except Exception as e:
        error_msg = str(e)
        if "User location" in error_msg:
             error_msg = "Google Gemini заблокирован в вашем регионе. Включите VPN для Docker-контейнера сервера!"
        async def fallback_stream2():
             yield str(f"\n\n**[Ошибка API ИИ]** Обновление прервано: {error_msg}").encode("utf-8")
        return StreamingResponse(fallback_stream2(), media_type="text/plain")

    async def generate_chunks():
        try:
            async for chunk in response:
                if chunk.text:
                    yield chunk.text.encode("utf-8")
        except Exception as e:
            yield str(f"\n\n**[Ошибка ИИ]** Обновление прервано: {e}").encode("utf-8")

    return StreamingResponse(generate_chunks(), media_type="text/plain")


@router.get("/ai/draft", response_model=DraftResponse)
async def get_draft(
    current_user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        return DraftResponse(content=None)
        
    return DraftResponse(content=profile.ai_resume_draft)

@router.post("/ai/save-draft")
async def save_draft(
    body: DraftSaveRequest,
    current_user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=current_user.email.split("@")[0],
            ai_resume_draft=body.content
        )
        db.add(profile)
    else:
        profile.ai_resume_draft = body.content
        
    await db.commit()
    return {"status": "ok"}
