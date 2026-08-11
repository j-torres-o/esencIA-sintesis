from unittest.mock import MagicMock, patch

import pytest

from src.converter.video_converter import VideoConverter
from src.summarizer.gemma_summarizer import GemmaSummarizer
from src.transcriber.audio_transcriber import AudioTranscriber
from src.version import APP_ID, APP_NAME, __version__, get_version_info


class TestVersionInfo:
    def test_version_constants(self):
        assert __version__ == "0.2.1"
        assert APP_NAME == "esencIA"
        assert APP_ID == "com.esencia.video-to-notes.v1"

    def test_get_version_info(self):
        info = get_version_info()
        assert info["version"] == "0.2.1"
        assert info["name"] == "esencIA"
        assert info["app_id"] == "com.esencia.video-to-notes.v1"

class TestVideoConverter:
    def test_convert_mp4_to_mp3_invalid_extension(self):
        converter = VideoConverter()
        with pytest.raises(ValueError, match="El archivo de entrada debe ser un MP4."):
            converter.convert_mp4_to_mp3("test.txt")

    def test_convert_mp4_to_mp3_file_not_found(self):
        converter = VideoConverter()
        with pytest.raises(FileNotFoundError):
            converter.convert_mp4_to_mp3("non_existent_video.mp4")

    @patch("src.converter.video_converter.VideoFileClip")
    def test_convert_mp4_to_mp3_success(self, mock_video_clip, tmp_path):
        output_dir = tmp_path / "outputs"
        converter = VideoConverter(output_dir=str(output_dir))

        test_video = tmp_path / "sample.mp4"
        test_video.write_bytes(b"dummy video content")

        mock_clip_instance = MagicMock()
        mock_audio = MagicMock()
        mock_clip_instance.audio = mock_audio
        mock_video_clip.return_value = mock_clip_instance

        result_path = converter.convert_mp4_to_mp3(str(test_video))

        assert result_path.suffix == ".mp3"
        assert result_path.parent == output_dir
        mock_audio.write_audiofile.assert_called_once()
        mock_clip_instance.close.assert_called_once()

class TestAudioTranscriber:
    def test_transcribe_file_not_found(self):
        transcriber = AudioTranscriber()
        with pytest.raises(FileNotFoundError):
            transcriber.transcribe("non_existent_file.mp3")

    @patch("src.transcriber.audio_transcriber.WhisperModel")
    def test_transcribe_success(self, mock_whisper_model_cls, tmp_path):
        mock_model_instance = MagicMock()

        segment1 = MagicMock()
        segment1.text = "Hola"
        segment1.end = 5.0
        segment2 = MagicMock()
        segment2.text = "mundo"
        segment2.end = 10.0

        mock_info = MagicMock()
        mock_info.duration = 10.0

        mock_model_instance.transcribe.return_value = ([segment1, segment2], mock_info)
        mock_whisper_model_cls.return_value = mock_model_instance

        transcriber = AudioTranscriber(model_size="tiny")
        test_audio = tmp_path / "test_audio.mp3"
        test_audio.write_bytes(b"dummy audio content")

        progress_history = []
        def on_progress(pct):
            progress_history.append(pct)

        result_text = transcriber.transcribe(str(test_audio), progress_callback=on_progress)

        assert result_text == "Hola mundo"
        assert len(progress_history) == 2

class TestGemmaSummarizer:
    @patch("src.summarizer.gemma_summarizer.ConfigManager")
    @patch("openai.OpenAI")
    def test_summarize_empty_text(self, mock_openai, mock_config_cls):
        summarizer = GemmaSummarizer(api_key="fake_key")
        result, tokens = summarizer.summarize("")
        assert result == "No se proporcionó texto para resumir."
        assert tokens == 0

    @patch("src.summarizer.gemma_summarizer.ConfigManager")
    @patch("openai.OpenAI")
    def test_summarize_success(self, mock_openai, mock_config_cls):
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key: {
            "gemma_api_base_url": "http://localhost:11434/v1",
            "gemma_model_name": "gemma"
        }.get(key, "")
        mock_config_cls.return_value = mock_config_instance

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "# Resumen Exec\nTexto de prueba"
        mock_response.usage.total_tokens = 150
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        summarizer = GemmaSummarizer(api_key="fake_key")
        summary_md, tokens = summarizer.summarize("Este es el texto transcrito de la clase.")

        assert summary_md == "# Resumen Exec\nTexto de prueba"
        assert tokens == 150
