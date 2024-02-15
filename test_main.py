import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os
from main import (
    convert_speech_to_text,
    process_text_through_gpt,
    convert_text_to_speech,
    play_audio,
    process_audio,
    is_valid_audio_format,
)

class TestMain(unittest.TestCase):

    def setUp(self):
        self.test_audio_file_wav = "test_audio.wav"
        self.test_audio_file_mp3 = "test_audio.mp3"

    def test_convert_speech_to_text(self):
        # Mock Recognizer and AudioFile
        recognizer_mock = MagicMock()
        audio_file_mock = MagicMock()
        recognizer_mock.record.return_value = "test audio data"
        recognizer_mock.recognize_google.return_value = "test text"
        with patch("speech_recognition.Recognizer", return_value=recognizer_mock):
            with patch("speech_recognition.AudioFile", return_value=audio_file_mock):
                text = convert_speech_to_text(self.test_audio_file_wav)
        self.assertEqual(text, "test text")

    def test_process_text_through_gpt(self):
        text = "test text"
        expected_generated_text = "generated text"
        tokenizer_mock = MagicMock()
        model_mock = MagicMock()
        output_mock = MagicMock()
        tokenizer_mock.encode.return_value = "encoded text"
        model_mock.generate.return_value = [output_mock]
        output_mock.tolist.return_value = [1, 2, 3]  # Dummy output
        tokenizer_mock.decode.return_value = expected_generated_text
        with patch("transformers.GPT2Tokenizer.from_pretrained", return_value=tokenizer_mock):
            with patch("transformers.GPT2LMHeadModel.from_pretrained", return_value=model_mock):
                generated_text = process_text_through_gpt(text)
        self.assertEqual(generated_text, expected_generated_text)

    def test_convert_text_to_speech(self):
        text = "test text"
        with patch("gtts.gTTS") as gTTS_mock:
            convert_text_to_speech(text)
            gTTS_mock.assert_called_once_with(text=text, lang="en")

    def test_play_audio(self):
        audio_file = "test_audio.mp3"
        mixer_mock = MagicMock()
        mixer_music_mock = MagicMock()
        pygame_mock = MagicMock()
        pygame_mock.mixer = mixer_mock
        pygame_mock.mixer.music = mixer_music_mock
        with patch("pygame.mixer", pygame_mock):
            play_audio(audio_file)
            mixer_music_mock.load.assert_called_once_with(audio_file)
            mixer_music_mock.play.assert_called_once()

    def test_process_audio(self):
        audio_file = "test_audio.wav"
        expected_output_audio_file = "samples/output_audio.mp3"
        mock_text = "test text"
        mock_gpt_response = "generated text"
        with patch("main.convert_speech_to_text", return_value=mock_text):
            with patch("main.process_text_through_gpt", return_value=mock_gpt_response):
                with patch("main.convert_text_to_speech") as convert_text_to_speech_mock:
                    convert_text_to_speech_mock.return_value = MagicMock()
                    with patch("main.play_audio") as play_audio_mock:
                        output_audio_file = process_audio(audio_file)
                        convert_text_to_speech_mock.assert_called_once_with(mock_gpt_response)
                        play_audio_mock.assert_called_once_with(expected_output_audio_file)
                        self.assertEqual(output_audio_file, expected_output_audio_file)

    def test_is_valid_audio_format(self):
        valid_audio_file_wav = "valid_audio.wav"
        valid_audio_file_mp3 = "valid_audio.mp3"
        invalid_audio_file = "invalid_audio.xyz"
        with patch("wave.open") as wave_open_mock, patch("pydub.AudioSegment.from_mp3") as from_mp3_mock:
            # Valid WAV file
            wave_open_mock.return_value = MagicMock()
            self.assertTrue(is_valid_audio_format(valid_audio_file_wav))
            # Valid MP3 file
            from_mp3_mock.return_value = MagicMock()
            self.assertTrue(is_valid_audio_format(valid_audio_file_mp3))
            # Invalid file
            self.assertFalse(is_valid_audio_format(invalid_audio_file))

if __name__ == "__main__":
    unittest.main()
