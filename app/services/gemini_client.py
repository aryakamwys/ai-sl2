"""
Google Gemini API client
"""
import google.generativeai as genai
from typing import Optional, List
from app.core.config import settings
from app.core.logger import logger


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self):
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            if not settings.GEMINI_API_KEY:
                logger.warning("Gemini API key not configured")
                return
            
            # Configure API key
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini client initialized with model: {settings.GEMINI_MODEL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response using Gemini"""
        try:
            if not self.model:
                raise Exception("Gemini client not initialized")
            
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"""Context Information:
{context}

User Question: {prompt}

Please provide a helpful and accurate answer based on the context provided."""
            
            # Generate content
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature or settings.GEMINI_TEMPERATURE,
                )
            )
            
            logger.info("Generated response from Gemini")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            raise
    
    def generate_with_rag(
        self,
        query: str,
        retrieved_docs: List[str],
        temperature: Optional[float] = None
    ) -> str:
        """Generate response using RAG approach"""
        try:
            # Build context from retrieved documents
            context = "\n\n".join([
                f"Document {i+1}:\n{doc}"
                for i, doc in enumerate(retrieved_docs)
            ])
            
            # Create RAG prompt
            prompt = f"""Based on the following retrieved documents, please answer the user's question.
If the answer cannot be found in the documents, please say so.

Retrieved Documents:
{context}

User Question: {query}

Answer:"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature or settings.GEMINI_TEMPERATURE,
                )
            )
            
            logger.info("Generated RAG response from Gemini")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            raise


# Create global instance
gemini_client = GeminiClient()

