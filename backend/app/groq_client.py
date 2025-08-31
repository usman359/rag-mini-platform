import groq
import logging
from typing import List, Dict, Any, Optional
from .config import settings

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.client = groq.Groq(api_key=self.api_key)
    
    def chat_completions_create(self, model: str = None, messages: List[Dict[str, str]] = None, 
                               temperature: float = 0.7, max_tokens: int = 1000, **kwargs):
        """Mimic OpenAI's chat.completions.create interface"""
        try:
            # Use provided model or default
            model_name = model or self.model
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Convert Groq response to OpenAI format
            return self._convert_groq_response_to_openai_format(response)
            
        except Exception as e:
            logger.error(f"Error in Groq chat completion: {e}")
            raise
    
    def _convert_groq_response_to_openai_format(self, groq_response) -> Dict[str, Any]:
        """Convert Groq response to OpenAI format"""
        # Handle both object and dict responses
        if hasattr(groq_response, 'choices'):
            # Object response
            choices = groq_response.choices
            model = groq_response.model
            usage = groq_response.usage
        else:
            # Dict response
            choices = groq_response['choices']
            model = groq_response.get('model', self.model)
            usage = groq_response.get('usage', {})
        
        # Handle usage object vs dict
        if hasattr(usage, 'prompt_tokens'):
            usage_dict = {
                'prompt_tokens': usage.prompt_tokens,
                'completion_tokens': usage.completion_tokens,
                'total_tokens': usage.total_tokens
            }
        else:
            usage_dict = usage
        
        # Extract the first choice
        first_choice = choices[0]
        
        # Handle both object and dict for choice
        if hasattr(first_choice, 'message'):
            message_content = first_choice.message.content
            finish_reason = getattr(first_choice, 'finish_reason', 'stop')
        else:
            message_content = first_choice['message']['content']
            finish_reason = first_choice.get('finish_reason', 'stop')
        
        return {
            "choices": [
                {
                    "message": {
                        "content": message_content,
                        "role": "assistant"
                    },
                    "finish_reason": finish_reason,
                    "index": 0
                }
            ],
            "model": model,
            "usage": {
                "prompt_tokens": usage_dict.get('prompt_tokens', 0),
                "completion_tokens": usage_dict.get('completion_tokens', 0),
                "total_tokens": usage_dict.get('total_tokens', 0)
            }
        }
    
    def models_list(self):
        """Mimic OpenAI's models.list interface"""
        try:
            models_response = self.client.models.list()
            
            # Handle both object and dict responses
            if hasattr(models_response, 'data'):
                models_data = models_response.data
            else:
                models_data = models_response.get('data', [])
            
            return {
                "data": [
                    {
                        "id": model.get('id') if isinstance(model, dict) else model.id,
                        "object": "model",
                        "created": 0,
                        "owned_by": "groq"
                    }
                    for model in models_data
                ]
            }
        except Exception as e:
            logger.error(f"Error listing Groq models: {e}")
            return {"data": []}
