from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import get_filtered_properties
from app.db import get_db
from mcp_client import extract_final_answer, run_agent

router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="Role of the message sender ('user' or 'assistant')"
    )
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message")
    chat_history: List[ChatMessage] = Field(
        default_factory=list, description="List of previous chat messages for context"
    )
    model: str = Field(
        default="gpt-4o", description="The OpenAI model to use for the chat completion"
    )


@router.get("/properties")
async def search_properties(
    city: str = None,
    bhk: int = None,
    max_price: int = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Search for properties based on filters.

    Args:
        city: Filter by city name
        bhk: Filter by number of bedrooms
        max_price: Maximum price filter
        db: Database session

    Returns:
        List of properties matching the criteria
    """
    try:
        properties = await get_filtered_properties(
            db, city=city, bhk=bhk, max_price=max_price
        )
        return {"status": "success", "results": len(properties), "data": properties}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching properties: {str(e)}",
        )


@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_agent(request: ChatRequest):
    """
    Chat with the MCP-powered LLM agent.

    This endpoint connects to the MCP server and uses the available tools
    to respond to user queries about properties.

    Example request body:
    ```json
    {
        "message": "Find me 2 BHK apartments in Mumbai under 2 crores",
        "chat_history": [
            {"role": "user", "content": "Hi, I'm looking for a property"},
            {"role": "assistant", "content": "I can help with that! What are you looking for?"}
        ]
    }
    ```

    Returns:
        JSON response with the agent's reply and updated chat history
    """
    try:
        # Format the chat history for the agent
        formatted_messages = [(msg.role, msg.content) for msg in request.chat_history]

        # Add the current user message
        user_message = ("user", request.message)
        formatted_messages.append(user_message)

        # Run the agent with the full message history
        agent_response = await run_agent(
            {"messages": formatted_messages, "model": request.model}
        )

        print(agent_response, "AGENT RESPONSE")

        # Extract the final answer
        final_answer = extract_final_answer(agent_response.get("messages", []))

        # Update chat history with the assistant's response
        updated_history = request.chat_history.copy()
        updated_history.append(ChatMessage(role="assistant", content=final_answer))

        return {
            "status": "success",
            "message": final_answer,
            "chat_history": updated_history,
            "raw_response": agent_response,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat processing: {str(e)}",
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "version": "1.0.0", "service": "real-estate-chat-api"}
