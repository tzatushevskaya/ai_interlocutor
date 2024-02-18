"""
This module implements an AI Interlocutor, which automates the conversion of speech to text,
processes the text through a preconfigured GPT model acting as a specific expert,
converts the GPT's textual response back to speech, and finally plays the resulting audio.

The main functionalities include:
- Converting speech from an audio file to text using Google's Speech Recognition.
- Processing the text through a preconfigured GPT model.
- Converting the GPT model's textual response back to speech using Google Text-to-Speech (gTTS).
- Playing the resulting audio.

Dependencies:
- `argparse`: For parsing command-line arguments.
- `functools`: For handling errors with decorators.
- `json`: For JSON serialization of log records.
- `logging`: For logging messages to console and file.
- `shutil`: For file operations like copying.
- `wave`: For handling audio files.
- `datetime`: For generating timestamps.
- `colorlog`: For colorized logging output.
- `pygame`: For audio playback.
- `speech_recognition`: For converting speech to text.
- `gtts`: For text-to-speech conversion.
- `pydub`: For audio file manipulation.
- `transformers`: For accessing preconfigured GPT models.

Usage:
The script can be run with optional arguments to specify the input audio file and execution mode.
"""

import argparse
import functools
import json
import logging
import shutil
import wave
from datetime import datetime
from logging import Logger
from pathlib import Path

import colorlog
import pygame
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from transformers import GPT2LMHeadModel, GPT2Tokenizer


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for logging records."""

    def format(self, record):
        """
        Format the logging record as a JSON object.

        Parameters:
        - record (LogRecord): The logging record to format.

        Returns:
        - str: The JSON-formatted logging record.
        """
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        return json.dumps(log_record)


def setup_logger(logger_name, style=None, filename=None, json_formatter=False):
    """
    Set up a logger with customizable formatting and output options.

    Parameters:
    - logger_name (str): The name of the logger.
    - style (str, optional): The style of formatting to use.
    If set to "color", a colored formatter will be applied.
    Defaults to None.
    - filename (str, optional): The path to the log file.
    If provided, logs will be written to this file.
    Defaults to None.
    - json_formatter (bool, optional): Whether to enable JSON formatting for logs.
    If True, logs will be formatted
    as JSON objects. Defaults to False.

    Returns:
    - Logger: The configured logger object.
    """
    # Create a logger
    configured_logger: Logger = logging.getLogger(logger_name)
    configured_logger.setLevel(logging.INFO)

    # Create a formatter
    color_formatter = colorlog.ColoredFormatter(
        (
            "%(white)s%(asctime)s - [%(cyan)s%(levelname)s%(reset)s]"
            "[%(green)s%(filename)s%(reset)s:"
            "%(yellow)s%(funcName)s:%(purple)s%(lineno)s%(reset)s] %(message)s"
        )
    )
    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s][%(filename)s:%(funcName)s:%(lineno)s] %(message)s"
    )

    # Create a handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if style and style == "color":
        handler.setFormatter(color_formatter)

    # Add the handler to the logger
    configured_logger.addHandler(handler)
    configured_logger.propagate = False

    if json_formatter:
        log_json_handler = logging.FileHandler(filename, mode="a")
        json_formatter = JSONFormatter()
        log_json_handler.setFormatter(json_formatter)
        configured_logger.addHandler(log_json_handler)

    return configured_logger


current_timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
local_log_file = Path(f"log_{current_timestamp}.json")
logger = setup_logger(__name__, filename=local_log_file, json_formatter=True)


def handle_errors(error_logger):
    """
    A decorator function that wraps another function and handles errors by logging them.

    Args:
    - logger (Logger): The logger object used for error logging.

    Returns:
    - function: A wrapped function that handles errors gracefully.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_logger.error(f"An error occurred in {func.__name__}: {e}")
                raise e

        return wrapper

    return decorator


@handle_errors(logger)
def find_file(file_name):
    """
    Search for a file with the specified name recursively starting from the current directory.

    Parameters:
    - file_name (str): The name of the file to search for.

    Returns:
    - Path: The path to the first found file.

    Raises:
    - FileNotFoundError: If the specified file is not found.
    """
    # Search for the file recursively starting from the current directory
    found_files = list(Path.cwd().rglob(file_name))

    if found_files:
        return found_files[0]  # Return the first found file
    raise FileNotFoundError  # Return None if the file is not found


@handle_errors(logger)
def copy_file_and_get_filename(file_path_str):
    """
    Copy the file specified by the input path to the directory where the script is located.

    If the file already exists in the script's directory, the existing file is used.
    If the file does not exist, it searches for the file recursively
    starting from the current directory.
    The copied file's name is returned.

    Parameters:
    - file_path_str (str): Path to the file to be copied.

    Returns:
    - str: The name of the copied file.
    """
    # Convert the input string to a Path object
    supposed_path = Path(file_path_str)
    # Find existing path
    file_path = (
        supposed_path if supposed_path.exists() else find_file(supposed_path.name)
    )

    # Get the filename
    filename = file_path.name

    # Copy the file to the directory where the script is placed
    destination_path = Path(__file__).resolve().parent / filename
    # destination_path = Path.cwd() / filename

    shutil.copy(file_path, destination_path)

    return filename


@handle_errors(logger)
def reformat_to_wav(filename):
    """
    Convert an audio file from MP3 to WAV format.

    Parameters:
    - filename (str): Input audio file name.
    """
    sound = AudioSegment.from_mp3(filename)
    sound.export(filename, format="wav")


