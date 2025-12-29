"""
Tests for Context Synthesis Engine tools.

Covers:
- agi_synthesize_context
"""

import pytest
import json


@pytest.mark.asyncio
async def test_agi_synthesize_context_success(mock_app, mock_context_engine):
    """Test successful context synthesis."""
    import server

    result = await server.agi_synthesize_context(
        query="multi-agent coordination implementation",
        source_types=["file", "memory", "code"],
        target_tokens=10000
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert "context" in data
    assert data["context"]["chunks"] == 2
    assert data["context"]["total_tokens"] == 5000
    assert data["context"]["compression_ratio"] == 0.5
    assert len(data["context"]["sources"]) == 2

    mock_context_engine.synthesize.assert_called_once_with(
        "multi-agent coordination implementation",
        ["file", "memory", "code"],
        10000
    )


@pytest.mark.asyncio
async def test_agi_synthesize_context_minimal(mock_app, mock_context_engine):
    """Test context synthesis with minimal parameters."""
    import server

    result = await server.agi_synthesize_context(
        query="authentication system"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    # Should be called with None for optional parameters
    call_args = mock_context_engine.synthesize.call_args[0]
    assert call_args[0] == "authentication system"
    assert call_args[1] is None  # source_types
    assert call_args[2] is None  # target_tokens


@pytest.mark.asyncio
async def test_agi_synthesize_context_validation():
    """Test parameter validation for synthesize_context."""
    import server

    # Test with missing required parameter
    with pytest.raises(TypeError):
        await server.agi_synthesize_context()  # Missing query


@pytest.mark.asyncio
async def test_agi_synthesize_context_all_sources(mock_app, mock_context_engine):
    """Test context synthesis with all source types."""
    import server

    all_sources = ["file", "memory", "code", "api", "sensor"]

    result = await server.agi_synthesize_context(
        query="system health check",
        source_types=all_sources
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    call_args = mock_context_engine.synthesize.call_args[0]
    assert call_args[1] == all_sources


@pytest.mark.asyncio
async def test_agi_synthesize_context_with_target_tokens(mock_app, mock_context_engine):
    """Test context synthesis with specific token target."""
    import server

    result = await server.agi_synthesize_context(
        query="optimization strategies",
        target_tokens=5000
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    call_args = mock_context_engine.synthesize.call_args[0]
    assert call_args[2] == 5000


@pytest.mark.asyncio
async def test_agi_synthesize_context_high_compression(mock_app, mock_context_engine):
    """Test context synthesis with high compression ratio."""
    import server

    # Update mock to return high compression
    context_result = mock_context_engine.synthesize.return_value
    context_result.compression_ratio = 0.1  # 90% compression

    result = await server.agi_synthesize_context(
        query="large codebase analysis",
        target_tokens=2000
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["context"]["compression_ratio"] == 0.1


@pytest.mark.asyncio
async def test_agi_synthesize_context_many_chunks(mock_app, mock_context_engine):
    """Test context synthesis with many source chunks."""
    import server

    # Update mock to return many chunks
    from unittest.mock import Mock
    chunks = [
        Mock(source_type=f"source_{i}", relevance_score=0.9 - (i * 0.05))
        for i in range(10)
    ]
    mock_context_engine.synthesize.return_value.chunks = chunks

    result = await server.agi_synthesize_context(
        query="comprehensive analysis"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"
    assert data["context"]["chunks"] == 10
    # Should only return first 5 sources in the response
    assert len(data["context"]["sources"]) == 5


@pytest.mark.asyncio
async def test_agi_synthesize_context_empty_query(mock_app, mock_context_engine):
    """Test context synthesis with empty query."""
    import server

    result = await server.agi_synthesize_context(
        query=""
    )

    # Should still call the underlying function
    data = json.loads(result[0].text)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_agi_synthesize_context_relevance_ordering(mock_app, mock_context_engine):
    """Test that context sources are ordered by relevance."""
    import server

    from unittest.mock import Mock

    # Create chunks with different relevance scores
    chunks = [
        Mock(source_type="file", relevance_score=0.9),
        Mock(source_type="memory", relevance_score=0.8),
        Mock(source_type="code", relevance_score=0.95),
        Mock(source_type="api", relevance_score=0.7),
        Mock(source_type="sensor", relevance_score=0.85)
    ]
    mock_context_engine.synthesize.return_value.chunks = chunks

    result = await server.agi_synthesize_context(
        query="test query"
    )

    data = json.loads(result[0].text)
    sources = data["context"]["sources"]

    # Should return first 5 sources (all in this case)
    assert len(sources) == 5
    # First source should have highest relevance
    assert sources[0]["type"] == "file"
    assert sources[0]["relevance"] == 0.9


@pytest.mark.asyncio
async def test_synthesize_context_error_handling(mock_app, mock_context_engine):
    """Test error handling in context synthesis."""
    import server

    # Make the mock raise an exception
    mock_context_engine.synthesize.side_effect = Exception("Synthesis failed")

    result = await server.agi_synthesize_context(
        query="failing query"
    )

    data = json.loads(result[0].text)
    assert data["status"] == "error"
    assert "Synthesis failed" in data["message"]


@pytest.mark.asyncio
async def test_agi_synthesize_context_zero_tokens(mock_app, mock_context_engine):
    """Test context synthesis with zero token budget."""
    import server

    result = await server.agi_synthesize_context(
        query="test",
        target_tokens=0
    )

    data = json.loads(result[0].text)
    assert data["status"] == "success"

    call_args = mock_context_engine.synthesize.call_args[0]
    assert call_args[2] == 0
