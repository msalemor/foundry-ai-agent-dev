# Azure AI Foundry - AI Agent Development

Development with Azure AI Foundry AI Agents.

## Overview of Azure AI Foundry AI Agents

Azure AI Foundry AI Agents is a comprehensive platform for building, deploying, and managing intelligent AI agents. It provides developers with the tools and infrastructure needed to create sophisticated conversational AI solutions that can integrate with various data sources and services.

### Key Features

- **Agent Creation**: Build custom AI agents with specific instructions, capabilities, and personas
- **Thread Management**: Handle multi-turn conversations with persistent context and memory
- **Integration**: Seamlessly integrate with Azure services and external APIs
- **Scalability**: Deploy agents that can handle multiple concurrent conversations
- **Security**: Built-in authentication and authorization with Azure Identity
- **Monitoring**: Track agent performance and conversation analytics

### Core Components

- **Projects**: Organizational units that group related agents and resources
- **Agents**: The AI entities that interact with users, configured with specific instructions and capabilities
- **Threads**: Conversation sessions that maintain context across multiple message exchanges
- **Messages**: Individual communication units within a thread (user inputs and agent responses)

References:
- [Concepts - Threads, Runs and Messages](https://learn.microsoft.com/en-ca/azure/ai-foundry/agents/concepts/threads-runs-messages)

### Use Cases

- Customer service chatbots
- Technical support assistants
- Knowledge base query systems
- Workflow automation agents
- Educational tutoring systems
- Interactive documentation helpers

### Getting Started

This repository demonstrates how to:
1. Create and configure AI agents
2. Manage conversation threads
3. Store agent configurations and state
4. Integrate with Azure AI Projects
5. Handle authentication and security

## Demos

1. [No AI Agent](./demos/1-noaiagent-rag-chatbot.py)
2. [AI Agent - Portal Code](./demos/2-use-agent-portal-code.py)
3. [Simple AI Agent](./demos/3-create-simple-agent.py)
4. [Full AI Agent](./demos/4-create-full-agent.py)
5. [AI Agent Class](./demos/5-full-agent-class.py)
6. [AI Agent from REST FastAPI](./demos/6-fastapi-agent.py)