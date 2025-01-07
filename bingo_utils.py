import os
import json
import pickle
import numpy as np
import azure.cognitiveservices.speech as speechsdk
from typing import List, Optional, Tuple
from dotenv import load_dotenv

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


def initialize_speech_service(dotenv_path="user_files/secrets.env", voice_languages_file="user_files/voice_languages.json"):
    """
    Initializes the Azure Speech Service and loads the voice languages from a JSON file.

    Parameters:
    - dotenv_path (str): The path to the .env file containing the Azure Speech API keys.
    - voice_languages_file (str): The path to the JSON file containing voice language configurations.

    Returns:
        tuple: A tuple containing the speech_config, audio_config, and voice_languages.
    """
    # Load environment variables from .env file
    load_dotenv(dotenv_path)

    # Get Azure subscription key and region from environment variables
    SPEECH_KEY = os.getenv("SPEECH_KEY")
    SPEECH_REGION = os.getenv("SPEECH_REGION")

    # Configure the Azure Speech Service using environment variables for security
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

    # Set the audio output configuration to use the default speaker for playback
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # Open and load the voice languages file
    with open(voice_languages_file, 'r', encoding='utf-8') as file:
        voice_languages = json.load(file)

    return speech_config, audio_config, voice_languages