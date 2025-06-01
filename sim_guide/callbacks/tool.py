"""
Tool callbacks for the Sim Guide Agent.

These callbacks handle tool execution events for monitoring,
logging, and state management around tool usage.
"""

import logging
from typing import Optional, Any, Dict
from datetime import datetime

try:
    from google.adk.tools.base_tool import BaseTool
    from google.adk.tools.tool_context import ToolContext
except ImportError:
    # Fallback for development/testing
    BaseTool = Any
    ToolContext = Any

# Configure logging for callbacks
logger = logging.getLogger(__name__)


def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Callback executed before each tool invocation.
    
    This is called before any tool is executed by the agent.
    Use this for logging, argument validation, and preparation.
    
    Args:
        tool: The tool being invoked
        args: Arguments being passed to the tool
        tool_context: Context information for the tool execution
        
    Returns:
        Optional dict with modifications to the tool arguments
    """
    try:
        # Extract tool information
        tool_name = getattr(tool, 'name', str(tool))
        logger.info(f"Tool execution started: {tool_name}")
        
        # Log tool arguments (be careful with sensitive data)
        sanitized_args = {k: v for k, v in args.items() if not k.lower().startswith('secret')}
        logger.info(f"Tool arguments: {sanitized_args}")
        
        # Extract session context if available
        session_id = getattr(tool_context, 'session_id', 'unknown')
        user_id = getattr(tool_context, 'user_id', 'unknown')
        
        logger.info(f"Tool '{tool_name}' called by user: {user_id}, session: {session_id}")
        
        # Track timing for performance metrics
        if hasattr(tool_context, 'state'):
            tool_context.state[f'{tool_name}_start_time'] = datetime.now().isoformat()
        
        # Here you could add functionality like:
        # - Argument validation or sanitization
        # - Rate limiting per user
        # - Tool usage analytics
        # - Custom tool routing logic
        
        # Return None to proceed with original arguments
        # Return a dict to modify the arguments passed to the tool
        return None
        
    except Exception as e:
        logger.error(f"Error in before_tool_callback: {e}")
        return None


def after_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Any
) -> Optional[Dict]:
    """
    Callback executed after each tool invocation.
    
    This is called after a tool has been executed by the agent.
    Use this for logging, response processing, and state updates.
    
    Args:
        tool: The tool that was invoked
        args: Arguments that were passed to the tool
        tool_context: Context information for the tool execution
        tool_response: The response returned by the tool
        
    Returns:
        Optional dict with state updates or response modifications
    """
    try:
        # Extract tool information
        tool_name = getattr(tool, 'name', str(tool))
        logger.info(f"Tool execution completed: {tool_name}")
        
        # Calculate tool execution time
        if hasattr(tool_context, 'state'):
            start_time_key = f'{tool_name}_start_time'
            if start_time_key in tool_context.state:
                start_time = datetime.fromisoformat(tool_context.state[start_time_key])
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Tool '{tool_name}' execution time: {duration:.2f} seconds")
                
                # Store performance metrics
                tool_context.state[f'{tool_name}_last_duration'] = duration
                
                # Clean up the start time
                del tool_context.state[start_time_key]
        
        # Extract session context
        session_id = getattr(tool_context, 'session_id', 'unknown')
        user_id = getattr(tool_context, 'user_id', 'unknown')
        
        logger.info(f"Tool '{tool_name}' completed for user: {user_id}, session: {session_id}")
        
        # Log response information (be careful with sensitive data)
        if tool_response:
            response_type = type(tool_response).__name__
            logger.info(f"Tool response type: {response_type}")
            
            # Log response size if it's a string or has length
            try:
                if hasattr(tool_response, '__len__'):
                    logger.info(f"Tool response length: {len(tool_response)}")
                elif isinstance(tool_response, str):
                    logger.info(f"Tool response length: {len(tool_response)} characters")
            except:
                pass
        
        # Handle specific tool integrations
        try:
            # Integration with RAG Memory Service for memory-related tools
            if tool_name and 'memory' in tool_name.lower():
                _handle_memory_tool_response(
                    tool_name, args, tool_response, tool_context
                )
            
            # Handle search or knowledge tools
            if tool_name and any(keyword in tool_name.lower() for keyword in ['search', 'query', 'knowledge']):
                _handle_knowledge_tool_response(
                    tool_name, args, tool_response, tool_context
                )
                
        except Exception as integration_error:
            logger.warning(f"Tool integration error for {tool_name}: {integration_error}")
        
        # Here you could add additional functionality like:
        # - Response caching
        # - Tool usage analytics
        # - Custom response formatting
        # - State persistence to external systems
        
        return None
        
    except Exception as e:
        logger.error(f"Error in after_tool_callback: {e}")
        return None


def _handle_memory_tool_response(
    tool_name: str, args: Dict[str, Any], response: Any, context: ToolContext
) -> None:
    """
    Handle responses from memory-related tools by integrating with RAG Memory Service.
    
    Args:
        tool_name: Name of the memory tool
        args: Tool arguments
        response: Tool response
        context: Tool execution context
    """
    try:
        # Import RAG memory service for integration
        import asyncio
        from ..rag_memory_service import (
            add_memory_from_conversation, retrieve_user_memories, health_check
        )
        
        user_id = getattr(context, 'user_id', 'unknown')
        session_id = getattr(context, 'session_id', 'unknown')
        
        # Store important interactions in RAG memory
        if response and isinstance(response, str) and len(response) > 50:
            memory_content = f"Tool: {tool_name}\nArgs: {args}\nResponse: {response[:500]}..."
            
            # Run async function in a new event loop if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, schedule the task
                    asyncio.create_task(add_memory_from_conversation(user_id, session_id, memory_content))
                else:
                    # If no event loop is running, run it
                    asyncio.run(add_memory_from_conversation(user_id, session_id, memory_content))
            except Exception as async_error:
                logger.warning(f"Could not store memory asynchronously: {async_error}")
            
            logger.info(f"Stored tool interaction in RAG memory for user {user_id}")
            
    except Exception as e:
        logger.warning(f"Failed to integrate with RAG memory service: {e}")


def _handle_knowledge_tool_response(
    tool_name: str, args: Dict[str, Any], response: Any, context: ToolContext
) -> None:
    """
    Handle responses from knowledge/search tools.
    
    Args:
        tool_name: Name of the knowledge tool
        args: Tool arguments  
        response: Tool response
        context: Tool execution context
    """
    try:
        # Here you could add functionality like:
        # - Caching search results
        # - Learning from user queries
        # - Improving search relevance
        # - Building user knowledge profiles
        
        logger.info(f"Knowledge tool '{tool_name}' provided response for query")
        
    except Exception as e:
        logger.warning(f"Failed to handle knowledge tool response: {e}")
