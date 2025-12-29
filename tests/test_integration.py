"""
Integration tests for AGI MCP Server.

Tests the integration between multiple tools and components.
"""

import pytest
import json


@pytest.mark.asyncio
async def test_full_workflow_meta_learning(mock_app, mock_meta_learning, mock_coordinator):
    """Test full workflow: execute task -> record outcome -> get recommendation."""
    import server

    # Step 1: Execute a task
    execute_result = await server.agi_execute_task(
        description="Generate authentication code",
        task_type="code_generation"
    )
    execute_data = json.loads(execute_result[0].text)
    assert execute_data["status"] == "success"

    # Step 2: Record the outcome
    outcome_result = await server.agi_record_outcome(
        task_id=execute_data["result"]["task_id"],
        task_type="code_generation",
        agent_used="coder",
        success=True,
        execution_time_ms=2000,
        quality_score=0.9
    )
    outcome_data = json.loads(outcome_result[0].text)
    assert outcome_data["status"] == "success"

    # Step 3: Get recommendation for similar task
    recommend_result = await server.agi_recommend_agent(
        task_type="code_generation"
    )
    recommend_data = json.loads(recommend_result[0].text)
    assert recommend_data["status"] == "success"
    assert recommend_data["recommended_agent"] == "test_agent"


@pytest.mark.asyncio
async def test_full_workflow_skill_evolution(mock_app, mock_skill_evolution):
    """Test full workflow: register skill -> A/B test -> promote."""
    import server

    # Step 1: Register version 1
    register_v1 = await server.agi_register_skill(
        skill_name="optimizer",
        code="def optimize_v1(data): return data",
        version="v1.0"
    )
    v1_data = json.loads(register_v1[0].text)
    assert v1_data["status"] == "success"

    # Step 2: Register version 2
    register_v2 = await server.agi_register_skill(
        skill_name="optimizer",
        code="def optimize_v2(data): return [x*2 for x in data]",
        version="v2.0"
    )
    v2_data = json.loads(register_v2[0].text)
    assert v2_data["status"] == "success"

    # Step 3: Start A/B test
    test_result = await server.agi_start_ab_test(
        skill_name="optimizer",
        version_a="v1.0",
        version_b="v2.0"
    )
    test_data = json.loads(test_result[0].text)
    assert test_data["status"] == "success"

    # Step 4: Promote winning version
    promote_result = await server.agi_promote_skill(
        skill_name="optimizer",
        version="v2.0"
    )
    promote_data = json.loads(promote_result[0].text)
    assert promote_data["status"] == "success"


@pytest.mark.asyncio
async def test_full_workflow_goal_execution(mock_app, mock_goal_ai, mock_coordinator):
    """Test full workflow: execute goal -> track progress -> execute subtasks."""
    import server

    # Step 1: Execute high-level goal
    goal_result = await server.agi_execute_goal(
        goal_description="Build user authentication system",
        context={"language": "Python", "framework": "FastAPI"}
    )
    goal_data = json.loads(goal_result[0].text)
    assert goal_data["status"] == "success"
    goal_id = goal_data["result"]["goal_id"]

    # Step 2: Check progress
    progress_result = await server.agi_get_goal_progress(
        goal_id=goal_id
    )
    progress_data = json.loads(progress_result[0].text)
    assert progress_data["status"] == "success"
    assert progress_data["progress"]["goal_id"] == goal_id

    # Step 3: Execute a subtask
    task_result = await server.agi_execute_task(
        description="Implement JWT token generation",
        task_type="code_generation"
    )
    task_data = json.loads(task_result[0].text)
    assert task_data["status"] == "success"


