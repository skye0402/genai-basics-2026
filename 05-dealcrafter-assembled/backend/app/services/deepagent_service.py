"""DeepAgent service with MCP tools integration for agentic workflows."""
import asyncio
import logging
from typing import Any, AsyncGenerator, Optional
from collections.abc import Iterable
from textwrap import dedent

from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.core.config import settings
from app.services.session_storage import SessionStorage

# Configure logger
logger = logging.getLogger(__name__)

# Singleton instances
_agent_instance: Optional[Any] = None
_mcp_client_instance: Optional[MultiServerMCPClient] = None
_model_instance: Optional[Any] = None

# MCP server configuration
MCP_SERVER_CONFIG = {
    "backend": {
        "transport": "streamable_http",
        "url": "http://localhost:3001/mcp",
    }
}

# Thread configuration for conversation persistence
THREAD_CONFIG = {"configurable": {"thread_id": "backend-session"}}


def _get_model() -> Any:
    """
    Get or initialize the LLM model instance (singleton pattern).
    
    Returns:
        Initialized LLM model
    """
    global _model_instance
    
    if _model_instance is None:
        logger.info("Initializing LLM model for DeepAgent")

        base_url = (settings.litellm_proxy_url or "").rstrip("/")
        if base_url and not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        _model_instance = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.litellm_api_key or None,
            base_url=base_url or None,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
        logger.info("LLM model initialized successfully")
    
    return _model_instance


async def _load_mcp_tools() -> tuple[list[Any], Optional[MultiServerMCPClient]]:
    """
    Connect to the local MCP server and retrieve available tools.
    
    Returns:
        Tuple of (tools list, mcp_client instance or None)
    """
    try:
        mcp_client = MultiServerMCPClient(MCP_SERVER_CONFIG)
        tools = await mcp_client.get_tools()
        logger.info(f"Loaded {len(tools)} MCP tool(s)")
        return list(tools), mcp_client
    except Exception as exc:
        logger.warning(f"Unable to load MCP tools: {exc}", exc_info=True)
        return [], None


async def _get_agent() -> tuple[Any, Optional[MultiServerMCPClient]]:
    """
    Get or initialize the DeepAgent instance (singleton pattern).
    
    Returns:
        Tuple of (agent instance, mcp_client instance or None)
    """
    global _agent_instance, _mcp_client_instance
    
    if _agent_instance is None:
        logger.info("Initializing DeepAgent with MCP tools")
        
        # Load model and MCP tools
        model = _get_model()
        mcp_tools, mcp_client = await _load_mcp_tools()
        
        # Store MCP client for cleanup
        _mcp_client_instance = mcp_client
        
        # Create agent with tools
        system_prompt = dedent(
            """You are DealCrafter, an AI-powered financial research assistant.
            
            ## Your Role
            You help users with investment research, market analysis, and document retrieval.
            You can also generate formal Deal Memos when requested.
            
            ## Capabilities (Tools)
            - **get_stock_info**: Fetch real-time stock prices and metrics from Yahoo Finance
            - **web_search**: Quick web search for recent news
            - **web_research**: Deep research for comprehensive analysis
            - **search_document_content**: Search ingested PDF documents (RAG)
            - **get_document_images**: Get images from documents to include in responses
            - **get_time_and_place**: Get current time and location context
            
            ## Including Images in Responses
            When search results contain `image_ids` in metadata, relevant charts/tables/diagrams are available.
            To include an image:
            1. Use `get_document_images` with the document_id to see available images
            2. Include relevant images using markdown: ![description](image:imageId)
            
            **When to include images:**
            - Charts showing financial data, trends, or comparisons
            - Tables with key metrics or figures
            - Diagrams explaining business models or strategies
            - Any visual that helps answer the user's question
            
            ## Language Guidelines
            - **Match the user's language**: If the user writes in English, respond in English.
              If the user writes in Japanese, respond in Japanese.
            - Only use Japanese for Deal Memos if explicitly requested.
            
            ## Guidelines
            1. Greet the user appropriately for the time of day based on their timezone
               (the user's timezone is provided in the message as "[User timezone: ...]")
            2. Always use tools to gather data before answering financial questions
            3. Cite specific numbers and sources
            4. Be objective, concise, and risk-aware
            5. Make good use of tools - better more tool calls than less
            6. Include relevant images when they help illustrate your response
            7. When citing document content, add footnote markers (e.g., [^1]) inline and
               include a footnote list at the end with document title/filename and page number
               for each citation (e.g., "[^1]: Mitsubishi Fuso Super Great Brochure — p. 22").
            
            ## Deal Memo Format (when requested)
            If the user asks for a formal Japanese Deal Memo (案件概要書), use this structure:
            
            # 案件概要書 (Deal Memo): {会社名}
            
            ## 1. エグゼクティブサマリー
            ## 2. 企業概要
            ## 3. 市場分析・外部環境
            ## 4. 財務・リスク評価
            ## 5. 戦略的意義
            ## 6. 推奨アクション
            
            ---
            Begin by greeting the user. Ask how you can help with their research today.
            """
        )

        _agent_instance = create_deep_agent(
            model=model,
            tools=mcp_tools,
            system_prompt=system_prompt,
        )
        
        logger.info("DeepAgent initialized successfully")
    
    return _agent_instance, _mcp_client_instance


