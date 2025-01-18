from fastapi import HTTPException
from pydantic import BaseModel


class RoomValidationException(Exception):
    def __init__(self, error_message: str, status_code: int, data: dict):
        self.error_message = error_message
        self.status_code = status_code
        self.data = data
        super().__init__(self.error_message)

    def to_http_exception(self):
        return HTTPException(status_code=self.status_code, detail={"error_message": self.error_message})


class ErrorResponse(BaseModel):
    error_message: str
    error: str
    data: dict