@pytest.mark.asyncio
async def test_full_workflow_self_improvement(mock_app, mock_darwin_godel):
    """Test full workflow: propose modification -> verify -> apply -> track history."""
    import server

    # Step 1: Propose improvement
    propose_result = await server.agi_propose_modification(
        code_before="def slow_algo(n): return sum(range(n))",
        code_after="def fast_algo(n): return (n * (n - 1)) // 2",
        modification_type="algorithm_improve",
        description="Optimize from O(n) to O(1)"
    )
    propose_data = json.loads(propose_result[0].text)
    assert propose_data["status"] == "success"
    mod_id = propose_data["modification_id"]

    # Step 2: Apply modification
    apply_result = await server.agi_apply_modification(
        modification_id=mod_id
    )
    apply_data = json.loads(apply_result[0].text)
    assert "modification_id" in apply_data

    # Step 3: Check improvement history
    history_result = await server.agi_get_improvement_history()
    history_data = json.loads(history_result[0].text)
    assert history_data["status"] == "success"
    assert len(history_data["history"]) > 0


@pytest.mark.asyncio
async def test_cross_component_context_synthesis(mock_app, mock_context_engine, mock_meta_learning):
    """Test context synthesis using data from meta-learning."""
    import server

    # Step 1: Record some outcomes to populate meta-learning
    await server.agi_record_outcome(
        task_id="task_1",
        task_type="analysis",
        agent_used="analyzer",
        success=True,
        execution_time_ms=1500
    )

    # Step 2: Synthesize context about analysis tasks
    context_result = await server.agi_synthesize_context(
        query="analysis task performance",
        source_types=["memory", "file"]
    )
    context_data = json.loads(context_result[0].text)
    assert context_data["status"] == "success"
    assert context_data["context"]["chunks"] >= 0


@pytest.mark.asyncio
async def test_system_status_after_operations(mock_app, mock_coordinator, mock_meta_learning):
    """Test system status reflects recent operations."""
    import server

    # Execute some tasks
    await server.agi_execute_task(
        description="Task 1",
        task_type="test"
    )

    await server.agi_execute_task(
        description="Task 2",
        task_type="test"
    )

    # Check system status
    status_result = await server.agi_get_system_status()
    status_data = json.loads(status_result[0].text)
    assert status_data["status"] == "success"
    assert "agents" in status_data["system_status"]


@pytest.mark.asyncio
async def test_pattern_detection_after_outcomes(mock_app, mock_meta_learning):
    """Test pattern detection after recording multiple outcomes."""
    import server

    # Record multiple outcomes
    for i in range(5):
        await server.agi_record_outcome(
            task_id=f"task_{i}",
            task_type="code_generation",
            agent_used="coder",
            success=True,
            execution_time_ms=1000 + (i * 100)
        )

    # Detect patterns
    pattern_result = await server.agi_detect_patterns(lookback_days=1)
    pattern_data = json.loads(pattern_result[0].text)
    assert pattern_data["status"] == "success"


@pytest.mark.asyncio
async def test_learning_summary_aggregation(mock_app, mock_meta_learning):
    """Test learning summary aggregates data correctly."""
    import server

    # Record various outcomes
    await server.agi_record_outcome(
        task_id="success_1",
        task_type="code_generation",
        agent_used="coder",
        success=True,
        execution_time_ms=1000
    )

    await server.agi_record_outcome(
        task_id="failure_1",
        task_type="analysis",
        agent_used="analyzer",
        success=False,
        execution_time_ms=3000,
        error_message="Timeout"
    )

    # Get summary
    summary_result = await server.agi_get_learning_summary()
    summary_data = json.loads(summary_result[0].text)
    assert summary_data["status"] == "success"
    assert "total_outcomes" in summary_data["summary"]


@pytest.mark.asyncio
async def test_concurrent_tool_calls(mock_app, mock_coordinator, mock_meta_learning):
    """Test that multiple tools can be called concurrently."""
    import server
    import asyncio

    # Call multiple tools concurrently
    results = await asyncio.gather(
        server.agi_get_system_status(),
        server.agi_get_learning_summary(),
        server.agi_detect_patterns(),
        return_exceptions=True
    )

    # All should succeed
    for result in results:
        if isinstance(result, Exception):
            pytest.fail(f"Tool call failed: {result}")
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["status"] == "success"
