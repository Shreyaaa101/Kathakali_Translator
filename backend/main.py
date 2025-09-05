from fastapi import FastAPI, WebSocket
from deep_translator import GoogleTranslator

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "WebSocket server is running at /ws/translate"}

@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    translator = GoogleTranslator(source="en", target="hi")  # English → Hindi

    while True:
        try:
            # 1. Receive message from frontend
            text = await websocket.receive_text()
            print(f"Received from frontend: {text}")

            # 2. Translate text
            translated = translator.translate(text)

            # 3. Send translated text back
            await websocket.send_text(translated)

        except Exception as e:
            print("Connection closed:", e)
            break
