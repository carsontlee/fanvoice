import os
from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import ElevenLabs

# el_client is the new client from 'elevenlabs.client'
global_el_client = None 

def initialize_elevenlabs(api_key):
    global global_el_client
    try:
        global_el_client = ElevenLabs(api_key=api_key)
        if not global_el_client:
            print("Error: ElevenLabs client (ElevenLabs) initialization failed to create a client object.")
    except Exception as e:
        print(f"Error during ElevenLabs client (ElevenLabs) initialization: {e}")
        global_el_client = None # Ensure client is None if initialization fails

def clone_voice(file_path, voice_name, api_key):
    """
    Clones a voice from an audio file using ElevenLabs API.
    Args:
        file_path (str): The path to the audio file for cloning.
        voice_name (str): The desired name for the cloned voice.
        api_key (str): The ElevenLabs API key.
    Returns:
        str: The voice ID of the cloned voice, or None if cloning failed.
    """
    global global_el_client
    if not global_el_client: # Check if client is initialized
        initialize_elevenlabs(api_key)
    
    if not global_el_client: # Check again after attempting initialization
        print("Error: ElevenLabs client (ElevenLabs) not initialized for clone_voice.")
        return None

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    try:
        # Corrected: Use global_el_client.clone directly, not global_el_client.voices.clone
        voice = global_el_client.clone(
            name=voice_name,
            description="Cloned voice for FanVoiceApp", # Optional description
            files=[file_path],
        )
        print(f"Voice cloned successfully. Voice ID: {voice.voice_id}")
        return voice.voice_id
    except Exception as e:
        print(f"Error cloning voice: {e}")
        return None

def text_to_speech(text, voice_id, api_key, output_path="generated_audio.mp3"):
    """
    Generates speech from text using a specified voice ID with ElevenLabs API.
    Args:
        text (str): The text to convert to speech.
        voice_id (str): The ID of the voice to use.
        api_key (str): The ElevenLabs API key.
        output_path (str): The path to save the generated audio file.
    Returns:
        str: Path to the generated audio file, or None if generation failed.
    """
    global global_el_client
    if not global_el_client: # Check if client is initialized
        initialize_elevenlabs(api_key)

    if not global_el_client: # Check again after attempting initialization
        print("Error: ElevenLabs client (ElevenLabs) not initialized for text_to_speech.")
        return None
    
    try:
        audio_stream = global_el_client.generate(
            text=text,
            voice=Voice(
                voice_id=voice_id,
                # settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True) # Example settings
            ),
            # model="eleven_multilingual_v2" # Or other models as needed
        )
        
        with open(output_path, "wb") as f:
            for chunk in audio_stream: # Iterate over the generator
                if chunk:
                    f.write(chunk)
        print(f"Audio generated successfully and saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

