from pydantic import BaseModel


class ChatPostDto(BaseModel):
    prompt: str


class ChangeIdDto(BaseModel):
    user_identifier: str
