"""
Pytest configuration and fixtures for AGI MCP Server tests.
"""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, Mock, AsyncMock
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock the AGI component modules before they're imported
mock_modules = [
    'meta_learning_engine',
    'multi_agent_coordinator',
    'skill_evolution_system',
    'goal_decomposition_ai',
    'context_synthesis_engine',
    'darwin_godel_machine'
]

for module_name in mock_modules:
    sys.modules[module_name] = MagicMock()


# Mock classes for AGI components
class MockTaskOutcome:
    """Mock TaskOutcome class."""
    def __init__(self, task_id, task_type, agent_used, success, execution_time_ms,
                 error_message=None, quality_score=None, timestamp=None, context=None):
        self.task_id = task_id
        self.task_type = task_type
        self.agent_used = agent_used
        self.success = success
        self.execution_time_ms = execution_time_ms
        self.error_message = error_message
        self.quality_score = quality_score
        self.timestamp = timestamp or datetime.now()
        self.context = context or {}


class MockModificationType:
    """Mock ModificationType enum."""
    ALGORITHM_IMPROVE = "algorithm_improve"
    DATA_STRUCTURE = "data_structure"
    INTERFACE = "interface"
    OPTIMIZATION = "optimization"

    def __getitem__(self, key):
        return getattr(self, key)


# Add mock classes to modules
sys.modules['meta_learning_engine'].TaskOutcome = MockTaskOutcome
sys.modules['darwin_godel_machine'].ModificationType = MockModificationType()


@pytest.fixture
def mock_meta_learning():
    """Mock MetaLearningEngine."""
    mock = Mock()
    mock.record_outcome = Mock(return_value=None)
    mock.recommend_agent = Mock(return_value=("test_agent", 0.85))
    mock.detect_patterns = Mock(return_value=[
        {"pattern": "high_success_rate", "agent": "test_agent", "confidence": 0.9}
    ])
    mock.get_learning_summary = Mock(return_value={
        "total_outcomes": 100,
        "success_rate": 0.85,
        "top_agents": ["test_agent"]
    })
    return mock


@pytest.fixture
def mock_coordinator():
    """Mock MultiAgentCoordinator."""
    mock = Mock()
    mock.execute_task = AsyncMock(return_value={
        "task_id": "test_task",
        "status": "completed",
        "subtasks": []
    })
    mock.get_system_status = Mock(return_value={
        "agents": ["agent1", "agent2"],
        "active_sessions": 2,
        "health": "healthy"
    })
    return mock


@pytest.fixture
def mock_skill_evolution():
    """Mock SkillEvolutionSystem."""
    mock = Mock()
    skill_mock = Mock()
    skill_mock.skill_name = "test_skill"
    skill_mock.version = "v1"
    skill_mock.created_at = datetime.now()

    mock.register_skill = Mock(return_value=skill_mock)
    mock.start_ab_test = Mock(return_value="test_id_123")
    mock.promote_version = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_goal_ai():
    """Mock GoalDecompositionAI."""
    mock = Mock()
    mock.execute_goal = AsyncMock(return_value={
        "goal_id": "goal_123",
        "tasks": [{"task_id": "t1", "description": "Task 1"}],
        "status": "in_progress"
    })
    mock.get_goal_progress = Mock(return_value={
        "goal_id": "goal_123",
        "completed": 2,
        "total": 5,
        "progress": 0.4
    })
    return mock


@pytest.fixture
def mock_context_engine():
    """Mock ContextSynthesisEngine."""
    mock = Mock()
    context_result = Mock()
    context_result.chunks = [
        Mock(source_type="file", relevance_score=0.9),
        Mock(source_type="memory", relevance_score=0.8)
    ]
    context_result.total_tokens = 5000
    context_result.compression_ratio = 0.5

    mock.synthesize = AsyncMock(return_value=context_result)
    return mock


@pytest.fixture
def mock_darwin_godel():
    """Mock DarwinGodelMachine."""
    mock = Mock()
    modification_mock = Mock()
    modification_mock.modification_id = "mod_123"
    modification_mock.modification_type = Mock(value="algorithm_improve")
    modification_mock.description = "Test modification"
    modification_mock.proof_status = Mock(value="verified")

    mock.set_baseline = Mock(return_value=None)
    mock.propose_modification = Mock(return_value=modification_mock)
    mock.get_improvement_history = Mock(return_value=[{
        "modification_id": "mod_123",
        "status": "applied",
        "performance_impact": 1.2
    }])
    return mock


@pytest.fixture
def mock_app(monkeypatch, mock_meta_learning, mock_coordinator, mock_skill_evolution,
             mock_goal_ai, mock_context_engine, mock_darwin_godel):
    """Mock the server app with all components."""
    import server

    # Replace global instances
    monkeypatch.setattr(server, 'meta_learning', mock_meta_learning)
    monkeypatch.setattr(server, 'coordinator', mock_coordinator)
    monkeypatch.setattr(server, 'skill_evolution', mock_skill_evolution)
    monkeypatch.setattr(server, 'goal_ai', mock_goal_ai)
    monkeypatch.setattr(server, 'context_engine', mock_context_engine)
    monkeypatch.setattr(server, 'darwin_godel', mock_darwin_godel)

    return server.app
