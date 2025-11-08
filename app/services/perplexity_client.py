"""
Perplexity AI API client
"""
import httpx
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.logger import logger


class PerplexityClient:
    """Client for interacting with Perplexity AI API"""
    
    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def query(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: str = "llama-3.1-sonar-small-128k-online"
    ) -> Dict[str, Any]:
        """Query Perplexity API"""
        try:
            if not self.api_key:
                raise Exception("Perplexity API key not configured")
            
            # Build messages
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context: {context}"
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Prepare request
            payload = {
                "model": model,
                "messages": messages
            }
            
            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info("Received response from Perplexity")
                
                return {
                    "answer": result["choices"][0]["message"]["content"],
                    "sources": result.get("citations", []),
                    "model": model
                }
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error querying Perplexity: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error querying Perplexity: {str(e)}")
            raise
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Perform a search query using Perplexity"""
        try:
            return await self.query(
                prompt=query,
                model="llama-3.1-sonar-small-128k-online"
            )
        except Exception as e:
            logger.error(f"Error searching with Perplexity: {str(e)}")
            raise


# Create global instance
perplexity_client = PerplexityClient()

