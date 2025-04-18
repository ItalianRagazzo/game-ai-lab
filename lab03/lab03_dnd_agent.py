from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parents[1]))

from ollama import chat
from util.llm_utils import pretty_stringify_chat, ollama_seed as seed
import pyttsx3
import json
import whisper
import sounddevice as sd
import numpy as np
import wave

# Initialize TTS engine
def initialize_tts():
    engine = pyttsx3.init()
    # Optional: customize voice settings
    engine.setProperty('rate', 150)  # Speed of speech
    voices = engine.getProperty('voices')
    # Choose a voice - typically voice[0] is male, voice[1] is female
    engine.setProperty('voice', voices[0].id)
    return engine

# Text-to-Speech function
def speak(text, engine):
    engine.say(text)
    engine.runAndWait()

# Replace the vosk imports with whisper
import whisper
import sounddevice as sd
import numpy as np
import wave

def listen():
    # Load model - only done once and reused for subsequent calls 
    if not hasattr(listen, "model"):
        listen.model = whisper.load_model("base")
    
    # Record audio
    duration = 5  # seconds
    fs = 16000  # sample rate
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    print("Listening... (speak now)")
    sd.wait()  # Wait until recording is finished
    
    # Convert to format expected by Whisper
    audio_data = recording.flatten().astype(np.float32)
    
    # Transcribe
    result = listen.model.transcribe(audio_data)
    text = result["text"].strip()
    
    if text:
        print(f"You said: {text}")
        return text
    else:
        print("Sorry, I couldn't understand that.")
        return None
# Process special commands
def process_command(command):
    global use_tts, use_stt
    
    if command.lower() == '/tts on':
        use_tts = True
        return "Text-to-speech enabled."
    elif command.lower() == '/tts off':
        use_tts = False
        return "Text-to-speech disabled."
    elif command.lower() == '/stt on':
        use_stt = True
        return "Speech-to-text enabled."
    elif command.lower() == '/stt off':
        use_stt = False
        return "Speech-to-text disabled."
    elif command.lower() == '/voice on':
        use_tts = True
        use_stt = True
        return "Both text-to-speech and speech-to-text enabled."
    elif command.lower() == '/voice off':
        use_tts = False
        use_stt = False
        return "Both text-to-speech and speech-to-text disabled."
    elif command.lower() == '/status':
        return f"TTS: {'enabled' if use_tts else 'disabled'}, STT: {'enabled' if use_stt else 'disabled'}"
    elif command.lower() == '/help':
        return """
Available commands:
/tts on - Enable text-to-speech
/tts off - Disable text-to-speech
/stt on - Enable speech-to-text
/stt off - Disable speech-to-text  
/voice on - Enable both TTS and STT
/voice off - Disable both TTS and STT
/status - Show current settings
/exit - End the session
/help - Show this help message
"""
    else:
        return None  # Not a special command

# Add your code below
sign_your_name = 'Nathan DiGilio'
model = 'deepseek-r1:7b'
options = {'temperature': 0.3, 'max_tokens': 50}
messages = [
    {
        'role': 'system',
        'content': (
            "You are an expert Dungeon Master for a fantasy tabletop role-playing game. Your role is to guide players through an immersive, dynamic, and interactive adventure. "
            "You describe environments vividly, role-play non-player characters (NPCs) with distinct personalities, and adapt to player choices in real time. "
            "Your storytelling is compelling, balancing mystery, danger, and humor while maintaining game mechanics. "
            "You generate encounters, puzzles, and quests that challenge the players and encourage creativity. "
            "When players attempt actions, you fairly determine outcomes based on dice rolls, character abilities, and logical consequences. "
            "Always foster engagement, encourage role-playing, and ensure the experience is fun and immersive."
            "Please use the 5e ruleset for this adventure."
        )
    }
]

# Initialize TTS engine
tts_engine = initialize_tts()

# Configure speech modes - separate toggles for TTS and STT
use_tts = False  # Text-to-speech enabled by default
use_stt = True  # Speech-to-text enabled by default

# Print startup instructions
print("\n=== D&D AI Game Master ===")
print("Type /help for available commands")
print(f"TTS: {'enabled' if use_tts else 'disabled'}, STT: {'enabled' if use_stt else 'disabled'}")

# But before here.
options |= {'seed': seed(sign_your_name)}

# Chat loop
while True:
    response = chat(model=model, messages=messages, stream=False, options=options)
    
    # Print and speak the agent's response
    print(f'Agent: {response.message.content}')
    if use_tts:
        speak(response.message.content, tts_engine)
    
    messages.append({'role': 'assistant', 'content': response.message.content})
    
    # Get user input - either through speech or text
    if use_stt:
        user_input = listen()
        # If speech recognition fails, fall back to text input
        if user_input is None:
            user_input = input('Speech not recognized. Please type: ')
    else:
        user_input = input('You: ')
    
    # Process special commands
    command_response = process_command(user_input)
    if command_response:
        print(command_response)
        continue  # Skip sending command to AI
    
    messages.append({'role': 'user', 'content': user_input})
    
    # Exit command
    if user_input.lower() == '/exit' or user_input.lower() == 'exit':
        break

# Save chat
with open(Path('lab03/attempts.txt'), 'a') as f:
    file_string = ''
    file_string += '-------------------------NEW ATTEMPT-------------------------\n\n\n'
    file_string += f'Model: {model}\n'
    file_string += f'Options: {options}\n'
    file_string += pretty_stringify_chat(messages)
    file_string += '\n\n\n------------------------END OF ATTEMPT------------------------\n\n\n'
    f.write(file_string)