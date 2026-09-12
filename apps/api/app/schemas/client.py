from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClientCreate(BaseModel):
    full_name: str
    address: str | None = None
    contact_number: str | None = None
    email: str | None = None


class ClientResponse(BaseModel):
    id: int
    law_office_id: int
    full_name: str
    address: str | None
    contact_number: str | None
    email: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)