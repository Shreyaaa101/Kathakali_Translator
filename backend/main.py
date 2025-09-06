from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Read transcript
    with open("transcript.txt", "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    # Stream words slowly and smoothly
    for line in lines:
        words = line.split()
        current_text = ""
        for word in words:
            current_text += word + " "
            await websocket.send_text(current_text.strip())
            await asyncio.sleep(0.8)  # cinematic word-by-word timing

        await asyncio.sleep(1.5)      # pause at sentence end
        await websocket.send_text("")  # clear for next sentence
