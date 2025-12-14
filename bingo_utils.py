import os
import json
import pickle
import tempfile
import subprocess
import platform
import pygame
import numpy as np
import azure.cognitiveservices.speech as speechsdk
from typing import List, Optional, Tuple, Dict, Any
from dotenv import load_dotenv
from gtts import gTTS


def save_numbers_to_file(filename: str, bingo_numbers: List[int], withdrawn_numbers: List[int]) -> None:
    """
    Save bingo numbers and withdrawn numbers to a binary file using pickle.

    Parameters:
    - filename (str): The name of the file to save the data.
    - bingo_numbers (List[int]): List of available bingo numbers.
    - withdrawn_numbers (List[int]): List of withdrawn bingo numbers.

    Returns:
    None
    """
    with open(filename, 'wb') as file:
        data = {
            'bingo_numbers': bingo_numbers,
            'withdrawn_numbers': withdrawn_numbers,
        }
        pickle.dump(data, file)


def load_numbers_from_file(filename: str, max_bingo_number: int) -> Tuple[List[int], List[int]]:
    """
    Load bingo numbers and withdrawn numbers from a binary file using pickle.

    Parameters:
    - filename (str): The name of the file to load the data.
    - max_bingo_number (int): The maximum bingo number allowed.

    Returns:
    Tuple[List[int], List[int]]: A tuple containing the loaded bingo numbers and withdrawn numbers.
    If the file is not found, default bingo numbers and an empty withdrawn numbers list are returned.
    """
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
            return data['bingo_numbers'], data['withdrawn_numbers']
    except FileNotFoundError:
        return list(range(1, max_bingo_number + 1)), []


def withdraw_number(bingo_numbers: List[int], withdrawn_numbers: List[int]) -> Optional[int]:
    """
    Withdraw a random number from the available bingo numbers.

    Parameters:
    - bingo_numbers (List[int]): List of available bingo numbers.
    - withdrawn_numbers (List[int]): List of withdrawn bingo numbers.

    Returns:
    Optional[int]: The withdrawn number or None if no numbers are available.
    """
    if bingo_numbers:
        index_to_remove = np.random.randint(len(bingo_numbers))
        removed_element = bingo_numbers.pop(index_to_remove)
        withdrawn_numbers.append(removed_element)
        return removed_element
    else:
        return None


def cancel_withdraw(bingo_numbers: List[int], withdrawn_numbers: List[int]) -> Optional[int]:
    """
    Cancel the last withdrawal and return the number to the available bingo numbers.

    Parameters:
    - bingo_numbers (List[int]): List of available bingo numbers.
    - withdrawn_numbers (List[int]): List of withdrawn bingo numbers.

    Returns:
    Optional[int]: The last withdrawn number or None if no withdrawals have been made.
    """
    if withdrawn_numbers:
        last_element_removed = withdrawn_numbers.pop(-1)
        bingo_numbers.append(last_element_removed)
        bingo_numbers.sort()
        return last_element_removed
    else:
        return None


def add_number(bingo_numbers: List[int], number: int) -> None:
    """
    Add a number to the available bingo numbers and sort the list.

    Parameters:
    - bingo_numbers (List[int]): List of available bingo numbers.
    - number (int): The number to be added to the list.

    Returns:
    None
    """
    bingo_numbers.append(number)
    bingo_numbers.sort()


def check_bingo(numbers_to_check: List[int], withdrawn_numbers: List[int]) -> Tuple[List[str], bool]:
    """
    Check the status of specified bingo numbers against the withdrawn numbers.

    Parameters:
    - numbers_to_check (List[int]): List of bingo numbers to check.
    - withdrawn_numbers (List[int]): List of withdrawn bingo numbers.

    Returns:
    Tuple[List[str], bool]: A tuple containing a list of statuses ("Withdrawn" or "Not Withdrawn")
    for each number and a boolean indicating whether all numbers have been withdrawn.
    """
    status = [num in withdrawn_numbers for num in numbers_to_check]
    result = ["Withdrawn" if s else "Not Withdrawn" for s in status]
    return result, all(status)


