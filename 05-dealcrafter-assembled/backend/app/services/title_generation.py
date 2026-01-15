"""Title generation service using LLM for chat session summarization."""
import logging
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.models.schemas import ChatSession

# Configure logger
logger = logging.getLogger(__name__)

# Singleton summarization LLM instance
_summarization_llm_instance: Optional[BaseChatModel] = None


def _get_summarization_llm() -> BaseChatModel:
    """
    Get or initialize the summarization LLM instance (singleton pattern).
    Uses a faster/cheaper model for title generation.
    
    Returns:
        Initialized summarization LLM instance
    """
    global _summarization_llm_instance
    
    if _summarization_llm_instance is None:
        logger.info("Initializing summarization LLM instance (first time)")

        base_url = (settings.litellm_proxy_url or "").rstrip("/")
        if base_url and not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        _summarization_llm_instance = ChatOpenAI(
            model=settings.summarization_llm_model,
            api_key=settings.litellm_api_key or None,
            base_url=base_url or None,
            temperature=settings.summarization_temperature,
            max_tokens=settings.summarization_max_tokens,
        )
        
        logger.info(f"Summarization LLM initialized with model: {settings.summarization_llm_model}")
    else:
        logger.debug("Reusing existing summarization LLM instance")
    
    return _summarization_llm_instance


async def generate_session_title(session: ChatSession, max_messages: int = 5) -> str:
    """
    Generate a concise title for a chat session using LLM.
    
    Uses the first few messages to create a meaningful, searchable title.
    
    Args:
        session: Chat session to generate title for
        max_messages: Maximum number of messages to include in context (default: 5)
        
    Returns:
        Generated title string (max 60 characters)
    """
    try:
        logger.info(f"Generating title for session {session.session_id}")
        
        # Get first few messages for context
        messages_for_context = session.messages[:max_messages]
        
        if not messages_for_context:
            logger.warning(f"No messages in session {session.session_id}, using default title")
            return "New Chat"
        
        # Build conversation context
        conversation = []
        for msg in messages_for_context:
            role = "User" if msg.role == "user" else "Assistant"
            # Truncate long messages
            content = msg.content[:200] if len(msg.content) > 200 else msg.content
            conversation.append(f"{role}: {content}")
        
        conversation_text = "\n".join(conversation)
        
        # Create prompt for title generation
        prompt = ChatPromptTemplate.from_template(
            """Based on the following conversation, generate a short, concise title (max 60 characters).
The title should capture the main topic or question.
Use only plain text, no quotes, no special formatting.

Conversation:
{conversation}

Title:"""
        )
        
        # Get summarization LLM
        llm = _get_summarization_llm()
        
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Generate title
        title = await chain.ainvoke({"conversation": conversation_text})
        
        # Clean and truncate title
        title = title.strip().strip('"').strip("'")
        if len(title) > 60:
            title = title[:57] + "..."
        
        logger.info(f"Generated title for session {session.session_id}: {title}")
        return title
        
    except Exception as e:
        logger.error(f"Error generating title for session {session.session_id}: {str(e)}", exc_info=True)
        # Fallback to first user message
        first_user_msg = next(
            (msg for msg in session.messages if msg.role == "user"),
            None
        )
        if first_user_msg:
            words = first_user_msg.content.split()[:8]
            fallback_title = " ".join(words)
            if len(first_user_msg.content.split()) > 8:
                fallback_title += "..."
            return fallback_title
        return "New Chat"
