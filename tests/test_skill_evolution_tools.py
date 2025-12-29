"""
Tests for Skill Evolution System tools.

Covers:
- agi_register_skill
- agi_start_ab_test
- agi_promote_skill
"""

import pytest
import json
from datetime import datetime


@pytest.mark.asyncio
async def test_agi_register_skill_success(mock_app, mock_skill_evolution):
    """Test successful skill registration."""
    import server

    result = await server.agi_register_skill(
        skill_name="data_processor",
        code="def process(data): return [x*2 for x in data]",
        description="Data processing skill",
        version="v1.0"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["skill"]["name"] == "test_skill"
    assert data["skill"]["version"] == "v1"
    assert "created_at" in data["skill"]

    mock_skill_evolution.register_skill.assert_called_once_with(
        "data_processor",
        "def process(data): return [x*2 for x in data]",
        "Data processing skill",
        "v1.0"
    )


@pytest.mark.asyncio
async def test_agi_register_skill_auto_version(mock_app, mock_skill_evolution):
    """Test skill registration with auto-generated version."""
    import server

    result = await server.agi_register_skill(
        skill_name="analyzer",
        code="def analyze(data): pass"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    # Version should be auto-generated (passed as None)
    call_args = mock_skill_evolution.register_skill.call_args[0]
    assert call_args[3] is None  # version parameter


@pytest.mark.asyncio
async def test_agi_register_skill_validation():
    """Test parameter validation for register_skill."""
    import server

    # Test with missing required parameter
    with pytest.raises(TypeError):
        await server.agi_register_skill(
            skill_name="test"
            # Missing required: code
        )


@pytest.mark.asyncio
async def test_agi_register_skill_empty_code(mock_app, mock_skill_evolution):
    """Test registering skill with empty code."""
    import server

    result = await server.agi_register_skill(
        skill_name="empty_skill",
        code=""
    )

    # Should still succeed (validation happens in the skill system)
    data = json.loads(result[0].text)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_agi_start_ab_test_success(mock_app, mock_skill_evolution):
    """Test starting an A/B test."""
    import server

    result = await server.agi_start_ab_test(
        skill_name="optimizer",
        version_a="v1.0",
        version_b="v2.0",
        split_ratio=0.5
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["test_id"] == "test_id_123"
    assert data["skill_name"] == "optimizer"
    assert data["version_a"] == "v1.0"
    assert data["version_b"] == "v2.0"
    assert data["split_ratio"] == 0.5

    mock_skill_evolution.start_ab_test.assert_called_once_with(
        "optimizer", "v1.0", "v2.0", 0.5
    )


@pytest.mark.asyncio
async def test_agi_start_ab_test_default_split(mock_app, mock_skill_evolution):
    """Test A/B test with default 50/50 split."""
    import server

    result = await server.agi_start_ab_test(
        skill_name="processor",
        version_a="v1",
        version_b="v2"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["split_ratio"] == 0.5


@pytest.mark.asyncio
async def test_agi_start_ab_test_custom_split(mock_app, mock_skill_evolution):
    """Test A/B test with custom traffic split."""
    import server

    result = await server.agi_start_ab_test(
        skill_name="analyzer",
        version_a="v1",
        version_b="v2",
        split_ratio=0.3  # 30% to A, 70% to B
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["split_ratio"] == 0.3

    mock_skill_evolution.start_ab_test.assert_called_once_with(
        "analyzer", "v1", "v2", 0.3
    )


@pytest.mark.asyncio
async def test_agi_start_ab_test_validation():
    """Test parameter validation for start_ab_test."""
    import server

    # Test with missing required parameters
    with pytest.raises(TypeError):
        await server.agi_start_ab_test(
            skill_name="test"
            # Missing: version_a, version_b
        )


@pytest.mark.asyncio
async def test_agi_promote_skill_success(mock_app, mock_skill_evolution):
    """Test successful skill promotion."""
    import server

    result = await server.agi_promote_skill(
        skill_name="optimizer",
        version="v2.0"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["skill_name"] == "optimizer"
    assert data["promoted_version"] == "v2.0"

    mock_skill_evolution.promote_version.assert_called_once_with(
        "optimizer", "v2.0"
    )


@pytest.mark.asyncio
async def test_agi_promote_skill_failed(mock_app, mock_skill_evolution):
    """Test skill promotion failure."""
    import server

    # Make the mock return False (promotion failed)
    mock_skill_evolution.promote_version.return_value = False

    result = await server.agi_promote_skill(
        skill_name="nonexistent",
        version="v1.0"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "failed"


@pytest.mark.asyncio
async def test_agi_promote_skill_validation():
    """Test parameter validation for promote_skill."""
    import server

    # Test with missing required parameter
    with pytest.raises(TypeError):
        await server.agi_promote_skill(
            skill_name="test"
            # Missing: version
        )


@pytest.mark.asyncio
async def test_skill_evolution_error_handling(mock_app, mock_skill_evolution):
    """Test error handling in skill evolution tools."""
    import server

    # Make the mock raise an exception
    mock_skill_evolution.register_skill.side_effect = Exception("Registration error")

    result = await server.agi_register_skill(
        skill_name="failing_skill",
        code="def fail(): pass"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Registration error" in data["message"]
