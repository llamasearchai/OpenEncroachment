"""
Tests for the OpenEncroachment agent functionality.
"""

import os
from unittest.mock import Mock, patch

import pytest

from open_encroachment.agents.agent import create_encroachment_agent, run_agent


class TestAgent:
    """Test cases for agent functionality."""

    def test_create_encroachment_agent(self):
        """Test creating the OpenEncroachment agent."""
        agent = create_encroachment_agent()
        assert agent.name == "OpenEncroachment Assistant"
        assert "OpenEncroachment" in agent.instructions
        assert len(agent.tools) == 3  # run_pipeline, severity_summary, package_notification

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("open_encroachment.agents.agent.Runner.run_sync")
    def test_run_agent_success(self, mock_runner):
        """Test successful agent execution."""
        mock_result = Mock()
        mock_result.final_output = "Test response"
        mock_runner.return_value = mock_result

        result = run_agent("Test prompt")

        assert result["ok"] is True
        assert result["output"] == "Test response"
        assert result["model"] == "gpt-4o-mini"
        mock_runner.assert_called_once()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("open_encroachment.agents.agent.Runner.run_sync")
    def test_run_agent_with_custom_model(self, mock_runner):
        """Test agent execution with custom model."""
        mock_result = Mock()
        mock_result.final_output = "Custom model response"
        mock_runner.return_value = mock_result

        result = run_agent("Test prompt", model="gpt-4")

        assert result["ok"] is True
        assert result["model"] == "gpt-4"
        mock_runner.assert_called_once()

    def test_run_agent_no_api_key(self):
        """Test agent execution without API key."""
        # Remove API key if it exists
        original_key = os.environ.get("OPENAI_API_KEY")
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        try:
            with pytest.raises(
                RuntimeError, match="OPENAI_API_KEY environment variable is required"
            ):
                run_agent("Test prompt")
        finally:
            # Restore original key
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("open_encroachment.agents.agent.Runner.run_sync")
    def test_run_agent_with_error(self, mock_runner):
        """Test agent execution with error."""
        mock_runner.side_effect = Exception("Test error")

        result = run_agent("Test prompt")

        assert result["ok"] is False
        assert "Test error" in result["error"]
        assert result["model"] == "gpt-4o-mini"
