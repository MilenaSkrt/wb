from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
import os
import json
import datetime

app = FastAPI()

# Модель для создания заметки
class NoteCreateResponse(BaseModel):
    id: int

# Модель для получения информации о заметке
class NoteInfoResponse(BaseModel):
    created_at: str
    updated_at: str

# Модель для получения текста заметки
class NoteTextResponse(BaseModel):
    id: int
    text: str

# Модель для получения списка заметок
class NotesListResponse(BaseModel):
    notes: List[int]

# Путь к директории для хранения заметок
NOTES_DIR = "notes"
TOKENS_FILE = "tokens.txt"

# Убедимся, что директория для заметок существует
os.makedirs(NOTES_DIR, exist_ok=True)

# Функция для проверки токена
def verify_token(token: str):
    if not os.path.exists(TOKENS_FILE):
        raise HTTPException(status_code=401, detail="Unauthorized")
    with open(TOKENS_FILE, "r") as f:
        valid_tokens = f.read().splitlines()
    if token not in valid_tokens:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Создание заметки
@app.post("/notes/", response_model=NoteCreateResponse)
def create_note(text: str, token: str = Depends(verify_token)):
    note_id = len(os.listdir(NOTES_DIR)) + 1  # Генерация ID на основе количества файлов
    created_at = datetime.datetime.now().isoformat()
    note_data = {
        "text": text,
        "created_at": created_at,
        "updated_at": created_at
    }
    with open(os.path.join(NOTES_DIR, f"note_{note_id}.json"), "w") as f:
        json.dump(note_data, f)
    return NoteCreateResponse(id=note_id)

# Получение текста заметки
@app.get("/notes/{note_id}", response_model=NoteTextResponse)
def get_note_text(note_id: int, token: str = Depends(verify_token)):
    note_file = os.path.join(NOTES_DIR, f"note_{note_id}.json")
    if not os.path.exists(note_file):
        raise HTTPException(status_code=404, detail="Note not found")
    with open(note_file) as f:
        note_data = json.load(f)
    return NoteTextResponse(id=note_id, text=note_data["text"])

# Получение информации о заметке
@app.get("/notes/{note_id}/info", response_model=NoteInfoResponse)
def get_note_info(note_id: int, token: str = Depends(verify_token)):
    note_file = os.path.join(NOTES_DIR, f"note_{note_id}.json")
    if not os.path.exists(note_file):
        raise HTTPException(status_code=404, detail="Note not found")
    with open(note_file) as f:
        note_data = json.load(f)
    return NoteInfoResponse(
        created_at=note_data["created_at"],
        updated_at=note_data["updated_at"]
    )

# Обновление текста заметки
@app.patch("/notes/{note_id}")
def update_note(note_id: int, text: str, token: str = Depends(verify_token)):
    note_file = os.path.join(NOTES_DIR, f"note_{note_id}.json")
    if not os.path.exists(note_file):
        raise HTTPException(status_code=404, detail="Note not found")
    with open(note_file) as f:
        note_data = json.load(f)
    note_data["text"] = text
    note_data["updated_at"] = datetime.datetime.now().isoformat()
    with open(note_file, "w") as f:
        json.dump(note_data, f)
    return {"message": "Note updated successfully"}

# Удаление заметки
@app.delete("/notes/{note_id}")
def delete_note(note_id: int, token: str = Depends(verify_token)):
    note_file = os.path.join(NOTES_DIR, f"note_{note_id}.json")
    if not os.path.exists(note_file):
        raise HTTPException(status_code=404, detail="Note not found")
    os.remove(note_file)
    return {"message": "Note deleted successfully"}

# Получение списка ID заметок
@app.get("/notes/", response_model=NotesListResponse)
def list_notes(token: str = Depends(verify_token)):
    note_ids = [int(note_file.split("_")[1].split(".")[0]) for note_file in os.listdir(NOTES_DIR)]
    return NotesListResponse(notes=note_ids)
