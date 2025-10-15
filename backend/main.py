import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from googletrans import Translator

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="वादAnuवाद - Translation Service",
    description="A simple WebSocket server for real-time text translation using Google Translate.",
    version="2.0.0"
)

translator = Translator()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, lang: str = 'hi'):
    """
    WebSocket endpoint for real-time translation.
    Receives text, translates it to the target language, and sends it back.
    - **lang**: Target language code (e.g., 'hi' for Hindi).
    """
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for target language: {lang}")
    
    try:
        while True:
            # Receive JSON data from the client, expecting a text field
            data = await websocket.receive_json()
            text_to_translate = data.get("text")

            if not text_to_translate:
                logger.warning("Received empty text. Awaiting next message.")
                continue

            logger.info(f"Received text: '{text_to_translate}' for translation to '{lang}'")

            try:
                # --- Translation Logic ---
                translated = translator.translate(text_to_translate, dest=lang)
                response = {
                    "original": text_to_translate,
                    "translated": translated.text
                }
                logger.info(f"Successfully translated to: '{translated.text}'")
                
                # Send the translated data back to the client
                await websocket.send_json(response)

            except Exception as e:
                logger.error(f"Translation failed for '{text_to_translate}': {e}", exc_info=True)
                await websocket.send_json({"error": f"Translation failed: {e}"})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the WebSocket connection: {e}", exc_info=True)
        # good practice to ensure the socket is closed if an unhandled error occurs.
        # Although FastAPI handles this, being explicit can prevent hanging connections.
        if not websocket.client_state == 'DISCONNECTED':
             await websocket.close()

