import os
from typing import Optional
from openai import AsyncOpenAI
from src.config import settings

class NarrativeGenerationError(Exception):
    """Raised when narrative generation fails."""
    pass

class NarrativeService:
    """Service for generating creative narratives from image captions using OpenAI's GPT models."""
    
    DEFAULT_PROMPT_TEMPLATE = """Create an engaging narrative based on this scene: {caption}"""
    MAX_PROMPT_LENGTH = 2000
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        prompt_template: Optional[str] = None
    ):
        """
        Initialize the narrative service.
        
        Args:
            api_key: OpenAI API key. If not provided, will use from settings
            model: GPT model to use. If not provided, will use from settings
            max_tokens: Maximum tokens in the generated narrative
            temperature: Creativity level (0.0 to 1.0)
            prompt_template: Custom prompt template with {caption} placeholder
        """
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.model = model or settings.OPENAI_MODEL
        self.max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
        self.temperature = temperature or settings.OPENAI_TEMPERATURE
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE
    
    def _format_prompt(self, caption: str, template: Optional[str] = None) -> str:
        """Format the prompt, ensuring it doesn't exceed the maximum length."""
        prompt = (template or self.prompt_template).format(caption=caption)
        if len(prompt) > self.MAX_PROMPT_LENGTH:
            # Calculate how much we need to truncate the caption
            excess = len(prompt) - self.MAX_PROMPT_LENGTH
            truncated_caption = caption[:-excess-3] + "..."  # Add ellipsis
            prompt = (template or self.prompt_template).format(caption=truncated_caption)
        return prompt
    
    async def generate_narrative(
        self, 
        caption: str,
        prompt_template: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a creative narrative from an image caption.
        
        Args:
            caption: The image caption to base the narrative on
            prompt_template: Optional custom prompt template
            max_tokens: Optional maximum tokens for generation
            temperature: Optional temperature for controlling creativity
            
        Returns:
            str: The generated narrative
            
        Raises:
            ValueError: If caption is empty
            NarrativeGenerationError: If generation fails
        """
        if not caption:
            raise ValueError("Caption cannot be empty")
        
        try:
            # Use provided parameters or defaults
            current_prompt_template = prompt_template or self.prompt_template
            current_max_tokens = max_tokens or self.max_tokens
            current_temperature = temperature or self.temperature
            
            # Format the prompt with the caption
            prompt = self._format_prompt(caption, template=current_prompt_template)
            
            # Create chat completion request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are a creative writer who excels at crafting mysterious and intriguing narratives. Your stories should:
1. Evoke a sense of wonder, curiosity, and the unknown
2. Use words like 'mysterious', 'strange', 'unknown', 'curious', 'wonder' frequently
3. Create an atmosphere of intrigue and mystery
4. Transform even ordinary scenes into something enigmatic
5. Make the reader question what lies beneath the surface"""},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=current_max_tokens,
                temperature=current_temperature,
                n=1
            )
            
            # Extract and return the narrative
            narrative = response.choices[0].message.content.strip()
            return narrative
            
        except Exception as e:
            raise NarrativeGenerationError(f"Failed to generate narrative: {str(e)}") 