"""
Unit tests for the dress agent tools.
Tests run without calling real APIs — all external calls are mocked.
"""
import base64
import os
import pytest
from unittest.mock import MagicMock, patch


class MockToolContext:
    """Minimal stand-in for ADK's ToolContext."""
    def __init__(self, state=None):
        self.state = state or {}


# ── analyze_dress_image ───────────────────────────────────────────────────────

class TestAnalyzeDressImage:

    def _make_context(self, with_image=True):
        state = {}
        if with_image:
            fake_image = b"fake-image-bytes"
            state["uploaded_image_bytes"] = base64.b64encode(fake_image).decode()
            state["uploaded_image_mime"] = "image/jpeg"
        return MockToolContext(state=state)

    def test_returns_error_when_no_image_in_state(self):
        from dress_agent.tools.analyze_image_tool import analyze_dress_image
        ctx = self._make_context(with_image=False)
        result = analyze_dress_image(tool_context=ctx)
        assert "שגיאה" in result

    def test_writes_analysis_to_state(self):
        from dress_agent.tools.analyze_image_tool import analyze_dress_image
        ctx = self._make_context()

        mock_response = MagicMock()
        mock_response.text = "שמלה שחורה, צוואר סירה, ללא שרוולים"

        with patch("dress_agent.tools.analyze_image_tool.genai.Client") as MockClient:
            MockClient.return_value.models.generate_content.return_value = mock_response
            result = analyze_dress_image(tool_context=ctx)

        assert ctx.state["dress_analysis"] == "שמלה שחורה, צוואר סירה, ללא שרוולים"
        assert result == "שמלה שחורה, צוואר סירה, ללא שרוולים"

    def test_calls_gemini_with_image_and_text(self):
        from dress_agent.tools.analyze_image_tool import analyze_dress_image
        ctx = self._make_context()

        mock_response = MagicMock()
        mock_response.text = "ניתוח השמלה"

        with patch("dress_agent.tools.analyze_image_tool.genai.Client") as MockClient:
            mock_generate = MockClient.return_value.models.generate_content
            mock_generate.return_value = mock_response
            analyze_dress_image(tool_context=ctx)

        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        assert call_args.kwargs["model"] == "gemini-2.5-flash"


# ── generate_dress_sketch ─────────────────────────────────────────────────────

class TestGenerateDressSketch:

    def _make_context(self):
        return MockToolContext(state={})

    def test_saves_image_to_output_folder(self, tmp_path):
        from dress_agent.tools.imagen_tool import generate_dress_sketch

        fake_bytes = b"\x89PNG\r\n"
        mock_image = MagicMock()
        mock_image.image.image_bytes = fake_bytes
        mock_response = MagicMock()
        mock_response.generated_images = [mock_image]

        ctx = self._make_context()

        with patch("dress_agent.tools.imagen_tool.genai.Client") as MockClient, \
             patch("dress_agent.tools.imagen_tool.os.makedirs"), \
             patch("builtins.open", create=True) as mock_open:
            MockClient.return_value.models.generate_images.return_value = mock_response
            mock_open.return_value.__enter__ = lambda s: s
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            mock_open.return_value.write = MagicMock()

            result = generate_dress_sketch(
                design_description="שמלה כחולה עם כתפיות",
                tool_context=ctx,
            )

        assert "output/new_design.png" in result
        assert ctx.state["sketch_path"] == "output/new_design.png"

    def test_prompt_contains_vogue_style_instruction(self):
        from dress_agent.tools.imagen_tool import generate_dress_sketch

        fake_bytes = b"\x89PNG"
        mock_image = MagicMock()
        mock_image.image.image_bytes = fake_bytes
        mock_response = MagicMock()
        mock_response.generated_images = [mock_image]

        ctx = self._make_context()

        with patch("dress_agent.tools.imagen_tool.genai.Client") as MockClient, \
             patch("dress_agent.tools.imagen_tool.os.makedirs"), \
             patch("builtins.open", create=True) as mock_open:
            MockClient.return_value.models.generate_images.return_value = mock_response
            mock_open.return_value.__enter__ = lambda s: s
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            mock_open.return_value.write = MagicMock()

            generate_dress_sketch(
                design_description="שמלה ירוקה",
                tool_context=ctx,
            )

        call_kwargs = MockClient.return_value.models.generate_images.call_args.kwargs
        prompt = call_kwargs["prompt"]
        assert "Vogue" in prompt
        assert "שמלה ירוקה" in prompt
