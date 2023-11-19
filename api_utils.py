from flask import current_app as app
import openai
import os
import base64

def configure_openai_api():
    openai.api_key = app.config['OPENAI_API_KEY']

def call_openai_api(thumbnail_image):
    # Convert the thumbnail image to base64
    thumbnail_bytes = thumbnail_image.tobytes()
    thumbnail_base64 = base64.b64encode(thumbnail_bytes).decode("utf-8")

    # Construct the payload with the thumbnail as a base64 encoded image
    app.logger.info("Calling OpenAI API...")
    PROMPT_MESSAGE = {
        "role": "user",
        "content": [
            "I have provided a thumbnail image from a video of a golf swing. Review this image and determine what element of the golf swing it represents. Using your knowledge of golf, provide useful feedback to the golfer as if you were the coach.",
            {"image": thumbnail_base64, "resize": 768},
        ],
    }
    
    params = {
        "model": "gpt-4-vision-preview",
        "messages": [PROMPT_MESSAGE],
        "max_tokens": 500,
    }

    try:
        result = openai.ChatCompletion.create(**params)
        app.logger.info(result)
        return result
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return None
