"""
Tests for AI topic generator
"""

import pytest
from src.ai.topic_generator import (
    get_random_fallback_topic,
    get_all_fallback_topics,
    get_topic_by_category,
    parse_ai_response
)


def test_get_random_fallback_topic():
    """Test getting a random fallback topic"""
    topic = get_random_fallback_topic()
    
    assert topic is not None
    assert "title" in topic
    assert "description" in topic
    assert "category" in topic
    assert "questions" in topic
    assert len(topic["questions"]) == 3


def test_get_all_fallback_topics():
    """Test getting all fallback topics"""
    topics = get_all_fallback_topics()
    
    assert len(topics) > 0
    assert all("title" in t for t in topics)
    assert all("description" in t for t in topics)
    assert all("category" in t for t in topics)


def test_get_topic_by_category():
    """Test getting topic by category"""
    # Test existing category
    topic = get_topic_by_category("Education")
    assert topic is not None
    assert topic["category"] == "Education"
    
    # Test non-existing category
    topic = get_topic_by_category("NonExistent")
    assert topic is None


def test_get_topic_by_category_case_insensitive():
    """Test category lookup is case insensitive"""
    topic1 = get_topic_by_category("education")
    topic2 = get_topic_by_category("EDUCATION")
    
    assert topic1 is not None
    assert topic2 is not None
    assert topic1["title"] == topic2["title"]


def test_parse_ai_response():
    """Test parsing AI response"""
    ai_text = "The Future of Quantum Computing\nThis is a test description."
    topic = parse_ai_response(ai_text)
    
    assert topic is not None
    assert "title" in topic
    assert "description" in topic
    assert "category" in topic
    assert "questions" in topic


def test_parse_ai_response_long_title():
    """Test parsing AI response with long title"""
    long_title = "A" * 100
    ai_text = f"{long_title}\nDescription here."
    topic = parse_ai_response(ai_text)
    
    # Title should be truncated to 50 characters
    assert len(topic["title"]) <= 50


@pytest.mark.asyncio
async def test_generate_discussion_topic():
    """Test generating discussion topic (will fallback without API key)"""
    from src.ai.topic_generator import generate_discussion_topic
    
    topic = await generate_discussion_topic()
    
    assert topic is not None
    assert "title" in topic
    assert "description" in topic
    assert "category" in topic
