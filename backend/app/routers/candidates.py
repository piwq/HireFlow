from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import os
import io
import json
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


from app.models.application import Application
from app.models.interview import Interview

@router.get("/", response_model=list[ProfileResponse])
async def list_candidates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("hr", "manager", "admin")),
    q: str | None = None,
    skills: str | None = None,
    city: str | None = None,
    min_salary: int | None = None,
    max_salary: int | None = None,
    work_format: str | None = None,
    employment_type: str | None = None,
    desired_position: str | None = None,
    level: str | None = None,
):
    stmt = select(CandidateProfile).options(selectinload(CandidateProfile.user))
    
    if current_user.role == "manager":
        # Managers only see candidates assigned to them for interviews
        stmt = stmt.join(CandidateProfile.applications).join(Application.interview).where(Interview.manager_id == current_user.id)
        
    if q:
        stmt = stmt.where(CandidateProfile.full_name.ilike(f"%{q}%"))
    if skills:
        stmt = stmt.where(CandidateProfile.skills.ilike(f"%{skills}%"))
    if city:
        stmt = stmt.where(CandidateProfile.city.ilike(f"%{city}%"))
    if min_salary is not None:
        stmt = stmt.where(CandidateProfile.salary_from >= min_salary)
    if max_salary is not None:
        stmt = stmt.where(CandidateProfile.salary_to <= max_salary)
    if work_format:
        stmt = stmt.where(CandidateProfile.work_format.ilike(f"%{work_format}%"))
    if employment_type:
        stmt = stmt.where(CandidateProfile.employment_type.ilike(f"%{employment_type}%"))
    if desired_position:
        stmt = stmt.where(CandidateProfile.desired_position.ilike(f"%{desired_position}%"))
    if level:
        stmt = stmt.where(CandidateProfile.level.ilike(f"%{level}%"))
    
    result = await db.execute(stmt)
    profiles = result.scalars().unique().all()
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
            photo_url=p.photo_url,
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
        photo_url=profile.photo_url,
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
        "photo_url": body.photo_url,
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

# --- AI Resilient Fallback Logic ---
MODELS_TO_TRY = ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

async def run_genai_with_fallback(prompt, stream=False, **kwargs):
    last_err = Exception("All AI models failed")
    for name in MODELS_TO_TRY:
        try:
            # Префикс models/ часто помогает избежать 404 в v1beta
            full_name = f"models/{name}" if not name.startswith("models/") else name
            model = genai.GenerativeModel(full_name)
            
            if stream:
                res = await model.generate_content_async(prompt, stream=True, **kwargs)
            else:
                res = await model.generate_content_async(prompt, **kwargs)
            
            return res, name
        except Exception as e:
            last_err = e
            print(f"DEBUG: AI Model {name} failed: {str(e)}", flush=True)
            continue
            
    # Если мы дошли сюда, значит всё упало
    raise Exception(f"Ни одна из моделей ({', '.join(MODELS_TO_TRY)}) не ответила. Последняя ошибка: {str(last_err)}")

def format_profile_context(profile: CandidateProfile) -> str:
    """Helper to convert structured profile data into a string for LLM prompt."""
    if not profile:
        return ""
    
    context = f"ФИО: {profile.full_name or 'Не указано'}\n"
    context += f"Желаемая позиция в профиле: {profile.desired_position or 'Не указано'}\n"
    context += f"Навыки из профиля: {profile.skills or 'Не указано'}\n"
    
    if profile.work_experiences:
        context += "\nОПЫТ РАБОТЫ (из профиля):\n"
        for we in profile.work_experiences:
            context += f"- {we.company} ({we.position}): {we.period}\n  Обязанности: {we.responsibilities}\n"
    
    if profile.educations:
        context += "\nОБРАЗОВАНИЕ (из профиля):\n"
        for edu in profile.educations:
            context += f"- {edu.institution} ({edu.degree}, {edu.specialization}): {edu.year}\n"
    
    if profile.projects:
        context += "\nПРОЕКТЫ И СЕРТИФИКАТЫ:\n"
        for proj in profile.projects:
            context += f"- {proj.name}: {proj.description}\n"
    
    return context


