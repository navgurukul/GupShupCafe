"""
AI Topic Generator
Generates discussion topics using Hugging Face's free API
"""

import httpx
import random
import os
from typing import Optional, Dict, Any, List


# Predefined topics as fallback
FALLBACK_TOPICS = [
    {
        "title": "The Future of Education",
        "description": "How will technology reshape learning in the next decade?",
        "category": "Education",
        "questions": [
            "What role should AI play in personalized learning?",
            "How can we maintain human connection in digital education?",
            "What skills will be most important for future students?"
        ]
    },
    {
        "title": "Sustainable Living in Urban Areas",
        "description": "Exploring practical ways to live more sustainably in cities.",
        "category": "Environment",
        "questions": [
            "What small changes can make the biggest environmental impact?",
            "How can cities be redesigned for sustainability?",
            "What role does individual responsibility play in climate change?"
        ]
    },
    {
        "title": "The Impact of Social Media on Society",
        "description": "Examining both positive and negative effects of social media platforms.",
        "category": "Technology",
        "questions": [
            "How has social media changed human relationships?",
            "What are the benefits and drawbacks of constant connectivity?",
            "How can we use social media more mindfully?"
        ]
    },
    {
        "title": "Mental Health and Well-being",
        "description": "Discussing strategies for maintaining good mental health in modern life.",
        "category": "Health",
        "questions": [
            "What practices contribute most to mental well-being?",
            "How can we reduce stigma around mental health discussions?",
            "What role does community play in supporting mental health?"
        ]
    },
    {
        "title": "The Future of Work",
        "description": "How is the nature of work changing with technology and remote work trends?",
        "category": "Career",
        "questions": [
            "What skills will be most valuable in the future job market?",
            "How can we balance work-life integration?",
            "What impact will AI have on different professions?"
        ]
    },
    {
        "title": "Cultural Diversity and Understanding",
        "description": "The importance of cultural exchange and global perspectives.",
        "category": "Culture",
        "questions": [
            "How can we celebrate differences while finding common ground?",
            "What role does travel play in cultural understanding?",
            "How can we combat cultural stereotypes and biases?"
        ]
    },
    {
        "title": "Entrepreneurship and Innovation",
        "description": "What drives innovation and successful business creation?",
        "category": "Business",
        "questions": [
            "What qualities make a successful entrepreneur?",
            "How can failure contribute to eventual success?",
            "What role does risk-taking play in innovation?"
        ]
    },
    {
        "title": "Personal Growth and Self-Development",
        "description": "Strategies for continuous learning and personal improvement.",
        "category": "Personal Development",
        "questions": [
            "What habits contribute most to personal growth?",
            "How can we overcome limiting beliefs?",
            "What role does feedback play in self-improvement?"
        ]
    }
]


async def generate_discussion_topic(category: str = None) -> Dict[str, Any]:
    """
    Generate a discussion topic using AI, MCP tools, or fallback topics
    Args:
        category: Optional topic category to filter by
    Returns: Topic object
    """
    # If category is provided, try to get topic by category first
    if category:
        category_topic = get_topic_by_category(category)
        if category_topic:
            print(f"📝 Selected topic by category '{category}': {category_topic['title']}")
            return category_topic
    
    try:
        # Try to generate topic using Hugging Face API
        ai_topic = await generate_topic_with_ai()
        if ai_topic:
            return ai_topic
    except Exception as e:
        print(f"AI topic generation failed, using fallback: {str(e)}")
    
    # Fallback to predefined topics
    return get_random_fallback_topic()


async def generate_topic_with_ai() -> Optional[Dict[str, Any]]:
    """
    Generate topic using Hugging Face API
    Returns: AI-generated topic or None
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not api_key or api_key == "your_huggingface_api_key_here":
        print("ℹ️ No Hugging Face API key provided, using fallback topics")
        return None

    try:
        # Use Hugging Face's free text generation model
        prompt = """Generate an engaging discussion topic for an educational roundtable. Include:
1. A compelling title (max 50 characters)
2. A brief description (max 200 characters)
3. A category (Education, Technology, Health, Environment, etc.)
4. 3 thought-provoking questions

Topic:"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_length": 300,
                        "temperature": 0.8,
                        "num_return_sequences": 1
                    }
                }
            )

        if response.status_code != 200:
            raise Exception(f"Hugging Face API error: {response.status_code}")

        data = response.json()
        
        if data and len(data) > 0 and "generated_text" in data[0]:
            # Parse the AI-generated content
            return parse_ai_response(data[0]["generated_text"])
        
        return None
    except Exception as e:
        print(f"Error generating topic with AI: {str(e)}")
        return None


def parse_ai_response(ai_text: str) -> Dict[str, Any]:
    """
    Parse AI response and structure it as a topic
    Args:
        ai_text: Raw AI-generated text
    Returns: Structured topic object
    """
    try:
        # This is a simplified parser - in production, you'd want more robust parsing
        lines = [line.strip() for line in ai_text.split('\n') if line.strip()]
        
        # Extract title (first meaningful line)
        title = lines[0].lstrip('0123456789. ') if lines else "AI-Generated Discussion Topic"
        
        # Create a structured topic
        return {
            "title": title[:50] if len(title) > 50 else title,
            "description": f"An AI-generated topic focusing on {title.lower()}.",
            "category": "AI Generated",
            "questions": [
                "What are your initial thoughts on this topic?",
                "How does this relate to your personal experience?",
                "What aspects would you like to explore further?"
            ],
            "source": "AI Generated"
        }
    except Exception as e:
        print(f"Error parsing AI response: {str(e)}")
        return get_random_fallback_topic()


def get_random_fallback_topic() -> Dict[str, Any]:
    """
    Get a random fallback topic
    Returns: Random topic from predefined list
    """
    topic = random.choice(FALLBACK_TOPICS).copy()
    print(f"📝 Selected fallback topic: {topic['title']}")
    return topic


def get_all_fallback_topics() -> List[Dict[str, Any]]:
    """
    Get all available fallback topics (for API endpoint)
    Returns: Array of all fallback topics
    """
    return [topic.copy() for topic in FALLBACK_TOPICS]


def get_topic_by_category(category: str) -> Optional[Dict[str, Any]]:
    """
    Get topic by category
    Args:
        category: Topic category
    Returns: Topic matching category or None
    """
    for topic in FALLBACK_TOPICS:
        if topic["category"].lower() == category.lower():
            return topic.copy()
    
    return None
