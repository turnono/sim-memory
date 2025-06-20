# Sim-Memory: A Meta-Cognitive Life Guidance Agent

## Project Overview

`sim-memory` is a sophisticated, meta-cognitive AI assistant designed to provide personalized life guidance. Its core mission is to not only help users with their daily challenges and long-term goals but also to continuously evolve and improve its own capabilities to better serve the user over time. The "simulation" it guides the user through is life itself.

This project is built using the `google.adk` (Agent Development Kit) and leverages Google Cloud's Vertex AI for advanced memory capabilities.

## Core Concepts

- **Meta-Cognition & Self-Improvement**: The agent can analyze its own performance and limitations. It proactively suggests creating new tools, new specialized sub-agents, or even "clones" of the user with expert knowledge in specific domains to enhance its guidance.
- **Hierarchical Agent Architecture**: The system is not a single AI. It's a team of specialized agents coordinated by a central `root_agent`. This allows for deep expertise in various domains like business strategy, memory management, and web search.
- **Flawless Memory**: A core design principle is that the agent has a complete and reliable memory of past interactions. It is explicitly programmed **never** to make excuses about forgetting information. It uses a powerful **R**etrieval **A**ugmented **G**eneration (RAG) service powered by Vertex AI to search and retrieve context from past conversations.
- **Personalized Partnership**: The agent positions the user as a co-creator. It works with the user to build their ideal, personalized AI system, making every interaction an opportunity for both guidance and system evolution.

## Architecture

The system is composed of a `root_agent` that orchestrates several specialized sub-agents and tools.

### `root_agent` (`sim_guide`)

- **Location**: `sim_guide/agent.py`
- **Function**: The central coordinator and the main point of interaction with the user. It analyzes the user's request and decides whether to handle it directly, use a utility tool, or delegate to a specialized sub-agent. Its behavior is governed by the detailed prompt in `sim_guide/prompts.py`.

### Sub-Agents

#### 1. `memory_manager`

- **Location**: `sim_guide/sub_agents/memory_manager/`
- **Function**: The cornerstone of the agent's memory. It handles storing and retrieving user information, conversation history, and session context. It uses ADK's `load_memory` tool which is connected to a Vertex AI RAG service, allowing it to perform semantic searches over past conversations.

#### 2. `business_strategist`

- **Location**: `sim_guide/sub_agents/business_strategist/`
- **Function**: An MBA-level business expert. When the user has business-related questions, the `root_agent` delegates to this sub-agent. It has its own team of even more specialized agents for:
  - Marketing
  - Finance
  - Operations
  - Product
  - Growth Strategy

#### 3. `capability_enhancement_agent`

- **Location**: `sim_guide/sub_agents/capability_enhancement/`
- **Function**: The "meta-cognitive" brain of the system. This agent's job is to analyze the `root_agent`'s performance and identify opportunities for improvement. It can suggest creating new agents, integrating new tools (e.g., connecting to Google Calendar), or designing "user clones" (agents that think like the user but have expert knowledge).

#### 4. `web_search_agent`

- **Location**: `sim_guide/sub_agents/web_search/`
- **Function**: Provides access to real-time information from the internet using Google's built-in search tool. This ensures the agent's knowledge is current and not limited to its training data.

### Callbacks and Services

- **Callbacks** (`sim_guide/callbacks/`): The system uses callbacks to log and monitor events throughout the agent's lifecycle (e.g., before/after a model call, before/after a tool is used). This is useful for debugging and performance tracking.
- **Services** (`sim_guide/sub_agents/memory_manager/services/`): These modules handle the configuration and initialization of core services, primarily the connection to the Vertex AI RAG memory and the ADK session management service.

## Current Status

- **Architecture & Code**: The project's architecture is well-defined and the code appears to be complete and robustly implemented according to the design. The logic is highly modular, separating concerns into different agents and services.
- **Configuration**: The system is configurable via a `.env` file, allowing developers to switch between a full-featured production agent and a lightweight evaluation agent, and to configure the memory backend (Vertex AI RAG or a local in-memory version for testing).
- **Potential Issues**:
  - The project has a high degree of complexity due to its multi-agent nature. Understanding the interaction flow between agents is key.
  - It has a strong dependency on the `google.adk` framework and Google Cloud Platform services. It is not a standalone application.
- **Overall**: The project is at a stage where the core implementation is finished. The next logical steps would be thorough end-to-end testing, deployment to a suitable environment (like Google Cloud Run), and gathering real user feedback to start leveraging its self-improvement capabilities.

## How to Run

1.  **Prerequisites**:
    - Python environment.
    - Google Cloud Project with Vertex AI API enabled.
    - Service account credentials with permissions for Vertex AI.
2.  **Setup**:
    - Install dependencies: `pip install -r requirements.txt`.
    - Create a `.env` file in the root directory and populate it with the necessary configuration from `.env.example` (if one exists) or the required variables (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `RAG_CORPUS_RESOURCE_NAME`, etc.).
3.  **Execution**:
    - The entry point for running the agent seems to be through the `Runner` object defined in `sim_guide/sub_agents/memory_manager/services/session_service.py`. The `main.py` file likely contains the logic to start the application.

This documentation should provide a comprehensive overview to understand the project's purpose, architecture, and current state.
