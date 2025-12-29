"""
Tests for Darwin Gödel Machine tools.

Covers:
- agi_propose_modification
- agi_apply_modification
- agi_get_improvement_history
"""

import pytest
import json


@pytest.mark.asyncio
async def test_agi_propose_modification_success(mock_app, mock_darwin_godel):
    """Test successful modification proposal."""
    import server

    code_before = "def old_algo(n): return sum(range(n))"
    code_after = "def new_algo(n): return (n * (n - 1)) // 2"

    result = await server.agi_propose_modification(
        code_before=code_before,
        code_after=code_after,
        modification_type="algorithm_improve",
        description="Optimize from O(n) to O(1)"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["modification_id"] == "mod_123"
    assert data["type"] == "algorithm_improve"
    # The mock returns a fixed description, so we check for that
    assert data["description"] == "Test modification"
    assert data["proof_status"] == "verified"

    # Verify the mock was called correctly
    mock_darwin_godel.propose_modification.assert_called_once()


@pytest.mark.asyncio
async def test_agi_propose_modification_all_types(mock_app, mock_darwin_godel):
    """Test proposing modifications of all types."""
    import server

    modification_types = [
        "algorithm_improve",
        "data_structure",
        "interface",
        "optimization"
    ]

    for mod_type in modification_types:
        result = await server.agi_propose_modification(
            code_before="old code",
            code_after="new code",
            modification_type=mod_type,
            description=f"Test {mod_type}"
        )

        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["type"] == "algorithm_improve"  # Mock always returns this


@pytest.mark.asyncio
async def test_agi_propose_modification_validation():
    """Test parameter validation for propose_modification."""
    import server

    # Test with missing required parameters
    with pytest.raises(TypeError):
        await server.agi_propose_modification(
            code_before="old",
            code_after="new"
            # Missing: modification_type, description
        )


@pytest.mark.asyncio
async def test_agi_propose_modification_invalid_type(mock_app, mock_darwin_godel):
    """Test proposing modification with invalid type."""
    import server

    # Make the mock raise an exception for invalid type
    mock_darwin_godel.propose_modification.side_effect = KeyError("INVALID_TYPE")

    result = await server.agi_propose_modification(
        code_before="old",
        code_after="new",
        modification_type="invalid_type",
        description="Test"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "error"


@pytest.mark.asyncio
async def test_agi_propose_modification_large_diff(mock_app, mock_darwin_godel):
    """Test proposing modification with large code diff."""
    import server

    # Simulate large code change
    code_before = "def func():\n" + "    pass\n" * 100
    code_after = "def func():\n" + "    return None\n" * 100

    result = await server.agi_propose_modification(
        code_before=code_before,
        code_after=code_after,
        modification_type="optimization",
        description="Large refactoring"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_agi_apply_modification_success(mock_app, mock_darwin_godel):
    """Test successful modification application."""
    import server

    result = await server.agi_apply_modification(
        modification_id="mod_123"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "info"  # Returns info status
    assert data["modification_id"] == "mod_123"
    assert "current_status" in data

    mock_darwin_godel.get_improvement_history.assert_called_once()


@pytest.mark.asyncio
async def test_agi_apply_modification_not_found(mock_app, mock_darwin_godel):
    """Test applying nonexistent modification."""
    import server

    # Update mock to return empty history
    mock_darwin_godel.get_improvement_history.return_value = []

    result = await server.agi_apply_modification(
        modification_id="nonexistent"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "not found" in data["message"]


@pytest.mark.asyncio
async def test_agi_apply_modification_validation():
    """Test parameter validation for apply_modification."""
    import server

    # Test with missing required parameter
    with pytest.raises(TypeError):
        await server.agi_apply_modification()  # Missing modification_id


@pytest.mark.asyncio
async def test_agi_get_improvement_history_success(mock_app, mock_darwin_godel):
    """Test getting improvement history."""
    import server

    result = await server.agi_get_improvement_history()

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert "history" in data
    assert len(data["history"]) == 1
    assert data["history"][0]["modification_id"] == "mod_123"
    assert data["history"][0]["status"] == "applied"
    assert data["history"][0]["performance_impact"] == 1.2

    mock_darwin_godel.get_improvement_history.assert_called_once_with(10)


@pytest.mark.asyncio
async def test_agi_get_improvement_history_custom_limit(mock_app, mock_darwin_godel):
    """Test getting improvement history with custom limit."""
    import server

    result = await server.agi_get_improvement_history(limit=50)

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    mock_darwin_godel.get_improvement_history.assert_called_once_with(50)


@pytest.mark.asyncio
async def test_agi_get_improvement_history_empty(mock_app, mock_darwin_godel):
    """Test getting improvement history when empty."""
    import server

    # Update mock to return empty history
    mock_darwin_godel.get_improvement_history.return_value = []

    result = await server.agi_get_improvement_history()

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert len(data["history"]) == 0


@pytest.mark.asyncio
async def test_agi_get_improvement_history_large_limit(mock_app, mock_darwin_godel):
    """Test getting improvement history with large limit."""
    import server

    # Update mock to return many items
    mock_darwin_godel.get_improvement_history.return_value = [
        {"modification_id": f"mod_{i}", "status": "applied"}
        for i in range(100)
    ]

    result = await server.agi_get_improvement_history(limit=100)

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert len(data["history"]) == 100


@pytest.mark.asyncio
async def test_darwin_godel_error_handling(mock_app, mock_darwin_godel):
    """Test error handling in Darwin Gödel tools."""
    import server

    # Make the mock raise an exception
    mock_darwin_godel.propose_modification.side_effect = Exception("Proof failed")

    result = await server.agi_propose_modification(
        code_before="old",
        code_after="new",
        modification_type="optimization",
        description="Failing modification"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Proof failed" in data["message"]


@pytest.mark.asyncio
async def test_agi_get_improvement_history_error_handling(mock_app, mock_darwin_godel):
    """Test error handling in improvement history retrieval."""
    import server

    # Make the mock raise an exception
    mock_darwin_godel.get_improvement_history.side_effect = Exception("Database error")

    result = await server.agi_get_improvement_history()

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Database error" in data["message"]
