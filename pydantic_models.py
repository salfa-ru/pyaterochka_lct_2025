from pydantic import BaseModel


class PredictIn(BaseModel):
    input: str

class SpanOut(BaseModel):
    start_index: int
    end_index: int
    entity: str

class ChatRequest(BaseModel):
    message: str
    history: list[str] = []
