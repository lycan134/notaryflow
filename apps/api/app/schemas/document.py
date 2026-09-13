from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    transaction_id: int
    uploaded_by_user_id: int
    filename: str
    document_type: str
    status: str = "UPLOADED"
    storage_key: str


class DocumentResponse(BaseModel):
    id: int
    law_office_id: int
    transaction_id: int
    uploaded_by_user_id: int
    filename: str
    document_type: str
    status: str
    storage_key: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
