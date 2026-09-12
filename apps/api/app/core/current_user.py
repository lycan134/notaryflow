from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


def get_current_user(
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, settings.development_user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Development user is not available.",
        )

    return user
