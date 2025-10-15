import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from deep_translator import GoogleTranslator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, lang: str = 'hi'):
    await websocket.accept()
    logger.info(f"WebSocket connection established for target language: {lang}")
    
    try:
        while True:
            data = await websocket.receive_json()
            text_to_translate = data.get("text")

            if text_to_translate:
                logger.info(f"Received text: '{text_to_translate}' for translation to '{lang}'")
                try:
                    # Use deep-translator's GoogleTranslator
                    translated_text = GoogleTranslator(source='auto', target=lang).translate(text_to_translate)
                    
                    logger.info(f"Translated text: '{translated_text}'")
                    await websocket.send_json({
                        "original": text_to_translate,
                        "translated": translated_text
                    })
                except Exception as e:
                    logger.error(f"Translation failed: {e}")
                    await websocket.send_json({"error": "Translation failed."})
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the websocket: {e}")

