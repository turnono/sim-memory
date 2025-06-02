"""
Tool execution callbacks for the Sim Guide Agent

Monitors tool executions and integrates with RAG Memory Service
and User Preference System for enhanced user experience.
"""

import time
import logging
from typing import Dict, Any, Optional, Union
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import BaseTool

logger = logging.getLogger(__name__)


def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, **kwargs
) -> Optional[Dict]:
    """
    Called before a tool is executed.
    
    Args:
        tool: The tool about to be executed
        args: Arguments passed to the tool
        tool_context: The tool execution context from ADK
        **kwargs: Additional arguments from the framework
        
    Returns:
        Optional[Dict]: Return None to proceed, or dict to override tool execution
    """
    try:
        # Get tool information
        tool_name = getattr(tool, 'name', getattr(tool, '__name__', str(tool)))
        function_call_id = getattr(tool_context, 'function_call_id', 'unknown_call')
        
        # Store start time for performance tracking
        if not hasattr(tool_context, 'state'):
            tool_context.state = {}
        
        tool_context.state[f'{tool_name}_start_time'] = time.time()
        tool_context.state['current_tool_name'] = tool_name
        tool_context.state['current_function_call_id'] = function_call_id
        
        # Log tool execution start
        logger.info(f"🔧 Starting tool execution: {tool_name} (call_id: {function_call_id})")
        logger.debug(f"Tool arguments: {args}")
        
        # Auto-analyze user messages for preferences if available
        _analyze_message_for_preferences(args or {}, tool_context)
        
        # Track tool usage patterns
        _track_tool_usage(tool_name, tool_context)
        
        # Return None to proceed with normal tool execution
        return None
        
    except Exception as e:
        logger.error(f"Error in before_tool_callback: {e}")
        # Don't raise - callbacks should be non-blocking
        return None


def after_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, response: Any = None, **kwargs
) -> Optional[Dict]:
    """
    Called after a tool is executed.
    
    Args:
        tool: The executed tool
        args: Arguments that were passed to the tool
        tool_context: The tool execution context from ADK
        response: The tool's response (may also be passed in kwargs)
        **kwargs: Additional arguments from the framework
        
    Returns:
        Optional[Dict]: Return None to use original response, or dict to override response
    """
    try:
        # Handle cases where response or tool_context might be in kwargs (fallback)
        if response is None and 'response' in kwargs:
            response = kwargs['response']
        if response is None and 'tool_response' in kwargs:
            response = kwargs['tool_response']
        
        # Validate tool_context is a proper object, not a string
        if tool_context is not None and (isinstance(tool_context, str) or not hasattr(tool_context, '__dict__')):
            logger.debug(f"Invalid tool_context type: {type(tool_context)}, creating minimal context")
            tool_context = None
        
        # Get tool information
        tool_name = getattr(tool, 'name', getattr(tool, '__name__', str(tool)))
        function_call_id = getattr(tool_context, 'function_call_id', 'unknown_call') if tool_context else 'unknown_call'
        
        # Ensure context has state (only if we have a valid tool_context)
        if tool_context and not hasattr(tool_context, 'state'):
            try:
                tool_context.state = {}
            except (AttributeError, TypeError):
                logger.debug(f"Cannot set state on tool_context of type {type(tool_context)}")
                tool_context = None
        
        # Calculate execution time
        start_time = None
        execution_time = 0.0
        
        if tool_context and hasattr(tool_context, 'state') and isinstance(tool_context.state, dict):
            start_time = tool_context.state.get(f'{tool_name}_start_time', time.time())
            execution_time = time.time() - start_time
        elif tool_context and hasattr(tool_context, 'state') and isinstance(tool_context.state, str):
            # If state is a string, we can't get the start time, so estimate a small execution time
            execution_time = 0.01
        else:
            # Fallback: estimate a small execution time
            execution_time = 0.01
        
        # Determine success based on response
        success = response is not None and not (
            isinstance(response, str) and response.startswith("Error:")
        )
        
        # Log tool completion
        logger.info(f"🔧 Completed tool execution: {tool_name} ({'✅' if success else '❌'}) in {execution_time:.2f}s")
        
        # Store performance metrics (only if we have a valid tool_context with state)
        if tool_context and hasattr(tool_context, 'state') and isinstance(tool_context.state, dict):
            try:
                if 'tool_metrics' not in tool_context.state:
                    tool_context.state['tool_metrics'] = []
                    
                tool_context.state['tool_metrics'].append({
                    'tool_name': tool_name,
                    'function_call_id': function_call_id,
                    'execution_time': execution_time,
                    'success': success,
                    'timestamp': time.time(),
                    'args_count': len(args) if args else 0,
                    'response_type': type(response).__name__ if response else 'None'
                })
                
                # Store the duration for this specific tool
                tool_context.state[f'{tool_name}_last_duration'] = execution_time
            except (AttributeError, TypeError) as e:
                logger.debug(f"Could not store tool metrics: {e}")
        
        # Handle memory-related tool responses
        if _is_memory_related_tool(tool_name):
            _handle_memory_tool_response(tool_name, args or {}, response, tool_context)
        
        # Handle preference-related tool responses
        if _is_preference_related_tool(tool_name):
            _handle_preference_tool_response(tool_name, args or {}, response, tool_context)
        
        # Update user preferences based on tool usage patterns
        _update_preferences_from_tool_usage(tool_name, args or {}, response, tool_context)
        
        logger.debug(f"Tool response type: {type(response).__name__ if response else 'None'}")
        
        # Return None to use the original response
        return None
        
    except Exception as e:
        logger.error(f"Error in after_tool_callback: {e}")
        # Don't raise - callbacks should be non-blocking
        return None


