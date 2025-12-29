"""
Tests for Meta-Learning Engine tools.

Covers:
- agi_record_outcome
- agi_recommend_agent
- agi_detect_patterns
- agi_get_learning_summary
"""

import pytest
import json
from datetime import datetime


@pytest.mark.asyncio
async def test_agi_record_outcome_success(mock_app, mock_meta_learning):
    """Test successfully recording a task outcome."""
    import server

    result = await server.agi_record_outcome(
        task_id="task_001",
        task_type="code_generation",
        agent_used="coder",
        success=True,
        execution_time_ms=1500,
        quality_score=0.9
    )

    # Verify result structure
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["message"] == "Recorded outcome for task task_001"
    assert data["outcome"]["task_type"] == "code_generation"
    assert data["outcome"]["agent"] == "coder"
    assert data["outcome"]["success"] is True

    # Verify meta_learning was called
    mock_meta_learning.record_outcome.assert_called_once()
    call_args = mock_meta_learning.record_outcome.call_args[0][0]
    assert call_args.task_id == "task_001"
    assert call_args.quality_score == 0.9


@pytest.mark.asyncio
async def test_agi_record_outcome_with_error(mock_app, mock_meta_learning):
    """Test recording a failed task outcome with error message."""
    import server

    result = await server.agi_record_outcome(
        task_id="task_002",
        task_type="analysis",
        agent_used="analyzer",
        success=False,
        execution_time_ms=3000,
        error_message="Timeout error"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["outcome"]["success"] is False

    call_args = mock_meta_learning.record_outcome.call_args[0][0]
    assert call_args.error_message == "Timeout error"


@pytest.mark.asyncio
async def test_agi_record_outcome_validation():
    """Test parameter validation for record_outcome."""
    import server

    # Test with missing required parameters
    with pytest.raises(TypeError):
        await server.agi_record_outcome(
            task_id="task_003",
            task_type="test"
            # Missing required: agent_used, success, execution_time_ms
        )


@pytest.mark.asyncio
async def test_agi_record_outcome_with_context(mock_app, mock_meta_learning):
    """Test recording outcome with additional context."""
    import server

    context = {"complexity": "high", "framework": "FastAPI"}

    result = await server.agi_record_outcome(
        task_id="task_004",
        task_type="code_generation",
        agent_used="coder",
        success=True,
        execution_time_ms=2000,
        context=context
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    call_args = mock_meta_learning.record_outcome.call_args[0][0]
    assert call_args.context == context


@pytest.mark.asyncio
async def test_agi_recommend_agent_success(mock_app, mock_meta_learning):
    """Test getting agent recommendation."""
    import server

    result = await server.agi_recommend_agent(
        task_type="code_generation"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["recommended_agent"] == "test_agent"
    assert data["confidence"] == 0.85
    assert data["task_type"] == "code_generation"

    mock_meta_learning.recommend_agent.assert_called_once_with(
        "code_generation", None
    )


@pytest.mark.asyncio
async def test_agi_recommend_agent_with_context(mock_app, mock_meta_learning):
    """Test agent recommendation with context."""
    import server

    context = {"language": "python", "complexity": "medium"}

    result = await server.agi_recommend_agent(
        task_type="refactoring",
        context=context
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    mock_meta_learning.recommend_agent.assert_called_once_with(
        "refactoring", context
    )


@pytest.mark.asyncio
async def test_agi_detect_patterns_default(mock_app, mock_meta_learning):
    """Test pattern detection with default lookback."""
    import server

    result = await server.agi_detect_patterns()

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["patterns_detected"] == 1
    assert data["lookback_days"] == 7
    assert len(data["patterns"]) == 1
    assert data["patterns"][0]["pattern"] == "high_success_rate"

    mock_meta_learning.detect_patterns.assert_called_once_with(7)


@pytest.mark.asyncio
async def test_agi_detect_patterns_custom_lookback(mock_app, mock_meta_learning):
    """Test pattern detection with custom lookback period."""
    import server

    result = await server.agi_detect_patterns(lookback_days=30)

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["lookback_days"] == 30

    mock_meta_learning.detect_patterns.assert_called_once_with(30)


@pytest.mark.asyncio
async def test_agi_get_learning_summary(mock_app, mock_meta_learning):
    """Test getting learning summary."""
    import server

    result = await server.agi_get_learning_summary()

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert "summary" in data
    assert data["summary"]["total_outcomes"] == 100
    assert data["summary"]["success_rate"] == 0.85
    assert "test_agent" in data["summary"]["top_agents"]

    mock_meta_learning.get_learning_summary.assert_called_once()


@pytest.mark.asyncio
async def test_error_handling(mock_app, mock_meta_learning):
    """Test error handling in meta-learning tools."""
    import server

    # Make the mock raise an exception
    mock_meta_learning.recommend_agent.side_effect = Exception("Test error")

    result = await server.agi_recommend_agent(task_type="test")

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Test error" in data["message"]
