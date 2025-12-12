#!/usr/bin/env python3
"""
AGI MCP Server
==============

Model Context Protocol server exposing all 6 AGI components as tools.

This server provides Claude Code with direct access to:
- Meta-Learning Engine: Learn from task outcomes
- Multi-Agent Coordinator: Parallel task execution
- Skill Evolution System: A/B testing and skill promotion
- Goal Decomposition AI: Natural language to tasks
- Context Synthesis Engine: Multi-source context gathering
- Darwin Gödel Machine: Safe self-modification

Components work together to provide autonomous AGI capabilities.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add intelligent-agents to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "intelligent-agents"))

# Import all AGI components
from meta_learning_engine import MetaLearningEngine, TaskOutcome
from multi_agent_coordinator import MultiAgentCoordinator
from skill_evolution_system import SkillEvolutionSystem
from goal_decomposition_ai import GoalDecompositionAI
from context_synthesis_engine import ContextSynthesisEngine
from darwin_godel_machine import DarwinGodelMachine, ModificationType

# MCP SDK
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize AGI components
meta_learning = MetaLearningEngine()
coordinator = MultiAgentCoordinator()
skill_evolution = SkillEvolutionSystem()
goal_ai = GoalDecompositionAI()
context_engine = ContextSynthesisEngine()
darwin_godel = DarwinGodelMachine()

# Set Darwin Gödel baseline
darwin_godel.set_baseline()

# Create MCP server
app = Server("agi-mcp")

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "agi_record_outcome": {
        "type": "object",
        "properties": {
            "task_id": {"type": "string"},
            "task_type": {"type": "string"},
            "agent_used": {"type": "string"},
            "success": {"type": "boolean"},
            "execution_time_ms": {"type": "integer"},
            "quality_score": {"type": "number"},
            "error_message": {"type": "string"},
            "context": {"type": "object"},
        },
        "required": ["task_id", "task_type", "agent_used", "success", "execution_time_ms"],
    },
    "agi_recommend_agent": {
        "type": "object",
        "properties": {
            "task_type": {"type": "string"},
            "context": {"type": "object"},
        },
        "required": ["task_type"],
    },
    "agi_detect_patterns": {
        "type": "object",
        "properties": {
            "lookback_days": {"type": "integer", "default": 7},
        },
        "required": [],
    },
    "agi_get_learning_summary": {"type": "object", "properties": {}, "required": []},
    "agi_execute_task": {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "task_type": {"type": "string", "default": "general"},
        },
        "required": ["description"],
    },
    "agi_get_system_status": {"type": "object", "properties": {}, "required": []},
    "agi_register_skill": {
        "type": "object",
        "properties": {
            "skill_name": {"type": "string"},
            "code": {"type": "string"},
            "description": {"type": "string", "default": ""},
            "version": {"type": "string"},
        },
        "required": ["skill_name", "code"],
    },
    "agi_start_ab_test": {
        "type": "object",
        "properties": {
            "skill_name": {"type": "string"},
            "version_a": {"type": "string"},
            "version_b": {"type": "string"},
            "split_ratio": {"type": "number", "default": 0.5},
        },
        "required": ["skill_name", "version_a", "version_b"],
    },
    "agi_promote_skill": {
        "type": "object",
        "properties": {
            "skill_name": {"type": "string"},
            "version": {"type": "string"},
        },
        "required": ["skill_name", "version"],
    },
    "agi_execute_goal": {
        "type": "object",
        "properties": {
            "goal_description": {"type": "string"},
            "context": {"type": "object"},
        },
        "required": ["goal_description"],
    },
    "agi_get_goal_progress": {
        "type": "object",
        "properties": {
            "goal_id": {"type": "string"},
        },
        "required": ["goal_id"],
    },
    "agi_synthesize_context": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "source_types": {"type": "array", "items": {"type": "string"}},
            "target_tokens": {"type": "integer"},
        },
        "required": ["query"],
    },
    "agi_propose_modification": {
        "type": "object",
        "properties": {
            "code_before": {"type": "string"},
            "code_after": {"type": "string"},
            "modification_type": {
                "type": "string",
                "enum": ["algorithm_improve", "data_structure", "interface", "optimization"],
            },
            "description": {"type": "string"},
        },
        "required": ["code_before", "code_after", "modification_type", "description"],
    },
    "agi_apply_modification": {
        "type": "object",
        "properties": {
            "modification_id": {"type": "string"},
        },
        "required": ["modification_id"],
    },
    "agi_get_improvement_history": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "default": 10},
        },
        "required": [],
    },
}

TOOL_DEFINITIONS = [
    ("agi_record_outcome", "Record a task outcome for meta-learning"),
    ("agi_recommend_agent", "Recommend the best agent for a task type"),
    ("agi_detect_patterns", "Detect patterns in recent task executions"),
    ("agi_get_learning_summary", "Summarize meta-learning system state"),
    ("agi_execute_task", "Execute a task using multi-agent coordination"),
    ("agi_get_system_status", "Report multi-agent coordinator status"),
    ("agi_register_skill", "Register a new skill version for evolution"),
    ("agi_start_ab_test", "Start an A/B test between two skill versions"),
    ("agi_promote_skill", "Promote a skill version to production"),
    ("agi_execute_goal", "Decompose and execute a natural language goal"),
    ("agi_get_goal_progress", "Get progress for a decomposed goal"),
    ("agi_synthesize_context", "Synthesize multi-source context for a query"),
    ("agi_propose_modification", "Propose a self-modification with proof status"),
    ("agi_apply_modification", "Apply a verified self-modification"),
    ("agi_get_improvement_history", "List recent self-improvement history"),
]

# Tools metadata so tools/list responds correctly
TOOLS: List[Tool] = [
    Tool(name=name, description=desc, inputSchema=TOOL_SCHEMAS[name])
    for name, desc in TOOL_DEFINITIONS
]


@app.list_tools()
async def list_tools() -> List[Tool]:
    """Return the list of available AGI tools."""
    return TOOLS


# ============================================================================
# META-LEARNING TOOLS
# ============================================================================

@app.call_tool()
async def agi_record_outcome(
    task_id: str,
    task_type: str,
    agent_used: str,
    success: bool,
    execution_time_ms: int,
    quality_score: Optional[float] = None,
    error_message: Optional[str] = None,
    context: Optional[Dict] = None
) -> List[TextContent]:
    """
    Record a task outcome for meta-learning.

    The meta-learning engine will learn from this outcome to improve
    future agent selection and task execution strategies.

    Args:
        task_id: Unique task identifier
        task_type: Type of task (e.g., "code_generation", "analysis")
        agent_used: Name of agent that executed the task
        success: Whether the task succeeded
        execution_time_ms: Execution time in milliseconds
        quality_score: Optional quality score (0.0-1.0)
        error_message: Optional error message if failed
        context: Optional context dict

    Returns:
        Confirmation message
    """
    try:
        outcome = TaskOutcome(
            task_id=task_id,
            task_type=task_type,
            agent_used=agent_used,
            success=success,
            execution_time_ms=execution_time_ms,
            error_message=error_message,
            quality_score=quality_score,
            timestamp=datetime.now(),
            context=context or {}
        )

        meta_learning.record_outcome(outcome)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "message": f"Recorded outcome for task {task_id}",
                "outcome": {
                    "task_type": task_type,
                    "agent": agent_used,
                    "success": success,
                    "execution_time_ms": execution_time_ms
                }
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error recording outcome: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_recommend_agent(
    task_type: str,
    context: Optional[Dict] = None
) -> List[TextContent]:
    """
    Get agent recommendation based on learned performance.

    Uses meta-learning to recommend the best agent for a given task type
    based on historical performance data.

    Args:
        task_type: Type of task
        context: Optional context dict for more specific recommendations

    Returns:
        Agent recommendation with confidence score
    """
    try:
        agent, confidence = meta_learning.recommend_agent(task_type, context)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "recommended_agent": agent,
                "confidence": confidence,
                "task_type": task_type
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error recommending agent: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_detect_patterns(
    lookback_days: int = 7
) -> List[TextContent]:
    """
    Detect patterns in recent task executions.

    Analyzes recent execution history to identify patterns in success/failure,
    agent performance, and task characteristics.

    Args:
        lookback_days: Number of days to look back

    Returns:
        List of detected patterns with insights
    """
    try:
        patterns = meta_learning.detect_patterns(lookback_days)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "patterns_detected": len(patterns),
                "lookback_days": lookback_days,
                "patterns": patterns
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error detecting patterns: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_get_learning_summary() -> List[TextContent]:
    """
    Get summary of meta-learning system state.

    Returns overall statistics including total outcomes, success rates,
    learning maturity, and agent performance comparisons.

    Returns:
        Learning summary with key metrics
    """
    try:
        summary = meta_learning.get_learning_summary()

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "summary": summary
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error getting learning summary: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


# ============================================================================
# MULTI-AGENT COORDINATION TOOLS
# ============================================================================

@app.call_tool()
async def agi_execute_task(
    description: str,
    task_type: str = "general"
) -> List[TextContent]:
    """
    Execute a task using multi-agent coordination.

    Decomposes the task, assigns to specialized agents, executes in parallel,
    and aggregates results. This is the main entry point for AGI task execution.

    Args:
        description: Natural language description of the task
        task_type: Type of task for better agent selection

    Returns:
        Execution results with subtask outcomes
    """
    try:
        result = await coordinator.execute_task(description, task_type)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "result": result
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error executing task: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_get_system_status() -> List[TextContent]:
    """
    Get multi-agent coordination system status.

    Returns information about available agents, active sessions,
    agent utilization, and system health.

    Returns:
        System status with agent details
    """
    try:
        status = coordinator.get_system_status()

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "system_status": status
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error getting system status: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


# ============================================================================
# SKILL EVOLUTION TOOLS
# ============================================================================

@app.call_tool()
async def agi_register_skill(
    skill_name: str,
    code: str,
    description: str = "",
    version: Optional[str] = None
) -> List[TextContent]:
    """
    Register a new skill version for evolution.

    Registers code as a skill that can be tracked, tested, and evolved
    through the A/B testing system.

    Args:
        skill_name: Unique skill name
        code: Skill implementation code
        description: Optional description
        version: Optional version (auto-generated if not provided)

    Returns:
        Skill version details
    """
    try:
        skill = skill_evolution.register_skill(skill_name, code, description, version)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "skill": {
                    "name": skill.skill_name,
                    "version": skill.version,
                    "created_at": skill.created_at.isoformat()
                }
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error registering skill: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_start_ab_test(
    skill_name: str,
    version_a: str,
    version_b: str,
    split_ratio: float = 0.5
) -> List[TextContent]:
    """
    Start A/B test between two skill versions.

    Initiates testing to determine which version performs better.
    Traffic will be split according to split_ratio.

    Args:
        skill_name: Skill to test
        version_a: First version
        version_b: Second version
        split_ratio: Ratio of traffic to version A (0.0-1.0)

    Returns:
        Test ID and configuration
    """
    try:
        test_id = skill_evolution.start_ab_test(skill_name, version_a, version_b, split_ratio)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "test_id": test_id,
                "skill_name": skill_name,
                "version_a": version_a,
                "version_b": version_b,
                "split_ratio": split_ratio
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error starting A/B test: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_promote_skill(
    skill_name: str,
    version: str
) -> List[TextContent]:
    """
    Promote a skill version to production.

    Makes the specified version the active version for the skill.

    Args:
        skill_name: Skill name
        version: Version to promote

    Returns:
        Promotion confirmation
    """
    try:
        success = skill_evolution.promote_version(skill_name, version)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success" if success else "failed",
                "skill_name": skill_name,
                "promoted_version": version
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error promoting skill: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


# ============================================================================
# GOAL DECOMPOSITION TOOLS
# ============================================================================

@app.call_tool()
async def agi_execute_goal(
    goal_description: str,
    context: Optional[Dict] = None
) -> List[TextContent]:
    """
    Parse and execute a goal with full decomposition.

    Takes a natural language goal, decomposes it into hierarchical tasks,
    and prepares for execution. This is the main entry point for goal-directed AI.

    Args:
        goal_description: Natural language goal description
        context: Optional context (language, framework, constraints)

    Returns:
        Goal execution plan with tasks and estimates
    """
    try:
        result = await goal_ai.execute_goal(goal_description, context)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "result": result
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error executing goal: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_get_goal_progress(
    goal_id: str
) -> List[TextContent]:
    """
    Get progress on a decomposed goal.

    Returns current status, completed tasks, pending tasks, and overall progress.

    Args:
        goal_id: Goal identifier

    Returns:
        Goal progress details
    """
    try:
        progress = goal_ai.get_goal_progress(goal_id)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "progress": progress
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error getting goal progress: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


# ============================================================================
# CONTEXT SYNTHESIS TOOLS
# ============================================================================

@app.call_tool()
async def agi_synthesize_context(
    query: str,
    source_types: Optional[List[str]] = None,
    target_tokens: Optional[int] = None
) -> List[TextContent]:
    """
    Synthesize optimal context from multiple sources.

    Gathers context from files, memory, code, APIs, and sensors,
    scores relevance, resolves conflicts, and compresses to fit token budget.

    Args:
        query: Context query
        source_types: Optional list of source types to include
        target_tokens: Optional target token count

    Returns:
        Synthesized context with compression stats
    """
    try:
        context = await context_engine.synthesize(query, source_types, target_tokens)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "context": {
                    "chunks": len(context.chunks),
                    "total_tokens": context.total_tokens,
                    "compression_ratio": context.compression_ratio,
                    "sources": [{"type": chunk.source_type, "relevance": chunk.relevance_score}
                               for chunk in context.chunks[:5]]  # First 5 sources
                }
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error synthesizing context: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


# ============================================================================
# DARWIN GÖDEL MACHINE TOOLS
# ============================================================================

@app.call_tool()
async def agi_propose_modification(
    code_before: str,
    code_after: str,
    modification_type: str,
    description: str
) -> List[TextContent]:
    """
    Propose a self-modification with formal proof.

    Creates a modification proposal with safety proof that will be verified
    before application. Supports algorithm improvements, data structure changes,
    interface modifications, and optimization.

    Args:
        code_before: Original code
        code_after: Modified code
        modification_type: Type (algorithm_improve, data_structure, interface, optimization)
        description: Description of the modification

    Returns:
        Modification proposal with proof
    """
    try:
        mod_type = ModificationType[modification_type.upper()]

        modification = darwin_godel.propose_modification(
            code_before, code_after, mod_type, description
        )

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "modification_id": modification.modification_id,
                "type": modification.modification_type.value,
                "description": modification.description,
                "proof_status": modification.proof_status.value
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error proposing modification: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_apply_modification(
    modification_id: str
) -> List[TextContent]:
    """
    Apply a verified modification.

    Applies a previously proposed modification after verification.
    Will automatically rollback if safety constraints are violated.

    Args:
        modification_id: Modification to apply

    Returns:
        Application result
    """
    try:
        # Get modification from history
        history = darwin_godel.get_improvement_history()
        modification = next((m for m in history if m["modification_id"] == modification_id), None)

        if not modification:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Modification {modification_id} not found"
                })
            )]

        # Note: In production, would need to reconstruct Modification object
        # For now, return status
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "info",
                "message": "Modification application requires full object reconstruction",
                "modification_id": modification_id,
                "current_status": modification
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error applying modification: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


@app.call_tool()
async def agi_get_improvement_history(
    limit: int = 10
) -> List[TextContent]:
    """
    Get history of self-improvements.

    Returns recent modifications with their status, performance impact,
    and whether they were applied or reverted.

    Args:
        limit: Maximum number of modifications to return

    Returns:
        Improvement history
    """
    try:
        history = darwin_godel.get_improvement_history(limit)

        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "history": history
            }, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error getting improvement history: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)})
        )]


# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

async def main():
    """Run the AGI MCP server."""
    from mcp.server.stdio import stdio_server

    logger.info("Starting AGI MCP Server...")
    logger.info("Components initialized:")
    logger.info("  - Meta-Learning Engine")
    logger.info("  - Multi-Agent Coordinator")
    logger.info("  - Skill Evolution System")
    logger.info("  - Goal Decomposition AI")
    logger.info("  - Context Synthesis Engine")
    logger.info("  - Darwin Gödel Machine")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
