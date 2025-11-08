"""
Helper utility functions
"""
import re
from typing import List, Dict, Any
from datetime import datetime


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = text.rfind('.', start, end)
            if last_period != -1:
                end = last_period + 1
        
        chunks.append(text[start:end].strip())
        start = end - overlap
    
    return chunks


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime as ISO string"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def parse_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and validate query parameters"""
    cleaned = {}
    
    for key, value in params.items():
        if value is not None and value != '':
            # Convert string booleans
            if isinstance(value, str):
                if value.lower() == 'true':
                    cleaned[key] = True
                elif value.lower() == 'false':
                    cleaned[key] = False
                else:
                    cleaned[key] = value
            else:
                cleaned[key] = value
    
    return cleaned


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple word-based similarity between two texts
    
    Returns:
        Similarity score between 0 and 1
    """
    words1 = set(clean_text(text1.lower()).split())
    words2 = set(clean_text(text2.lower()).split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract top keywords from text (simple frequency-based)
    
    Args:
        text: Input text
        top_n: Number of keywords to extract
    
    Returns:
        List of keywords
    """
    # Simple word frequency
    words = clean_text(text.lower()).split()
    
    # Common stop words to filter
    stop_words = {
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
        'in', 'with', 'to', 'for', 'of', 'as', 'by', 'from', 'this', 'that'
    }
    
    # Count word frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]

