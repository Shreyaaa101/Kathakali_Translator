from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chunks = ["Hello", " world!", " How", " are", " you?"]
    for chunk in chunks:
        await asyncio.sleep(1)
        await websocket.send_text(chunk)
    await websocket.close()
