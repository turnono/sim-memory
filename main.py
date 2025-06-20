import asyncio
import os
from google.adk.runners import Runner
from google.genai.types import Content, Part

# Import your actual components
from sim_guide.sub_agents.memory_manager.agent import memory_manager
from sim_guide.sub_agents.memory_manager.services.rag_memory_service import get_memory_service
from sim_guide.sub_agents.memory_manager.services.session_service import _get_vertex_session_service

# --- Constants ---
REASONING_ENGINE_ID = os.getenv('REASONING_ENGINE_ID')  
# For VertexAI session service, app_name must be the reasoning engine ID
APP_NAME = REASONING_ENGINE_ID if REASONING_ENGINE_ID else os.getenv("APP_NAME", "sim_guide")

# Global runner instance
_runner = None

async def create_runner():
    """Create and return a properly configured runner with memory service"""
    global _runner
    
    if _runner is None:
        print("Initializing ADK Runner with memory service...")
        
        # Get services
        session_service = _get_vertex_session_service()
        memory_service = get_memory_service()
        
        # Create runner with memory management agent
        _runner = Runner(
            agent=memory_manager,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service
        )
        
        print("Runner initialized with:")
        print(f"  - Agent: {memory_manager.name}")
        print(f"  - Session Service: {type(session_service).__name__}")
        print(f"  - Memory Service: {type(memory_service).__name__}")
        print(f"  - App Name: {APP_NAME}")
    
    return _runner

async def save_session_to_memory_if_needed(runner, user_id: str, session_id: str, user_message: str, agent_response: str):
    """Save session to memory if this looks like meaningful conversation"""
    try:
        # Check if this was a meaningful exchange worth preserving
        if (len(user_message) > 10 and len(agent_response) > 20 and 
            not user_message.lower() in ['hello', 'hi', 'hey', 'test']):
            
            # Get the current session
            session = await runner.session_service.get_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
            
            # Add session to memory service for future retrieval
            await runner.memory_service.add_session_to_memory(session)
            print(f"   💾 Session saved to long-term memory")
            
    except Exception as e:
        print(f"   ⚠️  Warning: Could not save session to memory: {e}")
        # Don't fail the chat if memory saving fails

async def chat_with_agent(user_id: str, session_id: str, message: str, runner):
    """Send a message to the agent and get response"""
    user_input = Content(parts=[Part(text=message)], role="user")
    
    print(f"\n🗣️  User ({user_id}): {message}")
    print("🤖 Agent processing...")
    
    final_response = None
    event_count = 0
    
    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_input):
            event_count += 1
            
            # Log different event types
            if event.get_function_calls():
                for func_call in event.get_function_calls():
                    print(f"   🔧 Tool Call: {func_call.name}")
            
            if event.get_function_responses():
                print("   ✅ Tool Response received")
            
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
                break
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        final_response = "Sorry, I encountered an error processing your message."
    
    print(f"🤖 Agent: {final_response}")
    print(f"   (Processed {event_count} events)")
    
    # Save session to memory for future reference
    await save_session_to_memory_if_needed(runner, user_id, session_id, message, final_response)
    
    return final_response or "No response generated"

async def main():
    """Interactive chat with the memory agent"""
    print("🧠 Memory Management Agent - Interactive Chat")
    print("=" * 60)
    
    # Initialize runner
    runner = await create_runner()
    
    # Interactive chat mode
    user_id = input("Enter your user ID (or press Enter for 'user'): ").strip() or "user"
    
    # Create session (VertexAI generates its own session ID)
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id=user_id)
    session_id = session.id
    print(f"📝 Created session: {session_id}")
    print("\n🗣️  Interactive Chat Mode - Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        try:
            user_message = input(f"\n{user_id}: ").strip()
            if user_message.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_message:
                continue
            
            await chat_with_agent(
                user_id=user_id,
                session_id=session_id,
                message=user_message,
                runner=runner
            )
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    asyncio.run(main()) 