def _analyze_message_for_preferences(args: Dict[str, Any], context: ToolContext) -> None:
    """
    Analyze tool arguments for user messages that might contain preference indicators.
    
    Args:
        args: Tool arguments
        context: Tool execution context
    """
    try:
        # Look for user message in common argument names
        user_message = None
        
        for key in ['message', 'user_message', 'text', 'query', 'prompt', 'input']:
            if key in args and isinstance(args[key], str):
                user_message = args[key]
                break
        
        if user_message and len(user_message) > 10:  # Only analyze substantial messages
            from ..services import analyze_user_message_for_preferences
            
            session_state = getattr(context, 'state', {})
            updated_prefs = analyze_user_message_for_preferences(user_message, session_state)
            
            logger.debug(f"Analyzed message for preferences: {len(user_message)} chars")
            
    except Exception as e:
        logger.debug(f"Could not analyze message for preferences: {e}")


def _track_tool_usage(tool_name: str, context: ToolContext) -> None:
    """
    Track tool usage patterns for preference insights.
    
    Args:
        tool_name: Name of the tool being used
        context: Tool execution context (may be None or invalid)
    """
    try:
        # Skip if context is invalid
        if not context or isinstance(context, str) or not hasattr(context, '__dict__'):
            logger.debug(f"Skipping tool usage tracking - invalid context")
            return
            
        if not hasattr(context, 'state'):
            try:
                context.state = {}
            except (AttributeError, TypeError):
                logger.debug(f"Cannot create state on context of type {type(context)}")
                return
        
        if not isinstance(context.state, dict):
            logger.debug(f"Context state is not a dict: {type(context.state)}")
            return
            
        if 'tool_usage_history' not in context.state:
            context.state['tool_usage_history'] = []
            
        context.state['tool_usage_history'].append({
            'tool_name': tool_name,
            'timestamp': time.time(),
            'session_id': getattr(context, 'session_id', 'unknown'),
            'agent_name': getattr(context, 'agent_name', 'unknown'),
            'invocation_id': getattr(context, 'invocation_id', 'unknown')
        })
        
        # Keep only recent history (last 50 tool uses)
        if len(context.state['tool_usage_history']) > 50:
            context.state['tool_usage_history'] = context.state['tool_usage_history'][-50:]
            
    except Exception as e:
        logger.debug(f"Could not track tool usage: {e}")


def _is_memory_related_tool(tool_name: str) -> bool:
    """Check if a tool is memory-related"""
    memory_tools = [
        'search_memories', 'add_memory', 'retrieve_memories',
        'store_conversation', 'recall_context', 'save_session',
        'load_life_guidance_memory', 'preload_life_context', 'load_life_resources'
    ]
    return any(memory_tool in tool_name.lower() for memory_tool in memory_tools)


def _is_preference_related_tool(tool_name: str) -> bool:
    """Check if a tool is preference-related"""
    preference_tools = [
        'get_user_preferences', 'set_user_preference', 'remove_user_preference',
        'analyze_message_for_preferences', 'get_personalization_context'
    ]
    return tool_name in preference_tools