@handle_errors(logger)
def convert_speech_to_text(audio_file):
    """
    Convert speech from an audio file to text using Google's Speech Recognition.

    Parameters:
    - audio_file (str): Path to the input audio file.

    Returns:
    - str: The recognized text.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_whisper(audio_data)
        return text


@handle_errors(logger)
def process_text_through_gpt(text):
    """
    Process the given text through a preconfigured GPT model.

    Parameters:
    - text (str): The input text to process.

    Returns:
    - str: The processed text generated by the GPT model.
    """
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
    model = GPT2LMHeadModel.from_pretrained("gpt2-medium")
    input_ids = tokenizer.encode(text, return_tensors="pt")
    output = model.generate(input_ids, max_length=100, num_return_sequences=1)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    cleaned_up_text = remove_repetitive_sentences(generated_text)
    return cleaned_up_text


@handle_errors(logger)
def remove_repetitive_sentences(text):
    """
    Remove repetitive sentences from a string.

    Parameters:
    - text (str): The input text containing sentences.

    Returns:
    - str: The text with repetitive sentences removed.
    """
    # Find the index of the last occurrence of '.'
    last_period_index = text.rfind(".")

    if last_period_index == -1:
        return text

    # Extract the text before the last period
    text_before_last_period = text[: last_period_index + 1]

    # Split the text before the last period into sentences
    sentences = text_before_last_period.split(".")

    # Initialize a set to store unique sentences
    unique_sentences = set()

    # Initialize a list to store non-repetitive sentences
    non_repetitive_sentences = []

    # Iterate over each sentence in the text
    for sentence in sentences:
        # Strip leading and trailing whitespace
        sentence = sentence.strip()

        # Add non-empty and unique sentences to the set
        if sentence and sentence not in unique_sentences:
            unique_sentences.add(sentence)
            non_repetitive_sentences.append(sentence)

    # Join the non-repetitive sentences back into a string
    result = ".".join(non_repetitive_sentences)

    return result.strip()


@handle_errors(logger)
def convert_text_to_speech(text):
    """
    Convert the given text to speech using Google Text-to-Speech (gTTS) library.

    Parameters:
    - text (str): The input text to convert.

    Returns:
    - gTTS: The gTTS object containing the audio data.
    """
    tts = gTTS(text=text, lang="en")
    return tts


@handle_errors(logger)
def play_audio(audio_file):
    """
    Play the audio file.

    Parameters:
    - audio_file (str): Path to the audio file to play.
    """
    reformat_to_wav(audio_file)
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


@handle_errors(logger)
def process_audio(audio_file):
    """
    Process the audio file.

    Parameters:
    - audio_file (str): Path to the input audio file.

    Returns:
    - str: Path to the processed audio file.
    """
    # Convert speech to text
    text = convert_speech_to_text(audio_file)

    # Process text through GPT model
    gpt_response = process_text_through_gpt(text)

    # Convert text response to speech
    tts = convert_text_to_speech(gpt_response)

    # Save text-to-speech output to a temporary file
    output_audio_file = "output_audio.wav"
    tts.save(output_audio_file)

    return output_audio_file


@handle_errors(logger)
def validate_and_reformat_audio_file(audio_file):
    """
    Check if the given audio file is in a valid format (WAV or MP3).

    Parameters:
    - audio_file (str): Path to the input audio file.

    Returns:
    - bool: True if the audio file is in a valid format, False otherwise.
    """
    if audio_file.endswith(".wav") or audio_file.endswith(".mp3"):
        reformat_to_wav(audio_file)
        try:
            with wave.open(audio_file, "rb"):
                return True
        except wave.Error as e:
            logger.warning(
                "An error occurred while validating the file format "
                "by trying to open it with WAV: %s",
                e,
            )
            return False
    else:
        return False


@handle_errors(logger)
def process_audio_file(input_audio_file):
    """
    Main function to process the input audio file.

    Parameters:
    - input_audio_file (str): Path to the input audio file.

    """
    # Validate audio file format
    if not validate_and_reformat_audio_file(input_audio_file):
        error_message = (
            "Error: Unsupported audio file format. "
            "Please provide a WAV or MP3 audio file."
        )
        print(error_message)
        logger.error(error_message)
        return

    # Process audio
    output_audio_file = process_audio(input_audio_file)

    # Play the resulting audio
    logger.info("Playing the resulting audio...")
    play_audio(output_audio_file)

    # Check the response in the audio file:
    response = convert_speech_to_text(output_audio_file)
    logger.info('The obtained response is "%s".', response)

    # Clean up temporary files
    Path(output_audio_file).unlink()
    print("The task is completed.")


def run():
    """Runs stages of audio processing in the conceived order,
    possibly with parameters."""

    parser = argparse.ArgumentParser(description="AI Interlocutor")

    parser.add_argument(
        "--file",
        "-f",
        type=str,
        default="samples/input_audio.wav",
        help="\tPath to audio file to process."
        "The default value is test sample audio file.",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run the program in the interactive mode.",
    )

    args = parser.parse_args()
    is_interactive = bool(args.interactive)
    input_file = (
        input(
            "Please enter the path to the audio file you want to process (wav or mp3):"
        )
        if is_interactive
        else args.file
    )

    filename = copy_file_and_get_filename(input_file)
    process_audio_file(filename)
    Path(filename).unlink()


if __name__ == "__main__":
    run()
