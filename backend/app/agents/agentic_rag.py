"""
Agentic RAG Agent implementation.

AgenticRAG is an agent architecture that enhances responses with knowledge
retrieval from vector databases. It decides when to retrieve information
and combines retrieved context with LLM reasoning.

Key features:
- Autonomous retrieval decisions
- Multi-knowledge base support
- Source citation
- Iterative retrieval when needed
"""

import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import uuid4

from app.agents.base import AgentConfig, AgentContext, BaseAgent, Tool
from app.agents.events import AgentEvent, EventType, StateSnapshotEvent
from app.integrations.llm.base import BaseLLMClient, LLMMessage, MessageRole


class DocumentChunk(Protocol):
    """Protocol for document chunks returned from retrieval."""

    @property
    def content(self) -> str:
        """The text content of the chunk."""
        ...

    @property
    def metadata(self) -> dict[str, Any]:
        """Metadata including source, document name, etc."""
        ...

    @property
    def score(self) -> float:
        """Relevance score (0-1)."""
        ...


@dataclass
class RetrievalResult:
    """Result of a retrieval operation."""

    query: str
    knowledge_base_id: str
    chunks: list[dict[str, Any]] = field(default_factory=list)
    total_found: int = 0


@dataclass
class RAGConfig(AgentConfig):
    """Configuration specific to RAG Agent."""

    # Retrieval settings
    top_k: int = 5
    similarity_threshold: float = 0.7
    max_retrieval_attempts: int = 3

    # Context settings
    max_context_length: int = 4000
    include_sources: bool = True

    # Behavior settings
    always_retrieve: bool = False  # If True, always retrieve before answering


# Type alias for retrieval function
RetrievalFunc = Any  # Callable[[str, list[str], int], Awaitable[list[RetrievalResult]]]


AGENTIC_RAG_SYSTEM_PROMPT = """You are a helpful AI assistant with access to a knowledge base.

Your task is to answer questions accurately using the provided context when relevant.

## Available Knowledge Bases
{knowledge_bases}

## Instructions

1. **Analyze the Question**: Determine if you need to retrieve information from the knowledge base.
   - Factual questions, specific details, or domain-specific queries → RETRIEVE
   - General conversation, greetings, or common knowledge → ANSWER DIRECTLY

2. **When Retrieving**:
   - Formulate a clear search query
   - Review the retrieved context carefully
   - If the context doesn't fully answer the question, you may retrieve again with a refined query

3. **When Answering**:
   - Base your answer on the retrieved context when available
   - Cite sources when using information from the knowledge base
   - Be honest if the knowledge base doesn't contain relevant information
   - Combine retrieved information with your general knowledge when appropriate

4. **Response Format**:
   When you need to retrieve, respond with:
   ```json
   {{
       "action": "retrieve",
       "query": "your search query",
       "knowledge_base_ids": ["kb_id1", "kb_id2"]
   }}
   ```

   When you're ready to answer, respond with:
   ```json
   {{
       "action": "answer",
       "answer": "Your complete answer here",
       "sources": ["source1", "source2"]
   }}
   ```

## Retrieved Context
{context}

## Conversation History
{history}
"""


