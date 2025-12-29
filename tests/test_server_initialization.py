"""
Tests for server initialization and configuration.

Covers:
- Tool definitions
- Schema validation
- Server setup
"""

import pytest
import json


def test_tool_schemas_completeness():
    """Test that all tools have complete schemas."""
    import server

    # Verify all tools have schemas
    for tool_name, _ in server.TOOL_DEFINITIONS:
        assert tool_name in server.TOOL_SCHEMAS, f"Missing schema for {tool_name}"


def test_tool_schemas_structure():
    """Test that all tool schemas have correct structure."""
    import server

    for tool_name, schema in server.TOOL_SCHEMAS.items():
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert isinstance(schema["required"], list)


def test_tool_definitions_count():
    """Test that we have exactly 15 tool definitions."""
    import server

    assert len(server.TOOL_DEFINITIONS) == 15
    assert len(server.TOOL_SCHEMAS) == 15
    assert len(server.TOOLS) == 15


def test_tool_definitions_categories():
    """Test that tools are organized by category."""
    import server

    tool_names = [name for name, _ in server.TOOL_DEFINITIONS]

    # Meta-learning tools (4)
    meta_learning_tools = [
        "agi_record_outcome",
        "agi_recommend_agent",
        "agi_detect_patterns",
        "agi_get_learning_summary"
    ]
    for tool in meta_learning_tools:
        assert tool in tool_names

    # Multi-agent coordination tools (2)
    coordinator_tools = [
        "agi_execute_task",
        "agi_get_system_status"
    ]
    for tool in coordinator_tools:
        assert tool in tool_names

    # Skill evolution tools (3)
    skill_tools = [
        "agi_register_skill",
        "agi_start_ab_test",
        "agi_promote_skill"
    ]
    for tool in skill_tools:
        assert tool in tool_names

    # Goal decomposition tools (2)
    goal_tools = [
        "agi_execute_goal",
        "agi_get_goal_progress"
    ]
    for tool in goal_tools:
        assert tool in tool_names

    # Context synthesis tools (1)
    context_tools = ["agi_synthesize_context"]
    for tool in context_tools:
        assert tool in tool_names

    # Darwin Gödel tools (3)
    darwin_tools = [
        "agi_propose_modification",
        "agi_apply_modification",
        "agi_get_improvement_history"
    ]
    for tool in darwin_tools:
        assert tool in tool_names


def test_tool_naming_convention():
    """Test that all tools follow agi_ naming convention."""
    import server

    for tool_name, _ in server.TOOL_DEFINITIONS:
        assert tool_name.startswith("agi_"), f"Tool {tool_name} doesn't follow naming convention"


def test_required_parameters():
    """Test that required parameters are correctly defined."""
    import server

    # Tools with no required parameters
    no_required = [
        "agi_detect_patterns",
        "agi_get_learning_summary",
        "agi_get_system_status",
        "agi_get_improvement_history"
    ]

    for tool_name in no_required:
        assert server.TOOL_SCHEMAS[tool_name]["required"] == []

    # Tools with required parameters
    assert "task_id" in server.TOOL_SCHEMAS["agi_record_outcome"]["required"]
    assert "task_type" in server.TOOL_SCHEMAS["agi_recommend_agent"]["required"]
    assert "skill_name" in server.TOOL_SCHEMAS["agi_register_skill"]["required"]
    assert "goal_description" in server.TOOL_SCHEMAS["agi_execute_goal"]["required"]


def test_optional_parameters():
    """Test that optional parameters are correctly defined."""
    import server

    # Check optional parameters are not in required list
    schema = server.TOOL_SCHEMAS["agi_record_outcome"]
    assert "quality_score" not in schema["required"]
    assert "error_message" not in schema["required"]
    assert "context" not in schema["required"]

    # But they should be in properties
    assert "quality_score" in schema["properties"]
    assert "error_message" in schema["properties"]
    assert "context" in schema["properties"]


def test_enum_parameters():
    """Test that enum parameters are correctly defined."""
    import server

    # Check modification_type has enum values
    schema = server.TOOL_SCHEMAS["agi_propose_modification"]
    mod_type_schema = schema["properties"]["modification_type"]

    assert "enum" in mod_type_schema
    expected_types = ["algorithm_improve", "data_structure", "interface", "optimization"]
    assert mod_type_schema["enum"] == expected_types


def test_default_values():
    """Test that default values are correctly defined."""
    import server

    # Check default values
    assert server.TOOL_SCHEMAS["agi_detect_patterns"]["properties"]["lookback_days"]["default"] == 7
    assert server.TOOL_SCHEMAS["agi_execute_task"]["properties"]["task_type"]["default"] == "general"
    assert server.TOOL_SCHEMAS["agi_start_ab_test"]["properties"]["split_ratio"]["default"] == 0.5
    assert server.TOOL_SCHEMAS["agi_get_improvement_history"]["properties"]["limit"]["default"] == 10


def test_parameter_types():
    """Test that parameter types are correctly defined."""
    import server

    # String parameters
    assert server.TOOL_SCHEMAS["agi_record_outcome"]["properties"]["task_id"]["type"] == "string"

    # Boolean parameters
    assert server.TOOL_SCHEMAS["agi_record_outcome"]["properties"]["success"]["type"] == "boolean"

    # Integer parameters
    assert server.TOOL_SCHEMAS["agi_record_outcome"]["properties"]["execution_time_ms"]["type"] == "integer"

    # Number parameters (float)
    assert server.TOOL_SCHEMAS["agi_record_outcome"]["properties"]["quality_score"]["type"] == "number"

    # Object parameters
    assert server.TOOL_SCHEMAS["agi_record_outcome"]["properties"]["context"]["type"] == "object"

    # Array parameters
    assert server.TOOL_SCHEMAS["agi_synthesize_context"]["properties"]["source_types"]["type"] == "array"


@pytest.mark.asyncio
async def test_list_tools(mock_app):
    """Test that list_tools returns all tools."""
    import server

    tools = await server.list_tools()

    assert len(tools) == 15
    for tool in tools:
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, 'inputSchema')


def test_tool_descriptions():
    """Test that all tools have meaningful descriptions."""
    import server

    for tool_name, description in server.TOOL_DEFINITIONS:
        assert len(description) > 10, f"Tool {tool_name} has too short description"
        assert description[0].isupper(), f"Tool {tool_name} description should start with uppercase"


def test_component_initialization():
    """Test that all AGI components are initialized."""
    import server

    # These should be initialized on module import
    assert server.meta_learning is not None
    assert server.coordinator is not None
    assert server.skill_evolution is not None
    assert server.goal_ai is not None
    assert server.context_engine is not None
    assert server.darwin_godel is not None


def test_server_instance():
    """Test that MCP server instance is created."""
    import server

    assert server.app is not None
    assert hasattr(server.app, 'list_tools')
    assert hasattr(server.app, 'call_tool')


def test_logging_configuration():
    """Test that logging is properly configured."""
    import server
    import logging

    # Verify logger exists
    assert server.logger is not None
    assert isinstance(server.logger, logging.Logger)
    assert server.logger.name == "server"
