from unittest.mock import MagicMock, patch

import pytest

from src.converter.video_converter import VideoConverter
from src.summarizer.ollama_summarizer import OllamaSummarizer
from src.transcriber.audio_transcriber import AudioTranscriber
from src.ui.main_window import ProcessingThread
from src.version import APP_ID, APP_NAME, __version__, get_version_info


class TestVersionInfo:
    def test_version_constants(self):
        assert __version__ == "0.5.0"
        assert APP_NAME == "esencIA"
        assert APP_ID == "com.esencia.video-to-notes.v1"

    def test_get_version_info(self):
        info = get_version_info()
        assert info["version"] == "0.5.0"
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

    def test_format_timestamp(self):
        from src.transcriber.audio_transcriber import format_timestamp, get_optimal_cpu_threads
        assert format_timestamp(0.0) == "00:00"
        assert format_timestamp(45.2) == "00:45"
        assert format_timestamp(65.0) == "01:05"
        assert format_timestamp(3600.0) == "01:00:00"
        assert format_timestamp(3665.0) == "01:01:05"
        assert get_optimal_cpu_threads() >= 1

    @patch("src.transcriber.audio_transcriber.WhisperModel")
    def test_transcribe_success(self, mock_whisper_model_cls, tmp_path):
        mock_model_instance = MagicMock()

        segment1 = MagicMock()
        segment1.text = "Hola"
        segment1.start = 0.0
        segment1.end = 5.0
        segment2 = MagicMock()
        segment2.text = "mundo"
        segment2.start = 5.0
        segment2.end = 10.0

        mock_info = MagicMock()
        mock_info.duration = 10.0

        mock_model_instance.transcribe.return_value = ([segment1, segment2], mock_info)
        mock_whisper_model_cls.return_value = mock_model_instance

        transcriber = AudioTranscriber(engine_type="whisper_large_v3_turbo")
        test_audio = tmp_path / "test_audio.mp3"
        test_audio.write_bytes(b"dummy audio content")

        progress_history = []
        def on_progress(pct):
            progress_history.append(pct)

        result_text = transcriber.transcribe(str(test_audio), progress_callback=on_progress)

        assert result_text == "[00:00] Hola\n[00:05] mundo"
        assert len(progress_history) >= 2
        assert 100 in progress_history

        result_without_ts = transcriber.transcribe(str(test_audio), include_timestamps=False)
        assert result_without_ts == "Hola mundo"

    @patch("src.transcriber.audio_transcriber.WhisperModel")
    def test_transcribe_parakeet_fallback_to_whisper(self, mock_whisper_model_cls, tmp_path):
        mock_model_instance = MagicMock()
        segment = MagicMock()
        segment.text = "Texto transcrito"
        segment.start = 0.0
        segment.end = 10.0
        mock_info = MagicMock()
        mock_info.duration = 10.0
        mock_model_instance.transcribe.return_value = ([segment], mock_info)
        mock_whisper_model_cls.return_value = mock_model_instance

        transcriber = AudioTranscriber(engine_type="parakeet_redux")
        test_audio = tmp_path / "test_audio.mp3"
        test_audio.write_bytes(b"dummy audio content")

        res = transcriber.transcribe(str(test_audio))
        assert res == "[00:00] Texto transcrito"

    @patch("src.transcriber.audio_transcriber.WhisperModel")
    def test_transcribe_with_batched_pipeline(self, mock_whisper_model_cls, tmp_path):
        mock_model_instance = MagicMock()
        mock_whisper_model_cls.return_value = mock_model_instance

        transcriber = AudioTranscriber(engine_type="whisper_large_v3_turbo")
        test_audio = tmp_path / "test_audio.mp3"
        test_audio.write_bytes(b"dummy audio content")

        mock_batched = MagicMock()
        segment = MagicMock()
        segment.text = "Inferencia acelerada"
        segment.start = 12.0
        segment.end = 18.0
        mock_info = MagicMock()
        mock_info.duration = 18.0
        mock_batched.transcribe.return_value = ([segment], mock_info)

        transcriber.batched_pipeline = mock_batched
        res = transcriber.transcribe(str(test_audio))

        assert res == "[00:12] Inferencia acelerada"
        mock_batched.transcribe.assert_called_once()
        assert mock_batched.transcribe.call_args[1]["batch_size"] == 16