def _text_from_chunk(chunk: object) -> Iterable[str]:
    """
    Yield text fragments from a LangGraph stream chunk.
    
    Args:
        chunk: Stream chunk from agent.astream()
        
    Yields:
        Text strings extracted from the chunk
    """
    if chunk is None:
        return []

    # LangGraph message chunks expose `.content`
    content = getattr(chunk, "content", None)
    if content is not None:
        yield from _normalize_content(content)
        return

    # Dictionaries may contain "messages" with structured content
    if isinstance(chunk, dict):
        if "messages" in chunk and chunk["messages"]:
            last = chunk["messages"][-1]
            if hasattr(last, "content"):
                yield from _normalize_content(getattr(last, "content"))
            elif isinstance(last, dict):
                yield from _normalize_content(last.get("content"))
        elif "delta" in chunk:
            delta = chunk["delta"]
            if hasattr(delta, "content"):
                yield from _normalize_content(getattr(delta, "content"))
            else:
                yield from _normalize_content(delta)
        return

    # Tuples can wrap (channels, payload) or (channel, payload)
    if isinstance(chunk, tuple):
        if len(chunk) == 3:
            _, channel, payload = chunk
        elif len(chunk) == 2:
            channel, payload = chunk
        else:
            return

        if channel == "messages":
            yield from _text_from_chunk(payload)
        else:
            yield from _text_from_chunk(payload)


def _normalize_content(content: object) -> Iterable[str]:
    """
    Normalize various content formats into plain text strings.
    
    Args:
        content: Content object to normalize
        
    Returns:
        List of text strings
    """
    if content is None:
        return []

    if isinstance(content, str):
        return [content]

    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text" and part.get("text"):
                    texts.append(part["text"])
            elif isinstance(part, str):
                texts.append(part)
        return texts

    return [str(content)]


async def generate_deepagent_response(
    message: str,
    session_id: str | None = None,
    timezone: str | None = None
) -> AsyncGenerator[dict, None]:
    """
    Generate streaming response using DeepAgent with MCP tools.
    
    Loads previous messages from the session and includes them as context
    for the agent to maintain conversation continuity.
    
    Args:
        message: User message
        session_id: Session ID to load chat history from
        timezone: IANA timezone from browser (e.g. "America/New_York")
        
    Yields:
        SSE events as dictionaries with 'event' and 'data' keys
    """
    # If timezone provided, prepend it to the message as context for the agent
    if timezone:
        message = f"[User timezone: {timezone}]\n\n{message}"
    try:
        # Get or initialize agent
        agent, _ = await _get_agent()
        
        # Load chat history from session
        conversation = []
        if session_id:
            logger.debug(f"Loading chat history for session: {session_id}")
            storage = SessionStorage()
            session = storage.get_session(session_id)
            if session and session.messages:
                logger.info(f"Loaded {len(session.messages)} messages from session {session_id}")
                for msg in session.messages:
                    # Check if message has image attachments (multimodal)
                    if msg.role == "user" and msg.attachments:
                        # Build multimodal content array (OpenAI format)
                        content = []
                        
                        # Add text if present
                        if msg.content:
                            content.append({
                                "type": "text",
                                "text": msg.content
                            })
                        
                        # Add images
                        for attachment in msg.attachments:
                            content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{attachment.mime_type};base64,{attachment.data}"
                                }
                            })
                        
                        conversation.append({
                            "role": msg.role,
                            "content": content
                        })
                        logger.debug(f"Added multimodal message with {len(msg.attachments)} attachment(s)")
                    else:
                        # Text-only message
                        conversation.append({
                            "role": msg.role,
                            "content": msg.content
                        })
            else:
                logger.warning(f"No session or messages found for session_id: {session_id}")
        else:
            logger.debug("No session_id provided, starting fresh conversation")
        
        # Add current message
        conversation.append({"role": "user", "content": message})
        
        # Prepare payload for agent
        payload = {"messages": [dict(msg) for msg in conversation]}
        
        # Stream response chunks
        has_output = False
        async for chunk in agent.astream(
            payload,
            config=THREAD_CONFIG,
            stream_mode="messages",
        ):
            for text in _text_from_chunk(chunk):
                if text:
                    has_output = True
                    yield {
                        "event": "text",
                        "data": text
                    }
                    # Small delay to make streaming visible
                    await asyncio.sleep(0.01)
        
        # If no streaming output, try invoke as fallback
        if not has_output:
            logger.warning("No streaming output, using invoke fallback")
            try:
                fallback = await agent.ainvoke(payload, config=THREAD_CONFIG)
                fallback_chunks = list(_text_from_chunk(fallback))
                if fallback_chunks:
                    fallback_text = "".join(fallback_chunks)
                    yield {
                        "event": "text",
                        "data": fallback_text
                    }
            except Exception as fallback_exc:
                logger.error(f"Invoke fallback error: {fallback_exc}", exc_info=True)
                yield {
                    "event": "error",
                    "data": f"Agent error: {str(fallback_exc)}"
                }
        
        # Signal end of stream
        yield {"event": "end", "data": ""}
        
    except Exception as e:
        # Log and send error event
        logger.error(f"DeepAgent error occurred: {str(e)}", exc_info=True)
        error_msg = f"DeepAgent Error: {str(e)}"
        yield {"event": "error", "data": error_msg}
        yield {"event": "end", "data": ""}


async def cleanup_deepagent_service() -> None:
    """
    Cleanup DeepAgent service resources.
    
    Should be called on application shutdown.
    """
    global _mcp_client_instance
    
    if _mcp_client_instance is not None:
        logger.info("Cleaning up MCP client connection")
        close = getattr(_mcp_client_instance, "aclose", None)
        if callable(close):
            try:
                await close()
                logger.info("MCP client closed successfully")
            except Exception as exc:
                logger.warning(f"Error closing MCP client: {exc}")
        _mcp_client_instance = None