def _handle_memory_tool_response(
    tool_name: str, args: Dict[str, Any], response: Any, context: ToolContext
) -> None:
    """
    Handle responses from memory-related tools by integrating with RAG Memory Service.
    
    Args:
        tool_name: Name of the memory tool
        args: Tool arguments
        response: Tool response
        context: Tool execution context (may be None or invalid)
    """
    try:
        # Skip if context is invalid
        if not context or isinstance(context, str) or not hasattr(context, '__dict__'):
            logger.debug(f"Skipping memory tool response handling - invalid context")
            return
            
        # Import RAG memory service for integration
        import asyncio
        from ..services import rag_memory_service
        
        user_id = getattr(context, 'user_id', 'unknown')
        session_id = getattr(context, 'session_id', 'unknown')
        
        # Store important interactions in RAG memory
        if response and hasattr(response, 'success') and response.success:
            memory_content = f"Tool: {tool_name}, Args: {args}, Response: {getattr(response, 'result', 'N/A')}"
            
            # Create async task to store memory (don't await to avoid blocking)
            def store_memory():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        rag_memory_service.add_memory_from_conversation(
                            user_id=user_id,
                            conversation_data=memory_content,
                            metadata={"tool_name": tool_name, "session_id": session_id}
                        )
                    )
                    loop.close()
                except Exception as e:
                    logger.debug(f"Could not store tool memory: {e}")
            
            import threading
            threading.Thread(target=store_memory, daemon=True).start()
        
        logger.debug(f"Handled memory tool response for: {tool_name}")
        
    except Exception as e:
        logger.debug(f"Could not integrate with RAG Memory Service: {e}")


def _handle_preference_tool_response(
    tool_name: str, args: Dict[str, Any], response: Any, context: ToolContext
) -> None:
    """
    Handle responses from preference-related tools.
    
    Args:
        tool_name: Name of the preference tool
        args: Tool arguments
        response: Tool response
        context: Tool execution context (may be None or invalid)
    """
    try:
        # Skip if context is invalid
        if not context or isinstance(context, str) or not hasattr(context, '__dict__'):
            logger.debug(f"Skipping preference tool response handling - invalid context")
            return
            
        # Detect preference changes from tool usage
        if tool_name == 'get_user_preferences':
            logger.debug("User checked their preferences")
            
        elif tool_name == 'set_user_preference' and args:
            preference_name = args.get('preference_name')
            preference_value = args.get('preference_value')
            logger.debug(f"User updated preference: {preference_name} = {preference_value}")
            
        elif tool_name == 'analyze_message_for_preferences' and args:
            message = args.get('message', '')
            if len(message) > 10:  # Only track substantial messages
                logger.debug(f"Analyzed message for preferences: {len(message)} chars")
        
    except Exception as e:
        logger.debug(f"Could not handle preference tool response: {e}")


def _update_preferences_from_tool_usage(
    tool_name: str, args: Dict[str, Any], response: Any, context: ToolContext
) -> None:
    """
    Update user preferences based on tool usage patterns.
    
    Args:
        tool_name: Name of the tool used
        args: Tool arguments
        response: Tool response
        context: Tool execution context (may be None or invalid)
    """
    try:
        # Skip if context is invalid
        if not context or isinstance(context, str) or not hasattr(context, '__dict__'):
            logger.debug(f"Skipping preference updates - invalid context")
            return
            
        # Try to get session state for preference updates
        session_state = getattr(context, 'state', {}) if hasattr(context, 'state') else {}
        if not isinstance(session_state, dict):
            logger.debug(f"Session state is not a dict: {type(session_state)}")
            return
        
        # Get current user preferences
        from ..services import get_user_preferences
        preferences = get_user_preferences(session_state)
        
        # Detect life areas from tool usage
        life_area_keywords = {
            'career': ['career', 'job', 'work', 'professional'],
            'finance': ['finance', 'money', 'budget', 'investment'],
            'health': ['health', 'fitness', 'wellness', 'exercise'],
            'relationships': ['relationship', 'family', 'friends', 'social'],
            'personal_growth': ['growth', 'learning', 'development', 'skills']
        }
        
        for area_type, keywords in life_area_keywords.items():
            if any(keyword in tool_name.lower() for keyword in keywords):
                from ..services import LifeArea
                try:
                    area_enum = LifeArea(area_type)
                    if area_enum not in preferences.focus_life_areas:
                        preferences.focus_life_areas.append(area_enum)
                        logger.debug(f"Added life area interest: {area_type}")
                        
                        # Update preferences in session
                        from ..services import update_user_preferences
                        update_user_preferences(preferences, session_state)
                        
                except (ValueError, AttributeError) as e:
                    logger.debug(f"Could not add life area {area_type}: {e}")
                break
        
    except Exception as e:
        logger.debug(f"Could not update preferences from tool usage: {e}")
