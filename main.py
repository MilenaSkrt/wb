from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Модели ответов
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class ResponseModel(BaseModel):
    success: bool
    data: List[Item]

class ErrorResponseModel(BaseModel):
    success: bool
    error: str

# Пример эндпоинта
@app.get("/items/", response_model=ResponseModel)
async def get_items():
    items = [
        Item(id=1, name="Item One", description="This is item one."),
        Item(id=2, name="Item Two"),
    ]
    return ResponseModel(success=True, data=items)

@app.get("/error/", response_model=ErrorResponseModel)
async def get_error():
    return ErrorResponseModel(success=False, error="An error occurred.")

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)