class AgenticRAGAgent(BaseAgent):
    """
    Agentic RAG Agent implementation.

    This agent intelligently decides when to retrieve from knowledge bases
    and how to incorporate retrieved information into responses.
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,
        tools: list[Tool] | None = None,
        config: RAGConfig | None = None,
        knowledge_base_ids: list[str] | None = None,
        retrieval_func: RetrievalFunc | None = None,
        system_prompt: str | None = None,
    ):
        """
        Initialize the AgenticRAG agent.

        Args:
            llm_client: LLM client for model calls
            tools: Optional list of tools available to the agent
            config: Optional RAG-specific configuration
            knowledge_base_ids: List of knowledge base IDs to query
            retrieval_func: Async function to perform retrieval
            system_prompt: Optional custom system prompt
        """
        super().__init__(llm_client, tools, config or RAGConfig())
        self.knowledge_base_ids = knowledge_base_ids or []
        self.retrieval_func = retrieval_func
        self._custom_system_prompt = system_prompt
        self._rag_config = config or RAGConfig()

    @property
    def agent_type(self) -> str:
        return "agentic_rag"

    def _build_system_prompt(
        self,
        context: AgentContext,
        retrieved_context: str = "",
    ) -> str:
        """Build the system prompt with knowledge base info and context."""
        if self._custom_system_prompt:
            base_prompt = self._custom_system_prompt
        else:
            base_prompt = AGENTIC_RAG_SYSTEM_PROMPT

        # Build knowledge base description
        if self.knowledge_base_ids:
            kb_desc = "\n".join([f"- {kb_id}" for kb_id in self.knowledge_base_ids])
        else:
            kb_desc = "No knowledge bases configured."

        # Build history summary
        history_lines = []
        for msg in context.message_history[-6:]:  # Last 6 messages
            role = msg.role.value.capitalize()
            content = (
                msg.content[:300] + "..." if len(msg.content) > 300 else msg.content
            )
            history_lines.append(f"{role}: {content}")

        history = "\n".join(history_lines) if history_lines else "No previous messages."

        return base_prompt.format(
            knowledge_bases=kb_desc,
            context=retrieved_context or "No context retrieved yet.",
            history=history,
        )

    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse the LLM response to extract action and parameters."""
        import re

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try to parse the entire content as JSON
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        # Fallback: treat as direct answer
        return {
            "action": "answer",
            "answer": content,
            "sources": [],
        }

    def _format_retrieved_context(
        self,
        results: list[RetrievalResult],
    ) -> str:
        """Format retrieved results into context string."""
        if not results:
            return "No relevant documents found."

        context_parts = []
        for result in results:
            if result.chunks:
                context_parts.append(f"### Results from: {result.knowledge_base_id}")
                context_parts.append(f"Query: {result.query}")
                context_parts.append("")

                for i, chunk in enumerate(result.chunks, 1):
                    source = chunk.get("metadata", {}).get("source", "Unknown")
                    score = chunk.get("score", 0)
                    content = chunk.get("content", "")

                    context_parts.append(
                        f"[{i}] (Score: {score:.2f}, Source: {source})"
                    )
                    context_parts.append(content)
                    context_parts.append("")

        return "\n".join(context_parts)

    async def _retrieve(
        self,
        query: str,
        knowledge_base_ids: list[str] | None = None,
    ) -> list[RetrievalResult]:
        """
        Perform retrieval from knowledge bases.

        Args:
            query: The search query
            knowledge_base_ids: Specific KBs to query (uses all if None)

        Returns:
            List of retrieval results
        """
        if not self.retrieval_func:
            # Return mock result when no retrieval function is configured
            return [
                RetrievalResult(
                    query=query,
                    knowledge_base_id="mock",
                    chunks=[
                        {
                            "content": f"[Mock retrieval] No retrieval function configured. Query: {query}",
                            "metadata": {"source": "mock"},
                            "score": 0.0,
                        }
                    ],
                    total_found=1,
                )
            ]

        kb_ids = knowledge_base_ids or self.knowledge_base_ids
        try:
            results = await self.retrieval_func(
                query,
                kb_ids,
                self._rag_config.top_k,
            )
            return results
        except Exception as e:
            # Return error as a result
            return [
                RetrievalResult(
                    query=query,
                    knowledge_base_id="error",
                    chunks=[
                        {
                            "content": f"Retrieval error: {str(e)}",
                            "metadata": {"source": "error"},
                            "score": 0.0,
                        }
                    ],
                    total_found=0,
                )
            ]

    async def _process(
        self,
        message: str,
        context: AgentContext,
    ) -> AsyncIterator[AgentEvent]:
        """
        Process the message using Agentic RAG pattern.

        Args:
            message: The user message to process
            context: Execution context

        Yields:
            AgentEvent objects representing the agent's activity
        """
        # Add user message to history
        context.message_history.append(
            LLMMessage(role=MessageRole.USER, content=message)
        )

        # Track retrieved context across iterations
        all_retrieved_context = ""
        retrieval_attempt = 0
        max_attempts = self._rag_config.max_retrieval_attempts

        # If always_retrieve is set, do initial retrieval
        if self._rag_config.always_retrieve and self.knowledge_base_ids:
            yield self.emit_step_started("retrieval")

            # Emit retrieval as a tool call
            retrieval_id = str(uuid4())
            yield self.emit_tool_call_start(
                tool_call_id=retrieval_id,
                tool_name="knowledge_retrieval",
            )
            yield self.emit_tool_call_args(
                retrieval_id,
                json.dumps(
                    {"query": message, "knowledge_bases": self.knowledge_base_ids}
                ),
            )
            yield self.emit_tool_call_end(retrieval_id)

            # Perform retrieval
            results = await self._retrieve(message)
            all_retrieved_context = self._format_retrieved_context(results)

            yield self.emit_tool_call_result(
                tool_call_id=retrieval_id,
                content=f"Retrieved {sum(len(r.chunks) for r in results)} documents",
            )
            yield self.emit_step_finished("retrieval")
            retrieval_attempt += 1

        while retrieval_attempt <= max_attempts:
            if context.is_cancelled():
                return

            # Step: Thinking/Reasoning
            yield self.emit_step_started("reasoning")

            # Build system prompt with current context
            system_prompt = self._build_system_prompt(context, all_retrieved_context)

            messages = [
                LLMMessage(role=MessageRole.SYSTEM, content=system_prompt),
                *context.message_history,
            ]

            # Call LLM
            reasoning_message_id = str(uuid4())
            yield self.emit_text_start(reasoning_message_id)

            full_content = ""
            async for chunk in self.llm_client.chat_stream(
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            ):
                if context.is_cancelled():
                    yield self.emit_text_end(reasoning_message_id)
                    return

                if chunk.content:
                    full_content += chunk.content
                    yield self.emit_text_content(reasoning_message_id, chunk.content)

            yield self.emit_text_end(reasoning_message_id)
            yield self.emit_step_finished("reasoning")

            # Parse the response
            parsed = self._parse_response(full_content)
            action = parsed.get("action", "answer")

            # Add to history
            context.message_history.append(
                LLMMessage(role=MessageRole.ASSISTANT, content=full_content)
            )

            if action == "retrieve":
                # Perform retrieval
                retrieval_attempt += 1
                if retrieval_attempt > max_attempts:
                    break

                yield self.emit_step_started("retrieval")

                query = parsed.get("query", message)
                kb_ids = parsed.get("knowledge_base_ids", self.knowledge_base_ids)

                # Emit as tool call for UI
                retrieval_id = str(uuid4())
                yield self.emit_tool_call_start(
                    tool_call_id=retrieval_id,
                    tool_name="knowledge_retrieval",
                    parent_message_id=reasoning_message_id,
                )
                yield self.emit_tool_call_args(
                    retrieval_id,
                    json.dumps({"query": query, "knowledge_bases": kb_ids}),
                )
                yield self.emit_tool_call_end(retrieval_id)

                # Perform retrieval
                results = await self._retrieve(query, kb_ids)
                new_context = self._format_retrieved_context(results)
                all_retrieved_context += "\n\n" + new_context

                yield self.emit_tool_call_result(
                    tool_call_id=retrieval_id,
                    content=f"Retrieved {sum(len(r.chunks) for r in results)} documents",
                )

                # Add retrieval observation to history
                context.message_history.append(
                    LLMMessage(
                        role=MessageRole.USER,
                        content=f"Retrieved context:\n{new_context}",
                    )
                )

                yield self.emit_step_finished("retrieval")

            elif action == "answer":
                # Final answer - stream it for better UX
                answer = parsed.get("answer", full_content)
                sources = parsed.get("sources", [])

                # Emit final answer with streaming
                yield self.emit_step_started("final_answer")
                final_message_id = str(uuid4())
                yield self.emit_text_start(final_message_id)

                # Stream the answer in chunks
                chunk_size = 10
                for i in range(0, len(answer), chunk_size):
                    if context.is_cancelled():
                        return
                    chunk = answer[i : i + chunk_size]
                    yield self.emit_text_content(final_message_id, chunk)
                    await asyncio.sleep(0.02)

                # Add source citations if available
                if sources and self._rag_config.include_sources:
                    sources_text = "\n\n---\n**Sources:**\n" + "\n".join(
                        [f"- {src}" for src in sources]
                    )
                    # Stream sources too
                    for i in range(0, len(sources_text), chunk_size):
                        if context.is_cancelled():
                            return
                        chunk = sources_text[i : i + chunk_size]
                        yield self.emit_text_content(final_message_id, chunk)
                        await asyncio.sleep(0.02)

                yield self.emit_text_end(final_message_id)
                yield self.emit_step_finished("final_answer")

                # Emit state with retrieved context summary
                if all_retrieved_context:
                    yield StateSnapshotEvent(
                        snapshot={
                            "retrieved_documents": retrieval_attempt,
                            "knowledge_bases_used": self.knowledge_base_ids,
                        }
                    )

                return

            else:
                # Unknown action, treat as answer with streaming
                yield self.emit_step_started("final_answer")
                final_message_id = str(uuid4())
                yield self.emit_text_start(final_message_id)

                chunk_size = 10
                for i in range(0, len(full_content), chunk_size):
                    if context.is_cancelled():
                        return
                    chunk = full_content[i : i + chunk_size]
                    yield self.emit_text_content(final_message_id, chunk)
                    await asyncio.sleep(0.02)

                yield self.emit_text_end(final_message_id)
                yield self.emit_step_finished("final_answer")
                return

        # Max retrieval attempts reached, provide best answer
        yield self.emit_step_started("final_answer")

        final_message_id = str(uuid4())
        fallback_answer = (
            "I've searched the knowledge base multiple times but couldn't find "
            "a definitive answer. Based on what I found:\n\n"
            + (context.message_history[-1].content if context.message_history else "")
        )

        yield self.emit_text_start(final_message_id)

        # Stream the fallback answer
        chunk_size = 10
        for i in range(0, len(fallback_answer), chunk_size):
            if context.is_cancelled():
                return
            chunk = fallback_answer[i : i + chunk_size]
            yield self.emit_text_content(final_message_id, chunk)
            await asyncio.sleep(0.02)

        yield self.emit_text_end(final_message_id)
        yield self.emit_step_finished("final_answer")