class TestOllamaSummarizer:
    @patch("src.summarizer.ollama_summarizer.ConfigManager")
    @patch("requests.post")
    def test_summarize_empty_text(self, mock_requests_post, mock_config_cls):
        summarizer = OllamaSummarizer()
        result, tokens = summarizer.summarize("")
        assert result == "No se proporcionó texto para resumir."
        assert tokens == 0

    @patch("src.summarizer.ollama_summarizer.ConfigManager")
    @patch("requests.post")
    def test_summarize_success(self, mock_requests_post, mock_config_cls):
        mock_config_instance = MagicMock()
        mock_config_instance.get.side_effect = lambda key: {
            "gemma_api_base_url": "http://localhost:11434",
            "gemma_model_name": "gemma"
        }.get(key, "")
        mock_config_cls.return_value = mock_config_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "# Resumen Exec\nTexto de prueba",
            "eval_count": 100,
            "prompt_eval_count": 50
        }
        mock_requests_post.return_value = mock_response

        summarizer = OllamaSummarizer()
        summary_md, tokens = summarizer.summarize("Este es el texto transcrito de la clase.")

        assert summary_md == "# Resumen Exec\nTexto de prueba"
        assert tokens == 150

    @patch("src.summarizer.ollama_summarizer.ConfigManager")
    @patch("requests.post")
    def test_summarize_connection_error(self, mock_requests_post, mock_config_cls):
        import requests
        mock_requests_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        summarizer = OllamaSummarizer()
        with pytest.raises(ConnectionError) as exc_info:
            summarizer.summarize("Texto de prueba")
        assert "No se pudo conectar al servidor local de Ollama" in str(exc_info.value)

class TestProcessingThreadCheckpoints:
    @patch("src.ui.main_window.OllamaSummarizer")
    @patch("src.ui.main_window.AudioTranscriber")
    @patch("src.ui.main_window.VideoConverter")
    def test_checkpoint_resume_all_exist(self, mock_converter_cls, mock_transcriber_cls, mock_summarizer_cls, tmp_path):
        video_file = tmp_path / "clase.mp4"
        video_file.write_bytes(b"dummy video")

        audio_file = tmp_path / "clase.mp3"
        audio_file.write_bytes(b"dummy audio")

        txt_file = tmp_path / "clase_transcription.txt"
        txt_file.write_text("Transcripcion previamente realizada", encoding="utf-8")

        md_file = tmp_path / "clase_summary.md"
        md_file.write_text("# Resumen Previo\nContenido guardado", encoding="utf-8")

        thread = ProcessingThread(str(video_file))

        messages = []
        thread.progress_signal.connect(lambda msg: messages.append(msg))
        finished_res = []
        thread.finished_signal.connect(lambda res: finished_res.append(res))

        thread.run()

        mock_converter_cls.assert_not_called()
        mock_transcriber_cls.assert_not_called()
        assert any("Artefacto de audio previo detectado" in m for m in messages)
        assert any("Transcripción previa detectada" in m for m in messages)
        assert any("Resumen previo detectado" in m for m in messages)
        assert finished_res[0] == "# Resumen Previo\nContenido guardado"


class TestUIBackendInfo:
    def test_get_app_info_returns_valid_json_string(self):
        import json
        from unittest.mock import MagicMock

        from src.ui.main_window import UIBackend

        mock_window = MagicMock()
        backend = UIBackend(mock_window)
        raw_info = backend.get_app_info()

        assert isinstance(raw_info, str)
        parsed = json.loads(raw_info)
        assert parsed["name"] == APP_NAME
        assert parsed["version"] == __version__
        assert parsed["app_id"] == APP_ID
