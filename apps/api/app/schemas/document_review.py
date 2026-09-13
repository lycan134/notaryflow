from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentReviewCreate(BaseModel):
    document_id: int
    reviewed_by_user_id: int
    result: str
    notes: str | None = None


class DocumentReviewResponse(BaseModel):
    id: int
    law_office_id: int
    document_id: int
    reviewed_by_user_id: int
    result: str
    notes: str | None
    reviewed_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)