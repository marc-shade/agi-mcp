"""
Tests for Goal Decomposition AI tools.

Covers:
- agi_execute_goal
- agi_get_goal_progress
"""

import pytest
import json


@pytest.mark.asyncio
async def test_agi_execute_goal_success(mock_app, mock_goal_ai):
    """Test successful goal execution."""
    import server

    result = await server.agi_execute_goal(
        goal_description="Build a REST API for user management",
        context={"language": "Python", "framework": "FastAPI"}
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert "result" in data
    assert data["result"]["goal_id"] == "goal_123"
    assert data["result"]["status"] == "in_progress"
    assert len(data["result"]["tasks"]) == 1

    mock_goal_ai.execute_goal.assert_called_once_with(
        "Build a REST API for user management",
        {"language": "Python", "framework": "FastAPI"}
    )


@pytest.mark.asyncio
async def test_agi_execute_goal_no_context(mock_app, mock_goal_ai):
    """Test goal execution without context."""
    import server

    result = await server.agi_execute_goal(
        goal_description="Refactor authentication module"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    # Context should be None when not provided
    call_args = mock_goal_ai.execute_goal.call_args[0]
    assert call_args[1] is None


@pytest.mark.asyncio
async def test_agi_execute_goal_validation():
    """Test parameter validation for execute_goal."""
    import server

    # Test with missing required parameter
    with pytest.raises(TypeError):
        await server.agi_execute_goal()  # Missing goal_description


@pytest.mark.asyncio
async def test_agi_execute_goal_empty_description(mock_app, mock_goal_ai):
    """Test goal execution with empty description."""
    import server

    result = await server.agi_execute_goal(
        goal_description=""
    )

    # Should still call the underlying function
    data = json.loads(result[0].text)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_agi_execute_goal_complex_context(mock_app, mock_goal_ai):
    """Test goal execution with complex context."""
    import server

    complex_context = {
        "language": "TypeScript",
        "framework": "Next.js",
        "constraints": ["no external libraries", "must be responsive"],
        "target_performance": {"load_time": 2000},
        "nested": {"key": "value"}
    }

    result = await server.agi_execute_goal(
        goal_description="Build dashboard",
        context=complex_context
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    call_args = mock_goal_ai.execute_goal.call_args[0]
    assert call_args[1] == complex_context


@pytest.mark.asyncio
async def test_agi_get_goal_progress_success(mock_app, mock_goal_ai):
    """Test getting goal progress."""
    import server

    result = await server.agi_get_goal_progress(
        goal_id="goal_123"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert "progress" in data
    assert data["progress"]["goal_id"] == "goal_123"
    assert data["progress"]["completed"] == 2
    assert data["progress"]["total"] == 5
    assert data["progress"]["progress"] == 0.4

    mock_goal_ai.get_goal_progress.assert_called_once_with("goal_123")


@pytest.mark.asyncio
async def test_agi_get_goal_progress_validation():
    """Test parameter validation for get_goal_progress."""
    import server

    # Test with missing required parameter
    with pytest.raises(TypeError):
        await server.agi_get_goal_progress()  # Missing goal_id


@pytest.mark.asyncio
async def test_agi_get_goal_progress_nonexistent(mock_app, mock_goal_ai):
    """Test getting progress for nonexistent goal."""
    import server

    # Update mock to return None or empty progress
    mock_goal_ai.get_goal_progress.return_value = {
        "goal_id": "nonexistent",
        "error": "Goal not found"
    }

    result = await server.agi_get_goal_progress(
        goal_id="nonexistent"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert "error" in data["progress"]


@pytest.mark.asyncio
async def test_agi_get_goal_progress_completed(mock_app, mock_goal_ai):
    """Test getting progress for completed goal."""
    import server

    # Update mock to return completed status
    mock_goal_ai.get_goal_progress.return_value = {
        "goal_id": "goal_456",
        "completed": 10,
        "total": 10,
        "progress": 1.0,
        "status": "completed"
    }

    result = await server.agi_get_goal_progress(
        goal_id="goal_456"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["progress"]["progress"] == 1.0
    assert data["progress"]["status"] == "completed"


@pytest.mark.asyncio
async def test_execute_goal_error_handling(mock_app, mock_goal_ai):
    """Test error handling in goal execution."""
    import server

    # Make the mock raise an exception
    mock_goal_ai.execute_goal.side_effect = Exception("Goal execution failed")

    result = await server.agi_execute_goal(
        goal_description="Failing goal"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Goal execution failed" in data["message"]


@pytest.mark.asyncio
async def test_get_goal_progress_error_handling(mock_app, mock_goal_ai):
    """Test error handling in goal progress retrieval."""
    import server

    # Make the mock raise an exception
    mock_goal_ai.get_goal_progress.side_effect = Exception("Progress unavailable")

    result = await server.agi_get_goal_progress(
        goal_id="goal_789"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Progress unavailable" in data["message"]
