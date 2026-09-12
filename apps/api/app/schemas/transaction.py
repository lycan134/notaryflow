from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    client_id: int
    reference_number: str | None = None
    transaction_type: str
    status: str = "DRAFT"
    title: str
    description: str | None = None
    date_received: date
    date_completed: date | None = None


class TransactionUpdate(BaseModel):
    reference_number: str | None = None
    transaction_type: str
    status: str
    title: str
    description: str | None = None
    date_received: date
    date_completed: date | None = None


class TransactionResponse(BaseModel):
    id: int
    law_office_id: int
    client_id: int
    reference_number: str | None
    transaction_type: str
    status: str
    title: str
    description: str | None
    date_received: date
    date_completed: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
