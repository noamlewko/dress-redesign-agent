"""
Unit tests for dress agent tools.
All external API calls are mocked — no real network or API key required.
"""
import base64
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
            state["uploaded_image_bytes"] = base64.b64encode(b"fake-image-bytes").decode()
            state["uploaded_image_mime"] = "image/jpeg"
        return MockToolContext(state=state)

    def test_returns_error_when_no_image_in_state(self):
        from dress_agent.tools.analyze_image_tool import analyze_dress_image

        ctx = self._make_context(with_image=False)
        result = analyze_dress_image(tool_context=ctx)
        assert "Error" in result

    def test_writes_analysis_to_state(self):
        from dress_agent.tools.analyze_image_tool import analyze_dress_image

        ctx = self._make_context()
        mock_response = MagicMock()
        mock_response.text = "Black dress, boat neck, sleeveless"

        with patch("dress_agent.tools.analyze_image_tool.genai.Client") as MockClient:
            MockClient.return_value.models.generate_content.return_value = mock_response
            result = analyze_dress_image(tool_context=ctx)

        assert ctx.state["dress_analysis"] == "Black dress, boat neck, sleeveless"
        assert result == "Black dress, boat neck, sleeveless"

    def test_calls_gemini_with_correct_model(self):
        from dress_agent.tools.analyze_image_tool import analyze_dress_image

        ctx = self._make_context()
        mock_response = MagicMock()
        mock_response.text = "dress analysis"

        with patch("dress_agent.tools.analyze_image_tool.genai.Client") as MockClient:
            mock_generate = MockClient.return_value.models.generate_content
            mock_generate.return_value = mock_response
            analyze_dress_image(tool_context=ctx)

        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        assert call_args.kwargs["model"] == "gemini-flash-lite-latest"


# ── generate_dress_sketch ─────────────────────────────────────────────────────


def _make_mock_image_response(image_bytes: bytes) -> MagicMock:
    """Build a mock that matches the Gemini generate_content response shape."""
    part = MagicMock()
    part.inline_data = MagicMock()
    part.inline_data.data = image_bytes

    content = MagicMock()
    content.parts = [part]

    candidate = MagicMock()
    candidate.content = content

    response = MagicMock()
    response.candidates = [candidate]
    return response


class TestGenerateDressSketch:

    def _make_context(self):
        return MockToolContext(state={})

    def test_saves_image_to_output_folder(self):
        from dress_agent.tools.imagen_tool import generate_dress_sketch

        mock_response = _make_mock_image_response(b"\x89PNG\r\n")
        ctx = self._make_context()

        with patch("dress_agent.tools.imagen_tool.genai.Client") as MockClient, \
             patch("dress_agent.tools.imagen_tool.os.makedirs"), \
             patch("builtins.open", create=True) as mock_open:
            MockClient.return_value.models.generate_content.return_value = mock_response
            mock_open.return_value.__enter__ = lambda s: s
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            mock_open.return_value.write = MagicMock()

            result = generate_dress_sketch(
                design_description="blue dress with straps",
                tool_context=ctx,
            )

        assert "output/new_design.png" in result
        assert ctx.state["sketch_path"] == "output/new_design.png"

    def test_calls_gemini_image_model(self):
        from dress_agent.tools.imagen_tool import generate_dress_sketch

        mock_response = _make_mock_image_response(b"\x89PNG")
        ctx = self._make_context()

        with patch("dress_agent.tools.imagen_tool.genai.Client") as MockClient, \
             patch("dress_agent.tools.imagen_tool.os.makedirs"), \
             patch("builtins.open", create=True) as mock_open:
            mock_generate = MockClient.return_value.models.generate_content
            mock_generate.return_value = mock_response
            mock_open.return_value.__enter__ = lambda s: s
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            mock_open.return_value.write = MagicMock()

            generate_dress_sketch(
                design_description="green dress",
                tool_context=ctx,
            )

        call_kwargs = mock_generate.call_args.kwargs
        assert call_kwargs["model"] == "gemini-3.1-flash-image"
        assert "green dress" in call_kwargs["contents"]

    def test_returns_no_image_message_when_response_has_no_image(self):
        from dress_agent.tools.imagen_tool import generate_dress_sketch

        part = MagicMock()
        part.inline_data = None
        candidate = MagicMock()
        candidate.content.parts = [part]
        mock_response = MagicMock()
        mock_response.candidates = [candidate]

        ctx = self._make_context()

        with patch("dress_agent.tools.imagen_tool.genai.Client") as MockClient, \
             patch("dress_agent.tools.imagen_tool.os.makedirs"):
            MockClient.return_value.models.generate_content.return_value = mock_response
            result = generate_dress_sketch(
                design_description="red dress",
                tool_context=ctx,
            )

        assert result == "Image generation returned no image"
