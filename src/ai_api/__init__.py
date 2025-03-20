"""
AI API Helper Module

This module provides a simplified interface for interacting with AI APIs.
"""

from .gemini import query_gemini
from .vision import query_vision

__all__ = ['query_gemini', 'query_vision'] 