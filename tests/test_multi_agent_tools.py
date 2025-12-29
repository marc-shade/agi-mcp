"""
Tests for Multi-Agent Coordinator tools.

Covers:
- agi_execute_task
- agi_get_system_status
"""

import pytest
import json


@pytest.mark.asyncio
async def test_agi_execute_task_success(mock_app, mock_coordinator):
    """Test successful task execution."""
    import server

    result = await server.agi_execute_task(
        description="Implement user authentication",
        task_type="code_generation"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert "result" in data
    assert data["result"]["task_id"] == "test_task"
    assert data["result"]["status"] == "completed"

    mock_coordinator.execute_task.assert_called_once_with(
        "Implement user authentication",
        "code_generation"
    )


@pytest.mark.asyncio
async def test_agi_execute_task_default_type(mock_app, mock_coordinator):
    """Test task execution with default task type."""
    import server

    result = await server.agi_execute_task(
        description="Analyze system performance"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    mock_coordinator.execute_task.assert_called_once_with(
        "Analyze system performance",
        "general"
    )


@pytest.mark.asyncio
async def test_agi_execute_task_validation():
    """Test parameter validation for execute_task."""
    import server

    # Test with missing required parameter
    with pytest.raises(TypeError):
        await server.agi_execute_task()  # Missing description


@pytest.mark.asyncio
async def test_agi_execute_task_with_subtasks(mock_app, mock_coordinator):
    """Test task execution returning subtasks."""
    import server

    # Update mock to return subtasks
    mock_coordinator.execute_task.return_value = {
        "task_id": "complex_task",
        "status": "completed",
        "subtasks": [
            {"id": "st1", "status": "done"},
            {"id": "st2", "status": "done"}
        ]
    }

    result = await server.agi_execute_task(
        description="Complex multi-step task",
        task_type="refactoring"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert len(data["result"]["subtasks"]) == 2


@pytest.mark.asyncio
async def test_agi_get_system_status(mock_app, mock_coordinator):
    """Test getting system status."""
    import server

    result = await server.agi_get_system_status()

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert "system_status" in data
    assert data["system_status"]["agents"] == ["agent1", "agent2"]
    assert data["system_status"]["active_sessions"] == 2
    assert data["system_status"]["health"] == "healthy"

    mock_coordinator.get_system_status.assert_called_once()


@pytest.mark.asyncio
async def test_agi_get_system_status_unhealthy(mock_app, mock_coordinator):
    """Test system status when system is unhealthy."""
    import server

    # Update mock to return unhealthy status
    mock_coordinator.get_system_status.return_value = {
        "agents": ["agent1"],
        "active_sessions": 10,
        "health": "degraded",
        "errors": ["High load"]
    }

    result = await server.agi_get_system_status()

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["system_status"]["health"] == "degraded"
    assert "errors" in data["system_status"]


@pytest.mark.asyncio
async def test_execute_task_error_handling(mock_app, mock_coordinator):
    """Test error handling in task execution."""
    import server

    # Make the mock raise an exception
    mock_coordinator.execute_task.side_effect = Exception("Execution failed")

    result = await server.agi_execute_task(
        description="Failing task",
        task_type="test"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Execution failed" in data["message"]


@pytest.mark.asyncio
async def test_system_status_error_handling(mock_app, mock_coordinator):
    """Test error handling in system status."""
    import server

    # Make the mock raise an exception
    mock_coordinator.get_system_status.side_effect = Exception("Status unavailable")

    result = await server.agi_get_system_status()

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Status unavailable" in data["message"]
