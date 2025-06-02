"""
Evaluation Suite for VertexAI Session Service
=============================================

This package contains comprehensive evaluations for testing:
- Session service functionality
- Agent behavior and response quality
- Performance and scalability
- Error handling and edge cases

Usage:
    # Run all evaluations
    python -m evals.run_all_evals

    # Run specific evaluation suites
    python -m evals.session_evals
    python -m evals.agent_evals
    python -m evals.performance_evals
"""

__version__ = "1.0.0"
__author__ = "VertexAI Session Service Team"

# Import main evaluation runners for convenience
from .session_evals import run_session_evals
from .agent_evals import run_agent_evals
from .performance_evals import run_performance_evals
from .run_all_evals import main as run_all_evals

__all__ = [
    "run_session_evals",
    "run_agent_evals",
    "run_performance_evals",
    "run_all_evals",
]
