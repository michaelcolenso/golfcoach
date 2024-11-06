import openai
from flask import current_app as app
import logging

def configure_openai_api():
    openai.api_key = app.config['OPENAI_API_KEY']

def call_openai_api(selected_frames):
    app.logger.info("Calling OpenAI API...")
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "I have provided a number of images from a video of a golf swing. Review each image and determine what element of the golf swing it is. Using your knowledge of golf, provide useful feedback to the golfer as if you were the coach",
                *map(lambda x: {"image": x, "resize": 768}, selected_frames),
            ],
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 2500,
    }

    try:
        result = openai.chat.completions.create(**params)
        app.logger.info("OpenAI API call successful")
        return result
   
    except Exception as e:
        app.logger.error(f"Unexpected error in OpenAI API call: {str(e)}")
        raise