@router.post("/ai/generate-stream")
async def ai_generate_stream(
    body: ResumeGenerateRequest,
    current_user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    job_title = body.answers[0] if len(body.answers) > 0 else ""
    
    # Fetch profile with relationships
    stmt = (
        select(CandidateProfile)
        .where(CandidateProfile.user_id == current_user.id)
        .options(
            selectinload(CandidateProfile.work_experiences),
            selectinload(CandidateProfile.educations),
            selectinload(CandidateProfile.languages),
            selectinload(CandidateProfile.projects),
        )
    )
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    profile_context = format_profile_context(profile)

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

Email кандидата: {current_user.email} (Сделай заголовок H1: {profile.full_name if profile and profile.full_name else 'Имя Кандидата'})
Желаемая должность (цель): {job_title}

ДАННЫЕ ИЗ ПРОФИЛЯ КАНДИДАТА (Основные факты):
{profile_context}

ДОПОЛНИТЕЛЬНЫЕ ОТВЕТЫ КАНДИДАТА (Для акцентов):
Прошлый опыт (акценты): {past_exp}
Ключевые навыки (приоритет): {skills}

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
    
    try:
        response, used_model = await run_genai_with_fallback(prompt, stream=True)
    except Exception as e:
        error_msg = str(e)
        if "User location" in error_msg:
             error_msg = "Google Gemini заблокирован в вашем регионе. Включите VPN для Docker-контейнера сервера!"
        async def fallback_stream_err():
             yield str(f"\n\n**[Ошибка API ИИ]** Генерация прервана: {error_msg}").encode("utf-8")
        return StreamingResponse(fallback_stream_err(), media_type="text/plain")

    async def generate_chunks():
        try:
            async for chunk in response:
                if chunk.text:
                    yield chunk.text.encode("utf-8")
        except Exception as e:
            yield str(f"\n\n**[Ошибка ИИ]** ({used_model}): {e}").encode("utf-8")

    return StreamingResponse(generate_chunks(), media_type="text/plain")


@router.post("/ai/enhance-stream")
async def ai_enhance_stream(
    body: ResumeEnhanceStreamRequest,
    current_user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    # Fetch profile context for better enhancements
    stmt = (
        select(CandidateProfile)
        .where(CandidateProfile.user_id == current_user.id)
        .options(
            selectinload(CandidateProfile.work_experiences),
            selectinload(CandidateProfile.educations),
            selectinload(CandidateProfile.languages),
            selectinload(CandidateProfile.projects),
        )
    )
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    profile_context = format_profile_context(profile)

    prompt = f"""
Ты — профессиональный HR-эксперт. Пользователь хочет внести изменения в своё текущее резюме формата Markdown.
ОЧЕНЬ ВАЖНО: НИКАКИХ ВСТУПИТЕЛЬНЫХ ИЛИ ЗАКЛЮЧИТЕЛЬНЫХ СЛОВ! ВЕРНИ ТОЛЬКО ИТОГОВЫЙ ОБНОВЛЕННЫЙ ТЕКСТ В MARKDOWN.
Сохраняй структуру А4 и стили.

КОНТЕКСТ ПРОФИЛЯ КАНДИДАТА (Для справки о фактах):
{profile_context}

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
    
    try:
        response, used_model = await run_genai_with_fallback(prompt, stream=True)
    except Exception as e:
        error_msg = str(e)
        if "User location" in error_msg:
             error_msg = "Google Gemini заблокирован в вашем регионе. Включите VPN для Docker-контейнера сервера!"
        async def fallback_stream_err2():
             yield str(f"\n\n**[Ошибка API ИИ]** Обновление прервано: {error_msg}").encode("utf-8")
        return StreamingResponse(fallback_stream_err2(), media_type="text/plain")

    async def generate_chunks():
        try:
            async for chunk in response:
                if chunk.text:
                    yield chunk.text.encode("utf-8")
        except Exception as e:
            yield str(f"\n\n**[Ошибка ИИ]** ({used_model}): {e}").encode("utf-8")

    return StreamingResponse(generate_chunks(), media_type="text/plain")


class SuggestRequest(BaseModel):
    field: str
    context: str | None = None


@router.post("/ai/suggest")
async def suggest_field(
    body: SuggestRequest,
    current_user: User = Depends(require_role("candidate"))
):
    """Generate a single professional suggestion for a profile field."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return {"suggestion": "ИИ-подсказки временно недоступны (нет ключа)"}

    genai.configure(api_key=gemini_key)

    system_prompt = (
        "Ты — профессиональный HR-консультант. "
        "Пользователь заполняет профиль и прислал черновик поля. "
        "Напиши один короткий, профессиональный и впечатляющий вариант заполнения этого поля на русском языке. "
        "Не используй кавычки, вступления и пояснения. Только сам текст для поля."
    )
    
    prompt = f"Поле: {body.field}\nЧерновик пользователя: {body.context or 'пусто'}\nКонтекст: Вакансия в IT."
    
    try:
        items = [{"role": "user", "parts": [system_prompt, prompt]}]
        response, used_model = await run_genai_with_fallback(items)
        return {"suggestion": response.text.strip().replace('"', ''), "model": used_model}
    except Exception as e:
        return {"suggestion": f"Ошибка ИИ: {str(e)}"}

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

@router.post("/parse-gosuslugi")
async def parse_gosuslugi_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db)
):
    """
    Парсит PDF-выписку из трудовой книжки (Госуслуги) с помощью ИИ.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        genai.configure(api_key=gemini_key)
        
    # Валидация размера файла (10 МБ)
    MAX_SIZE = 10 * 1024 * 1024
    size = getattr(file, "size", None)
    if size is None:
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
    
    if size > MAX_SIZE:
        raise HTTPException(status_code=413, detail=f"PDF файл слишком большой ({size / 1024 / 1024:.1f} МБ). Максимум: 10 МБ")

    try:
        import pdfplumber
        content = await file.read()
        pdf_text = ""
        
        # Экстракция текста с сохранением макета (важно для таблиц)
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                pdf_text += page.extract_text(layout=True) or ""
        
        if not pdf_text.strip():
            return {"error": "Не удалось извлечь текст из PDF. Возможно, файл пуст или защищен."}

        system_prompt = (
            "Ты — профессиональный ИИ-ассистент, специализирующийся на анализе российских кадровых документов. "
            "Твоя задача — проанализировать текст выписки из электронной трудовой книжки (Госуслуги) и извлечь историю работы. "
            "Ты должен вернуть ТОЛЬКО чистый JSON-массив объектов опыта работы."
        )
        
        prompt = (
            "Проанализируй текст и извлеки последовательность записей 'ПРИЕМ', 'ПЕРЕВОД', 'УВОЛЬНЕНИЕ'. "
            "Сгруппируй их по работодателю. Если был ПРИЕМ и потом УВОЛЬНЕНИЕ у одного работодателя — это один период. "
            "Если был ПЕРЕВОД, используй последнюю должность в этом периоде.\n\n"
            "Структура JSON-объекта в массиве:\n"
            "{\n"
            "  \"company\": \"Название работодателя (без лишних ОГРН/ИНН)\",\n"
            "  \"position\": \"Должность\",\n"
            "  \"period\": \"ДД.ММ.ГГГГ — ДД.ММ.ГГГГ\" (или 'Настоящее время', если нет записи об увольнении),\n"
            "  \"responsibilities\": \"Сформулируй 3-4 предложения описывающих типичные обязанности и достижения для этой роли.\"\n"
            "}\n\n"
            "Текст выписки:\n"
            f"{pdf_text[:12000]}"
        )
        
        items = [{"role": "user", "parts": [system_prompt, prompt]}]
        response, used_model = await run_genai_with_fallback(items)
        
        # Очистка ответа от Markdown-обертки
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            # Удаляем первую и последнюю строки с ```
            lines = clean_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_text = "\n".join(lines).strip()
            if clean_text.startswith("json"):
                clean_text = clean_text[4:].strip()
        
        try:
            experiences_raw = json.loads(clean_text)
            
            # Достаем ID профиля
            stmt = select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
            res = await db.execute(stmt)
            profile = res.scalar_one_or_none()
            if not profile:
                return {"error": "Профиль не найден"}

            # Сохраняем в базу пакетно
            from app.models.work_experience import WorkExperience
            saved_items = []
            for exp in experiences_raw:
                new_we = WorkExperience(
                    candidate_id=profile.id,
                    company=exp.get("company", ""),
                    position=exp.get("position", ""),
                    period=exp.get("period", ""),
                    responsibilities=exp.get("responsibilities", "")
                )
                db.add(new_we)
                saved_items.append({
                    "id": 0, # Placeholder, will be updated after commit if needed, 
                    "company": new_we.company,
                    "position": new_we.position,
                    "period": new_we.period,
                    "responsibilities": new_we.responsibilities
                })
            
            await db.commit()
            
            # Обновляем ID в ответе для фронтенда (чтобы можно было сразу редактировать/удалять)
            # Фронтенду лучше перезагрузить список или просто получить объекты с ID
            # Но для скорости мы просто вернем статус "ок" и попросим фронт обновиться
            return {"status": "success", "count": len(saved_items), "model": used_model}
            
        except Exception as json_err:
            return {"error": f"Ошибка обработки JSON от ИИ: {str(json_err)}", "raw_response": clean_text}
            
    except Exception as e:
        return {"error": f"Ошибка сервера при парсинге: {str(e)}"}
