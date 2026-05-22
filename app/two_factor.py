import hashlib
import random
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import TwoFactorChallenge, User


TWO_FACTOR_CODE_TTL_MINUTES = 10
TWO_FACTOR_MAX_ATTEMPTS = 5


def generate_two_factor_code() -> str:
    return f"{random.randint(100000, 999999)}"


def hash_two_factor_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def verify_two_factor_code(raw_code: str, code_hash: str) -> bool:
    return hash_two_factor_code(raw_code.strip()) == code_hash


def mask_email(email: str) -> str:
    if "@" not in email:
        return "***"

    local, domain = email.split("@", 1)

    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[:2] + "***"

    return f"{masked_local}@{domain}"


def mask_phone(phone: str | None) -> str:
    if not phone:
        return "—"

    cleaned = phone.strip()

    if len(cleaned) <= 4:
        return "***"

    return f"{cleaned[:2]}***{cleaned[-2:]}"


def create_two_factor_challenge(
    db: Session,
    user: User,
    method: str = "email",
) -> tuple[TwoFactorChallenge, str]:
    if method != "email":
        raise HTTPException(
            status_code=400,
            detail="Only email 2FA is available now",
        )

    code = generate_two_factor_code()

    challenge = TwoFactorChallenge(
        user_id=user.id,
        method="email",
        destination=user.email,
        code_hash=hash_two_factor_code(code),
        is_used=False,
        attempts_count=0,
        expires_at=datetime.utcnow()
        + timedelta(minutes=TWO_FACTOR_CODE_TTL_MINUTES),
    )

    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return challenge, code


def send_two_factor_email(email: str, code: str) -> None:
    """
    Для локальной разработки код просто печатается в консоль.
    Позже можно подключить SMTP через env.
    """
    print(f"[2FA] Email code for {email}: {code}")


def validate_two_factor_challenge(
    db: Session,
    challenge_id: int,
    code: str,
) -> User:
    challenge = (
        db.query(TwoFactorChallenge)
        .filter(TwoFactorChallenge.id == challenge_id)
        .first()
    )

    if not challenge:
        raise HTTPException(status_code=404, detail="2FA challenge not found")

    if challenge.is_used:
        raise HTTPException(status_code=400, detail="2FA challenge already used")

    if challenge.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="2FA code expired")

    if challenge.attempts_count >= TWO_FACTOR_MAX_ATTEMPTS:
        raise HTTPException(status_code=400, detail="Too many 2FA attempts")

    challenge.attempts_count += 1

    if not verify_two_factor_code(code, challenge.code_hash):
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid 2FA code")

    challenge.is_used = True
    challenge.used_at = datetime.utcnow()

    user = db.query(User).filter(User.id == challenge.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.commit()

    return user
