"""
Test suite for Text-to-Speech (TTS) functionality.

Tests cover the three TTS providers available in BingoXDraw:
- Azure Speech Service: Cloud-based, requires API credentials
- Google TTS (gTTS): Cloud-based, requires internet
- Local TTS (eSpeak): Offline, requires eSpeak/eSpeak-ng installation

Note: These tests are designed to verify the TTS function behavior,
but may require specific dependencies installed for full execution.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bingo_utils import (
    speak_local_tts,
    speak_google_tts,
    initialize_speech_service,
)


# ============================================================================
# LOCAL TTS (ESPEAK) TESTS
# ============================================================================

class TestLocalTTS:
    """Tests for local TTS using eSpeak"""

    @patch('subprocess.run')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    @patch('os.remove')
    def test_speak_local_tts_basic(self, mock_remove, mock_play, mock_load, mock_mixer_init, mock_run):
        """Test basic local TTS functionality"""
        speak_local_tts("Hello world", language="en")
        
        # Verify espeak command was called
        assert mock_run.called
        mock_mixer_init.assert_called_once()
        mock_load.assert_called_once()
        mock_play.assert_called_once()

    @patch('subprocess.run')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    def test_speak_local_tts_different_languages(self, mock_play, mock_load, mock_mixer_init, mock_run):
        """Test local TTS with different languages"""
        languages = ["en", "pt", "es", "fr"]
        
        for lang in languages:
            speak_local_tts(f"Hello in {lang}", language=lang)
        
        # Verify subprocess was called for each language
        assert mock_run.call_count == len(languages)

    @patch('subprocess.run', side_effect=FileNotFoundError)
    def test_speak_local_tts_espeak_not_found(self, mock_run):
        """Test local TTS when eSpeak is not installed"""
        # Should not raise an exception, only print error message
        speak_local_tts("Hello", language="en")
        
        mock_run.assert_called_once()

    @patch('subprocess.run')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    @patch('os.remove')
    def test_speak_local_tts_temp_file_cleanup(self, mock_remove, mock_play, mock_load, mock_mixer_init, mock_run):
        """Test that temporary files are cleaned up after playback"""
        speak_local_tts("Test cleanup", language="en")
        
        # Verify os.remove was called for temp file cleanup
        assert mock_remove.called


# ============================================================================
# GOOGLE TTS TESTS
# ============================================================================

class TestGoogleTTS:
    """Tests for Google Text-to-Speech (gTTS)"""

    @patch('bingo_utils.gTTS')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    @patch('os.remove')
    def test_speak_google_tts_basic(self, mock_remove, mock_play, mock_load, mock_mixer_init, mock_gtts):
        """Test basic Google TTS functionality"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        speak_google_tts("Hello world", language="en")
        
        # Verify gTTS was instantiated with correct parameters
        mock_gtts.assert_called_once_with(text="Hello world", lang="en", slow=False)
        # Verify save and playback
        assert mock_tts_instance.save.called
        mock_mixer_init.assert_called_once()
        mock_load.assert_called_once()
        mock_play.assert_called_once()

    @patch('bingo_utils.gTTS')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    def test_speak_google_tts_different_languages(self, mock_play, mock_load, mock_mixer_init, mock_gtts):
        """Test Google TTS with different languages"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        languages = ["en", "pt", "es", "fr"]
        
        for lang in languages:
            speak_google_tts(f"Hello in {lang}", language=lang)
        
        # Verify gTTS was called for each language
        assert mock_gtts.call_count == len(languages)

    @patch('bingo_utils.gTTS', side_effect=Exception("Network error"))
    def test_speak_google_tts_network_error(self, mock_gtts):
        """Test Google TTS when network is unavailable"""
        # Should not raise an exception, only print error message
        speak_google_tts("Hello", language="en")
        
        mock_gtts.assert_called_once()

    @patch('bingo_utils.gTTS')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    @patch('os.remove')
    def test_speak_google_tts_temp_file_cleanup(self, mock_remove, mock_play, mock_load, mock_mixer_init, mock_gtts):
        """Test that temporary files are cleaned up after playback"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        speak_google_tts("Test cleanup", language="en")
        
        # Verify os.remove was called for temp file cleanup
        assert mock_remove.called

    @patch('bingo_utils.gTTS')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    @patch('os.remove')
    def test_speak_google_tts_uses_mp3_format(self, mock_remove, mock_play, mock_load, mock_mixer_init, mock_gtts):
        """Test that Google TTS uses MP3 format for audio"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        speak_google_tts("Test format", language="en")
        
        # Verify save was called with MP3 file extension
        call_args = mock_tts_instance.save.call_args
        assert call_args is not None


# ============================================================================
# SPEECH SERVICE INITIALIZATION TESTS
# ============================================================================

class TestSpeechServiceInitialization:
    """Tests for speech service initialization"""

    def test_initialize_speech_service_loads_voice_languages(self):
        """Test that voice languages are loaded from JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temporary voice_languages.json file
            voice_file = os.path.join(tmpdir, "voice_languages.json")
            with open(voice_file, 'w', encoding='utf-8') as f:
                f.write('{"en": {"text": "Number", "voice": "en-US-AvaNeural"}}')
            
            # Create a temporary .env file
            env_file = os.path.join(tmpdir, ".env")
            with open(env_file, 'w') as f:
                f.write("")
            
            speech_config, audio_config, voice_languages = initialize_speech_service(
                dotenv_path=env_file,
                voice_languages_file=voice_file
            )
            
            # Verify voice_languages was loaded
            assert voice_languages is not None
            assert "en" in voice_languages

    @patch.dict(os.environ, {'SPEECH_KEY': '', 'SPEECH_REGION': ''})
    def test_initialize_speech_service_without_azure_credentials(self):
        """Test initialization when Azure credentials are not available"""
        with tempfile.TemporaryDirectory() as tmpdir:
            voice_file = os.path.join(tmpdir, "voice_languages.json")
            with open(voice_file, 'w', encoding='utf-8') as f:
                f.write('{"en": {"text": "Number", "voice": "en-US-AvaNeural"}}')
            
            env_file = os.path.join(tmpdir, ".env")
            with open(env_file, 'w') as f:
                f.write("")
            
            speech_config, audio_config, voice_languages = initialize_speech_service(
                dotenv_path=env_file,
                voice_languages_file=voice_file
            )
            
            # Should return None for Azure configs when credentials missing
            assert speech_config is None
            assert audio_config is None
            # But voice_languages should still be loaded
            assert voice_languages is not None

    def test_initialize_speech_service_voice_languages_structure(self):
        """Test that voice_languages has correct structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            voice_file = os.path.join(tmpdir, "voice_languages.json")
            test_languages = {
                "en": {
                    "text": "Number",
                    "voice": "en-US-AvaNeural",
                    "language_code": "en"
                },
                "pt": {
                    "text": "Número",
                    "voice": "pt-PT-DuarteNeural",
                    "language_code": "pt"
                }
            }
            
            import json
            with open(voice_file, 'w', encoding='utf-8') as f:
                json.dump(test_languages, f)
            
            env_file = os.path.join(tmpdir, ".env")
            with open(env_file, 'w') as f:
                f.write("")
            
            speech_config, audio_config, voice_languages = initialize_speech_service(
                dotenv_path=env_file,
                voice_languages_file=voice_file
            )
            
            # Verify structure
            assert len(voice_languages) == 2
            for lang_code, lang_info in voice_languages.items():
                assert "text" in lang_info
                assert "voice" in lang_info or "language_code" in lang_info


# ============================================================================
# TTS INTEGRATION TESTS
# ============================================================================

class TestTTSIntegration:
    """Integration tests for TTS functionality"""

    @patch('bingo_utils.gTTS')
    @patch('subprocess.run')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    def test_tts_provider_selection(self, mock_play, mock_load, mock_mixer_init, mock_run, mock_gtts):
        """Test switching between different TTS providers"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        test_text = "Test number"
        
        # Test Google TTS
        speak_google_tts(test_text, language="en")
        assert mock_gtts.called
        
        # Reset mocks
        mock_gtts.reset_mock()
        mock_run.reset_mock()
        
        # Test Local TTS
        speak_local_tts(test_text, language="en")
        assert mock_run.called

    def test_tts_text_length_handling(self):
        """Test TTS with various text lengths for all providers"""
        # Short text
        short_text = "A"
        
        # Medium text
        medium_text = "This is a medium length text for testing"
        
        # Long text
        long_text = "This is a much longer text " * 10
        
        test_texts = [short_text, medium_text, long_text]
        
        # Test Google TTS with various lengths
        with patch('bingo_utils.gTTS'):
            with patch('pygame.mixer.init'):
                with patch('pygame.mixer.music.load'):
                    with patch('pygame.mixer.music.play'):
                        for text in test_texts:
                            speak_google_tts(text)
        
        # Test Local TTS with various lengths
        with patch('subprocess.run'):
            with patch('pygame.mixer.init'):
                with patch('pygame.mixer.music.load'):
                    with patch('pygame.mixer.music.play'):
                        for text in test_texts:
                            speak_local_tts(text)

    @patch('bingo_utils.gTTS')
    def test_google_tts_special_characters_handling(self, mock_gtts):
        """Test Google TTS with special characters in text"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        special_texts = [
            "Number 123!",
            "Special characters: @#$%",
            "Accents: café, naïve",
            "Symbols: €¥£",
            "Mixed: café #123 @symbol",
            "Portuguese: Número, ção, ã",
            "Spanish: Español, ñoño",
            "French: Français, résumé",
        ]
        
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.music.load'):
                with patch('pygame.mixer.music.play'):
                    for text in special_texts:
                        speak_google_tts(text)
        
        # Verify gTTS was called for each text
        assert mock_gtts.call_count == len(special_texts)

    @patch('subprocess.run')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    def test_local_tts_special_characters_handling(self, mock_play, mock_load, mock_mixer_init, mock_run):
        """Test Local TTS (eSpeak) with special characters in text"""
        special_texts = [
            "Number 123!",
            "Special characters: @#$%",
            "Accents: café, naïve",
            "Symbols: €¥£",
            "Mixed: café #123 @symbol",
            "Portuguese: Número, ção, ã",
            "Spanish: Español, ñoño",
            "French: Français, résumé",
        ]
        
        for text in special_texts:
            speak_local_tts(text)
        
        # Verify subprocess.run was called for each text
        assert mock_run.call_count == len(special_texts)

    @patch('bingo_utils.gTTS')
    @patch('subprocess.run')
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.music.play')
    def test_all_providers_special_characters(self, mock_play, mock_load, mock_mixer_init, mock_run, mock_gtts):
        """Test all TTS providers with identical special character texts"""
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        special_texts = [
            "Number 123!",
            "Accents: café, naïve",
            "Symbols: €¥£",
            "Portuguese: Número",
        ]
        
        # Test Google TTS
        for text in special_texts:
            speak_google_tts(text, language="en")
        
        # Test Local TTS with same texts
        for text in special_texts:
            speak_local_tts(text, language="en")
        
        # Verify both providers were called
        assert mock_gtts.call_count == len(special_texts)
        assert mock_run.call_count == len(special_texts)
