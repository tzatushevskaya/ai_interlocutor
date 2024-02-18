# Speech to Text with GPT Processing

## Task

Develop a Python application that automates the conversion of speech to text, processes the text through a preconfigured GPT model acting as a specific expert, converts the GPT's textual response back to speech, and finally plays the resulting audio. This entire process should be executable on a local computer environment without the need for internet connectivity once all components are installed.

Requirements:

1. Python Version: Ensure the application is compatible with Python 3.8 or newer.
2. Libraries and Dependencies:
   - Use `speech_recognition` or any suitable library for converting speech to text.
   - Utilize a local instance of GPT (OpenAI's GPT-3 or an equivalent model) for generating expert responses. Assume the model is preconfigured and available locally.
   - Use `gTTS` (Google Text-to-Speech) or any suitable library for converting text responses back to speech.
   - Implement `pygame` or a similar library for audio playback.
   - Ensure all dependencies are clearly listed in a `requirements.txt` file.

3. Functionality:
   - Audio Input: The application should accept an audio file (e.g., WAV or MP3 format) as input. This file contains the speech to be converted to text.
   - Speech to Text: Convert the speech from the audio file into text using the `speech_recognition` library or an equivalent.
   - GPT Processing: Pass the converted text to the local GPT model, configured to simulate a specific expert (e.g., a financial advisor, a medical consultant, etc.). The exact nature of the expert should be defined prior to development.
   - Text to Speech: Convert the GPT model's textual response into speech using the `gTTS` library or an equivalent.
   - Audio Output: Save the resulting speech as an audio file and play it using `pygame` or a similar library.

4. User Interface: Implement a simple command-line interface (CLI) that allows users to:
   - Specify the path to the input audio file.
   - Initiate the processing workflow.
   - Receive feedback about the current stage of processing (e.g., "Converting speech to text...", "Generating response...", etc.).
   - Play the final audio response directly in the CLI.

5. Documentation:
   - Provide a README file with:
     - Installation instructions for all necessary libraries and dependencies.
     - Step-by-step instructions on how to run the application.
     - A brief description of the application's functionality.
   - Include inline comments in the code for clarity and maintainability.

6. Testing:
   - Include basic unit tests to verify the functionality of key components (e.g., speech to text conversion, text to speech conversion).
   - Provide sample audio files for testing purposes.

Deliverables:

1. Python script(s) implementing the described functionality.
2. `requirements.txt` file listing all external libraries and dependencies.
3. A README file containing all necessary documentation.
4. A folder with sample audio files for testing.
5. A test suite for basic functionality verification.

Evaluation Criteria:

- Functionality: The application meets all described requirements and performs the expected processing workflow without errors.
- Code Quality: The code is well-organized, clearly commented, and follows Python coding standards.
- Documentation: The provided documentation is clear, concise, and sufficient for setting up and using the application.
- Error Handling: The application gracefully handles and reports errors, such as unsupported audio formats or failure in any processing stage.


This Python application automates the conversion of speech to text, processes the text through a preconfigured GPT model
acting as a specific expert, converts the GPT's textual response back to speech, and finally plays the resulting audio.

## Prerequisites

This project requires a Linux operating system to run.

## Installation

1. Clone the repository to your local machine.
    ```bash
    git clone https://github.com/tzatushevskaya/ai_interlocutor.git
    ```
2. Navigate to the project directory.
    ```bash
    cd ./ai_interlocutor
    ```

It's recommended to run this project in a virtual environment to manage dependencies cleanly. 
You can use tools like `venv` or `micromamba` to create a virtual environment.

### Using micromamba

If you have micromamba installed, you can create a virtual environment and install dependencies like this:

```bash
# Create a new virtual environment
micromamba create -n myenv python=3.9.16

# Activate the virtual environment
micromamba activate myenv

# Install project dependencies
pip install --no-cache-dir -r requirements.txt .
```

### Using venv

If you prefer using venv, you can create and activate a virtual environment like this:

```bash
# Create a new virtual environment
python -m venv myenv

# Activate the virtual environment 
source myenv/bin/activate

# Install project dependencies
pip install --no-cache-dir -r requirements.txt .
```

Install the ffmpeg:
```bash
ffdl install -y
```

## Running the Application

### Without Parameters (Demo Mode)
Run the app without parameters (it will process the existing audio file):
```bash
python main.py
```

### Without Parameters (Interactive Mode)
Run the app in interactive mode:
```bash
python main.py -i
```

### With Parameters

Run the app with the desired parameters:
```bash
python main.py <path_to_audio_file>
```
Replace `<path_to_audio_file>` with the path to the audio file you want to process.

Follow the prompts to provide the path to the input audio file when prompted.

## Testing the Application
Execute the unit tests:
```bash
python test_main.py
```