def speak_local_tts(text: str, language: str = "en") -> None:
    """
    Synthesize and play text using eSpeak (offline, no internet required).
    
    This is a truly local/offline solution that works without internet. eSpeak is available on:
    - Windows: Built-in or install via NSSM/Chocolatey
    - macOS: Install via Homebrew (brew install espeak-ng)
    - Linux/WSL: Install via apt (sudo apt-get install espeak-ng)

    Parameters:
    - text (str): The text to be spoken.
    - language (str): The language code (e.g., 'en', 'pt', 'es', 'fr'). Default is 'en'.

    Returns:
    None
    """
    try:
        # Determine the espeak command based on OS
        espeak_cmd = "espeak-ng" if platform.system() == "Linux" else "espeak"
        
        # Use temporary file for audio output
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        # Run espeak to generate audio file
        command = [espeak_cmd, "-v", language, "-w", tmp_path, text]
        subprocess.run(command, capture_output=True, check=True)
        
        # Play the audio using pygame
        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        
        # Clean up temporary file
        try:
            os.remove(tmp_path)
        except:
            pass
                
    except FileNotFoundError:
        print("Error: espeak or espeak-ng not found.")
        if platform.system() == "Darwin":  # macOS
            print("Install with: brew install espeak-ng")
        elif platform.system() == "Linux":  # Linux/WSL
            print("Install with: sudo apt-get install espeak-ng")
        else:
            print("Please install eSpeak from: http://espeak.sourceforge.net/")
    except subprocess.CalledProcessError as e:
        print(f"Error running espeak: {e}")
    except Exception as e:
        print(f"Error with eSpeak TTS: {e}")


def speak_google_tts(text: str, language: str = "en") -> None:
    """
    Synthesize and play text using Google Text-to-Speech (gTTS).
    
    This requires internet connection but works reliably across all platforms.

    Parameters:
    - text (str): The text to be spoken.
    - language (str): The language code (e.g., 'en', 'pt', 'es', 'fr'). Default is 'en'.

    Returns:
    None
    """
    try:
        # Create gTTS object and save to temporary file
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Use temporary file for audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        tts.save(tmp_path)
        
        # Play the audio using pygame (already available in project)
        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        
        # Clean up temporary file
        try:
            os.remove(tmp_path)
        except:
            pass
                
    except Exception as e:
        print(f"Error with gTTS: {e}")


def initialize_speech_service(dotenv_path="user_files/secrets.env", voice_languages_file="user_files/voice_languages.json") -> Tuple[Optional[Any], Optional[Any], Dict[str, Dict[str, str]]]:
    """
    Initializes the speech service with either Azure Speech Service or local gTTS.

    Parameters:
    - dotenv_path (str): The path to the .env file containing the Azure Speech API keys.
    - voice_languages_file (str): The path to the JSON file containing voice language configurations.

    Returns:
        tuple: A tuple containing (speech_config, audio_config, voice_languages) for Azure,
               or (None, None, voice_languages) for local TTS.
    """
    # Load environment variables from .env file
    load_dotenv(dotenv_path)

    # Open and load the voice languages file
    with open(voice_languages_file, 'r', encoding='utf-8') as file:
        voice_languages = json.load(file)

    try:
        # Get Azure subscription key and region from environment variables
        SPEECH_KEY = os.getenv("SPEECH_KEY")
        SPEECH_REGION = os.getenv("SPEECH_REGION")

        if not SPEECH_KEY or not SPEECH_REGION:
            print("Warning: Azure Speech credentials not found. Falling back to Google TTS.")
            return None, None, voice_languages

        # Configure the Azure Speech Service using environment variables for security
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

        # Set the audio output configuration to use the default speaker for playback
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        return speech_config, audio_config, voice_languages
    except Exception as e:
        print(f"Warning: Could not initialize Azure Speech Service: {e}. Falling back to Google TTS.")
        return None, None, voice_languages