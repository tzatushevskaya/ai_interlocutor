import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from main import (
    convert_speech_to_text,
    process_text_through_gpt,
    convert_text_to_speech,
    play_audio,
    process_audio,
    validate_and_reformat_audio_file,
    copy_file_and_get_filename,
)

# Define test audio files
test_data = ["input_audio.wav", "input_audio.mp3", "invalid_audio.xyz"]


class TestMain(unittest.TestCase):

    def setUp(self):

        # Copy the files and get their paths
        (
            self.valid_audio_file_wav,
            self.valid_audio_file_mp3,
            self.invalid_audio_file,
        ) = [
            copy_file_and_get_filename(f"samples/{file_name}")
            for file_name in test_data
        ]

        # Ensure that the files are copied successfully
        assert Path(self.valid_audio_file_wav).exists(), "WAV file not found"
        assert Path(self.valid_audio_file_mp3).exists(), "MP3 file not found"
        assert Path(self.invalid_audio_file).exists(), "Invalid audio file not found"

    def test_convert_speech_to_text(self):
        # Test conversion of speech to text
        recognizer_mock = MagicMock()
        audio_file_mock = MagicMock()
        recognizer_mock.record.return_value = "test audio data"
        recognizer_mock.recognize_whisper.return_value = "test text"
        with patch("main.sr.Recognizer", return_value=recognizer_mock):
            with patch("main.sr.AudioFile", return_value=audio_file_mock):
                text = convert_speech_to_text(self.valid_audio_file_wav)
        self.assertEqual(text, "test text", "Conversion of speech to text failed")

    def test_process_text_through_gpt(self):
        # Test processing text through GPT model
        text = "test text"
        expected_generated_text = "generated text"
        tokenizer_mock = MagicMock()
        model_mock = MagicMock()
        output_mock = MagicMock()
        tokenizer_mock.encode.return_value = "encoded text"
        model_mock.generate.return_value = [output_mock]
        output_mock.tolist.return_value = [1, 2, 3]  # Dummy output
        tokenizer_mock.decode.return_value = expected_generated_text
        with patch("main.GPT2Tokenizer.from_pretrained", return_value=tokenizer_mock):
            with patch("main.GPT2LMHeadModel.from_pretrained", return_value=model_mock):
                generated_text = process_text_through_gpt(text)
        self.assertEqual(
            generated_text,
            expected_generated_text,
            "Processing text through GPT model failed",
        )

    def test_convert_text_to_speech(self):
        # Test conversion of text to speech
        text = "test text"
        with patch("main.gTTS") as gTTS_mock:
            convert_text_to_speech(text)
            gTTS_mock.assert_called_once_with(text=text, lang="en")

    def test_validate_and_reformat_audio_file(self):
        # Test validation and reformatting of audio file format
        with (
            patch("main.wave.open") as wave_open_mock,
            patch("main.AudioSegment.from_mp3") as from_mp3_mock,
        ):
            # Valid WAV file
            wave_open_mock.return_value = MagicMock()
            self.assertTrue(
                validate_and_reformat_audio_file(self.valid_audio_file_wav),
                "Validation and reformatting of WAV file failed",
            )
            # Valid MP3 file
            from_mp3_mock.return_value = MagicMock()
            self.assertTrue(
                validate_and_reformat_audio_file(self.valid_audio_file_mp3),
                "Validation and reformatting of MP3 file failed",
            )
            # Invalid file
            self.assertFalse(
                validate_and_reformat_audio_file(self.invalid_audio_file),
                "Validation of invalid audio file failed",
            )
            # Unlink the files (side effects only, no need to assign to a variable)
            _ = [Path(file_path).unlink() for file_path in test_data]


if __name__ == "__main__":
    unittest.main()
