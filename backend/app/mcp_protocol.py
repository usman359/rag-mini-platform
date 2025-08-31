import logging
from typing import List, Dict, Any, Optional
from .config import settings
from .groq_client import GroqClient
import json

logger = logging.getLogger(__name__)

class MCPProtocol:
    def __init__(self):
        self.client = GroqClient()
        logger.info(f"Using Groq with model: {settings.GROQ_MODEL}")
        
        self.conversation_memory = {}  # Store conversation context
    
    def llm_a_first_pass(self, query: str, retrieved_context: List[str], conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """LLM-A performs first-pass retrieval and generates initial response"""
        try:
            # Prepare context from retrieved documents
            context_text = "\n\n".join(retrieved_context) if retrieved_context else "No relevant context found."
            
            # Prepare conversation history for context
            history_text = ""
            if conversation_history:
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])  # Last 5 messages
            
            # Create prompt for LLM-A
            prompt = f"""
{settings.LLM_A_SYSTEM_PROMPT}

Previous conversation context:
{history_text}

Document context to answer from:
{context_text}

User's question: {query}

Answer the question based on the document context above. If the information isn't in the context, say so clearly. Give a natural, conversational response."""

            response = self.client.chat_completions_create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": settings.LLM_A_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # Slightly higher for more natural responses
                max_tokens=400
            )
            
            initial_response = response["choices"][0]["message"]["content"]
            
            return {
                "initial_response": initial_response,
                "context_used": retrieved_context,
                "query": query,
                "conversation_history": conversation_history
            }
            
        except Exception as e:
            logger.error(f"Error in LLM-A first pass: {e}")
            raise
    
    def llm_b_refinement(self, llm_a_output: Dict[str, Any]) -> str:
        """LLM-B refines the response from LLM-A"""
        try:
            # Prepare the context for LLM-B
            context_text = "\n\n".join(llm_a_output["context_used"]) if llm_a_output["context_used"] else "No context available."
            
            history_text = ""
            if llm_a_output["conversation_history"]:
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in llm_a_output["conversation_history"][-5:]])
            
            prompt = f"""
{settings.LLM_B_SYSTEM_PROMPT}

Previous conversation:
{history_text}

Document context:
{context_text}

Original question: {llm_a_output['query']}

Current response to improve:
{llm_a_output['initial_response']}

Make this response sound more natural and conversational. Remove any formal or robotic language. Keep it concise but friendly."""

            response = self.client.chat_completions_create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": settings.LLM_B_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Balanced for natural but consistent responses
                max_tokens=400
            )
            
            refined_response = response["choices"][0]["message"]["content"]
            
            return refined_response
            
        except Exception as e:
            logger.error(f"Error in LLM-B refinement: {e}")
            raise
    
    def process_query(self, query: str, retrieved_context: List[str], conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Complete MCP process: LLM-A first pass + LLM-B refinement"""
        try:
            # Step 1: LLM-A first pass
            llm_a_output = self.llm_a_first_pass(query, retrieved_context, conversation_history)
            
            # Step 2: LLM-B refinement
            final_response = self.llm_b_refinement(llm_a_output)
            
            # Step 3: Update conversation memory
            conversation_id = self._get_conversation_id(conversation_history)
            if conversation_id not in self.conversation_memory:
                self.conversation_memory[conversation_id] = []
            
            self.conversation_memory[conversation_id].append({
                "query": query,
                "context_used": retrieved_context,
                "llm_a_response": llm_a_output["initial_response"],
                "final_response": final_response
            })
            
            return {
                "response": final_response,
                "context_used": retrieved_context,
                "conversation_id": conversation_id,
                "llm_a_response": llm_a_output["initial_response"],  # For debugging/transparency
                "processing_steps": {
                    "llm_a_first_pass": "completed",
                    "llm_b_refinement": "completed"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in MCP process: {e}")
            raise
    
    def _get_conversation_id(self, conversation_history: List[Dict[str, str]]) -> str:
        """Generate a conversation ID based on history"""
        if not conversation_history:
            return "new_conversation"
        
        # Use the first user message as conversation identifier
        for msg in conversation_history:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                return f"conv_{hash(content) % 10000}"
        
        return "new_conversation"
    
    def get_conversation_memory(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation memory for a specific conversation"""
        return self.conversation_memory.get(conversation_id, [])
