from typing import Dict, Any, List, Union, Tuple
import asyncio
import os

from langchain_core.messages import ToolMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender ('user', 'assistant', or 'system')")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    messages: List[Union[Tuple[str, str], Dict[str, str]]] = Field(
        ...,
        description="List of message tuples (role, content) or dicts with role/content keys"
    )
    model: str = Field(
        default="gpt-4o",
        description="The OpenAI model to use for the chat completion"
    )
    temperature: float = Field(
        default=0.7,
        description="Controls randomness in the response generation"
    )

# Initialize the chat model with configuration
model_config = {
    "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
    "api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": 0.1,
}

model = ChatOpenAI(**model_config)

# MCP server configuration
server_params = StdioServerParameters(
    command="python3",
    args=["-m", "app.mcp_tools.server"],
)

async def run_agent(chat_request: Union[Dict[str, Any], ChatRequest]) -> Dict[str, Any]:
    """
    Run the MCP agent with the given chat request.
    
    Args:
        chat_request: Either a ChatRequest object or a dictionary containing:
            - messages: List of message tuples (role, content) or dicts with role/content
            
    Returns:
        dict: The agent's response containing messages and metadata
    """
    # Convert dict to ChatRequest if needed
    if isinstance(chat_request, dict):
        chat_request = ChatRequest(**chat_request)
    elif not isinstance(chat_request, ChatRequest):
        raise ValueError("chat_request must be a dict or ChatRequest object")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Get tools from MCP server
                tools = await load_mcp_tools(session)
                
                # Format messages for the agent
                formatted_messages = []
                for msg in chat_request.messages:
                    if isinstance(msg, (list, tuple)) and len(msg) == 2:
                        role, content = msg
                    elif isinstance(msg, dict):
                        role = msg.get('role')
                        content = msg.get('content')
                    else:
                        continue

                    # Print role and content
                    print(role, content, "MCP agent message")
                    
                    if role == 'system':
                        formatted_messages.append(SystemMessage(content=content))
                    elif role == 'user':
                        formatted_messages.append(HumanMessage(content=content))
                    elif role == 'ai':
                        formatted_messages.append(AIMessage(content=content))
                    elif role == 'tool':
                        formatted_messages.append(ToolMessage(content=content))
                
                # Create and run the agent
                agent = create_react_agent(model, tools)
                agent_response = await agent.ainvoke({
                    "messages": formatted_messages
                })

                print(agent_response.get("messages", []), "MCP agent response")
                # Format the response
                return {
                    "status": "success",
                    "messages": agent_response.get("messages", []),
                    "metadata": {
                        "model": model.model_name,
                        "tokens_used": len(str(agent_response).split())
                    }
                }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }

# def extract_final_answer(agent_response: Dict[str, Any]) -> str:
#     """
#     Extract the final answer from the agent's response.
#
#     Args:
#         agent_response: The response dictionary from run_agent
#
#     Returns:
#         str: The final answer text or error message
#     """
#     if not isinstance(agent_response, dict):
#         return "Invalid response format from agent"
#
#     if agent_response.get("status") == "error":
#         return f"Error: {agent_response.get('message', 'Unknown error')}"
#
#     messages = agent_response.get("messages", [])
#     if not messages:
#         return "No response generated"
#
#     # Return the last assistant message
#     for msg in reversed(messages):
#         print(msg, "type", type(msg))
#         if isinstance(msg, dict) and msg.get("role") == "assistant":
#             return msg.get("content", "No content")
#         elif hasattr(msg, "type") and msg.type == "ai":
#             return getattr(msg, "content", "No content")
#
#     return "No assistant message found in response"

def extract_final_answer(agent_response):
    if isinstance(agent_response, list):
        for message in reversed(agent_response):
            if isinstance(message, AIMessage) and message.content:
                return message.content
    return "No valid answer found."
async def chat_loop():
    """Run an interactive chat loop with the agent."""
    print("Real Estate Chat Agent (type 'exit' to quit)")
    print("-" * 40)
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")
            
            # Exit condition
            if user_input.lower() in ['exit', 'quit']:
                print("\nGoodbye!")
                break
            
            # Prepare the chat request
            chat_request = {
                "messages": user_input,
                "model": model.model_name,
                "temperature": model.temperature
            }
            
            # Get agent response
            print("\nAgent is thinking...")
            response = await run_agent(chat_request)
            
            # Extract and display the answer
            answer = extract_final_answer(response)
            print(f"\nAgent: {answer}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n{error_msg}")

if __name__ == "__main__":
    try:
        # Run the interactive chat loop
        asyncio.run(chat_loop())
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
