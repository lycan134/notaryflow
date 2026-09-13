from pydantic import BaseModel, ConfigDict


class DocumentStatusTransition(BaseModel):
    new_status: str

    model_config = ConfigDict(extra="forbid")
