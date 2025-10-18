"""
Grammar Tools MCP Server

Provides grammar checking and language analysis tools for English learning.
Compatible with Strands SDK MCPClient via streamable HTTP transport.
"""

from mcp.server import FastMCP
from typing import Dict, List, Optional, Any
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Create MCP server for grammar tools
mcp = FastMCP("Grammar Tools Server")


@mcp.tool(description="Detect basic grammar issues in English text")
def check_grammar(text: str) -> Dict[str, Any]:
    """
    Perform basic grammar checking on English text.
    
    Args:
        text: English text to analyze
        
    Returns:
        Dictionary with grammar issues and suggestions
    """
    issues = []
    
    # Simple grammar checks (can be enhanced with language-tool-python or LanguageTool API)
    # Check for double spaces
    if "  " in text:
        issues.append({
            "type": "spacing",
            "message": "Multiple consecutive spaces found",
            "severity": "minor"
        })
    
    # Check for missing capital at sentence start
    sentences = text.split(". ")
    for sentence in sentences:
        if sentence and not sentence[0].isupper():
            issues.append({
                "type": "capitalization",
                "message": "Sentence should start with capital letter",
                "severity": "medium"
            })
            break
    
    # Check for missing punctuation at the end
    if text and text[-1] not in '.!?':
        issues.append({
            "type": "punctuation",
            "message": "Missing ending punctuation",
            "severity": "medium"
        })
    
    return {
        "text": text,
        "issue_count": len(issues),
        "issues": issues,
        "status": "checked"
    }


@mcp.tool(description="Analyze vocabulary complexity and provide CEFR-aligned suggestions")
def analyze_vocabulary(text: str) -> Dict[str, Any]:
    """
    Analyze vocabulary usage and complexity.
    
    Args:
        text: English text to analyze
        
    Returns:
        Dictionary with vocabulary analysis
    """
    words = text.lower().split()
    word_count = len(words)
    unique_words = len(set(words))
    
    # Simple complexity indicators
    long_words = [w for w in words if len(w) > 7]
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    
    complexity_level = "basic"
    if avg_word_length > 5 and len(long_words) > word_count * 0.2:
        complexity_level = "advanced"
    elif avg_word_length > 4:
        complexity_level = "intermediate"
    
    return {
        "word_count": word_count,
        "unique_words": unique_words,
        "lexical_diversity": round(unique_words / word_count, 2) if word_count > 0 else 0,
        "avg_word_length": round(avg_word_length, 2),
        "long_words_count": len(long_words),
        "complexity_level": complexity_level
    }


@mcp.tool(description="Count filler words and suggest improvements")
def detect_fillers(text: str) -> Dict[str, Any]:
    """
    Detect and count filler words in speech/text.
    
    Args:
        text: English text to analyze
        
    Returns:
        Dictionary with filler word analysis
    """
    filler_words = ["um", "uh", "like", "you know", "actually", "basically", "literally", "so", "well"]
    
    text_lower = text.lower()
    detected_fillers = {}
    total_filler_count = 0
    
    for filler in filler_words:
        count = text_lower.count(filler)
        if count > 0:
            detected_fillers[filler] = count
            total_filler_count += count
    
    word_count = len(text.split())
    filler_ratio = round(total_filler_count / word_count, 3) if word_count > 0 else 0
    
    return {
        "total_filler_count": total_filler_count,
        "detected_fillers": detected_fillers,
        "word_count": word_count,
        "filler_ratio": filler_ratio,
        "suggestion": "Good work!" if filler_ratio < 0.05 else "Try to reduce filler words for clearer communication"
    }


@mcp.tool(description="Analyze sentence structure and complexity")
def analyze_sentence_structure(text: str) -> Dict[str, Any]:
    """
    Analyze sentence structure and complexity.
    
    Args:
        text: English text to analyze
        
    Returns:
        Dictionary with sentence analysis
    """
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    sentence_count = len(sentences)
    
    if sentence_count == 0:
        return {
            "sentence_count": 0,
            "avg_sentence_length": 0,
            "message": "No complete sentences found"
        }
    
    sentence_lengths = [len(s.split()) for s in sentences]
    avg_length = sum(sentence_lengths) / sentence_count
    
    # Categorize complexity
    if avg_length < 10:
        complexity = "simple"
    elif avg_length < 20:
        complexity = "moderate"
    else:
        complexity = "complex"
    
    return {
        "sentence_count": sentence_count,
        "avg_sentence_length": round(avg_length, 2),
        "longest_sentence": max(sentence_lengths),
        "shortest_sentence": min(sentence_lengths),
        "complexity": complexity
    }


def start_grammar_tools_server(port: int = 8001, host: str = "localhost"):
    """
    Start the grammar tools MCP server.
    
    Args:
        port: Port to run the server on (default: 8001)
        host: Host to bind to (default: localhost)
    """
    logger.info(f"🚀 Starting Grammar Tools MCP Server on http://{host}:{port}")
    logger.info(f"📋 Available tools: check_grammar, analyze_vocabulary, detect_fillers, analyze_sentence_structure")
    logger.info(f"🔗 MCP endpoint: http://{host}:{port}/mcp/")
    
    try:
        # Some MCP server versions don't accept host/port in run(); prefer uvicorn via http_app()
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("\n✅ Grammar Tools MCP Server stopped gracefully")
    except Exception as e:
        logger.error(f"❌ Error running server: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Grammar Tools MCP Server")
    parser.add_argument("--port", type=int, default=8001, help="Port to run server on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    
    args = parser.parse_args()
    start_grammar_tools_server(port=args.port, host=args.host)

# Expose ASGI app for uvicorn-based HTTP serving (recommended)
try:
    app = mcp.http_app()
except Exception:
    app = None
