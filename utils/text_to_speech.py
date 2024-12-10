import os
from elevenlabs import play
from elevenlabs.client import ElevenLabs

# ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs()

def audio_gen(text, voice="Brian"):
    """
    Convert text to speech using ElevenLabs SDK and play the audio.

    Args:
        text (str): The text to convert to speech.
        voice (str): The voice to use. Default is "Brian".
        model (str): The model to use. Default is "eleven_multilingual_v2".
    """
    try:
        audio = client.generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2",
        )

        play(audio)
    except Exception as e:
        print(f"Exception occurred while generating speech: {e}")
