from fastapi import FastAPI, HTTPException, WebSocket, Depends, status
from typing import List, Optional
from datetime import datetime
from .config import get_settings
from .models import Note, NoteCreate
from .services import get_summary
import asyncio
import json

settings = get_settings()


# dummy function to make a note summary with first 5 words.
async def mock_llm_summarize(text: str) -> str:
    await asyncio.sleep(1)  # Simulate API latency
    words = text.split()
    return " ".join(words[:5]) + "..."


app = FastAPI(
    title="Smart Notes API",
    description="A modern note-taking API with real-time updates and AI summaries",
    version="1.0.0"
)

# In-memory storage has been used. later database can be used 
notes_db = []
note_counter = 0
active_connections: List[WebSocket] = []

async def notify_clients(message: dict):
    """Notify all connected clients of updates"""
    for connection in active_connections:
        await connection.send_json(message)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)

@app.post("/notes/", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate):
    global note_counter
    note_counter += 1
    
    # Create new note with generated fields
    new_note = Note(
        id=note_counter,
        created_at=datetime.now(),
        **note.dict()
    )
    
    if not settings.use_mock_llm:
        new_note.summary = await get_summary(note.content)
    else:
        # Use mock summary if OpenAI is not enabled
        new_note.summary = await mock_llm_summarize(note.content)
    
    # Store note
    notes_db.append(new_note)
    
    # Notify websocket clients
    await notify_clients({
        "action": "new_note",
        "note": json.loads(new_note.json())
    })
    
    return new_note





@app.get("/notes/", response_model=List[Note])
async def get_notes(tag: Optional[str] = None):
    if tag:
        return [note for note in notes_db if tag in note.tags]
    return notes_db

@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: int):
    for note in notes_db:
        if note.id == note_id:
            return note
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    for index, note in enumerate(notes_db):
        if note.id == note_id:
            deleted_note = notes_db.pop(index)
            await notify_clients({
                "action": "delete_note",
                "note_id": note_id
            })
            return {"message": "Note deleted successfully"}
    raise HTTPException(status_code=404, detail="Note not found")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": app.version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)