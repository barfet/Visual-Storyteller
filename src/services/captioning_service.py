from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from typing import Optional
from src.config import settings
import os

class CaptioningService:
    """Service for generating captions from images using the BLIP model."""
    
    def __init__(self, processor: Optional[BlipProcessor] = None, model: Optional[BlipForConditionalGeneration] = None):
        """
        Initialize the captioning service.
        
        Args:
            processor: Optional pre-initialized BLIP processor
            model: Optional pre-initialized BLIP model
        """
        self._processor = processor
        self._model = model
        self.device = settings.DEVICE if torch.cuda.is_available() else "cpu"
    
    @property
    def processor(self):
        """Lazy initialization of the processor."""
        if self._processor is None:
            try:
                self._processor = BlipProcessor.from_pretrained(
                    settings.BLIP_MODEL,
                    local_files_only=True,  # Use cached files only
                    cache_dir=os.getenv('TRANSFORMERS_CACHE', None)
                )
            except Exception as e:
                raise Exception(f"Failed to load BLIP processor: {str(e)}. Please ensure enough disk space and model cache exists.")
        return self._processor
    
    @property
    def model(self):
        """Lazy initialization of the model."""
        if self._model is None:
            try:
                self._model = BlipForConditionalGeneration.from_pretrained(
                    settings.BLIP_MODEL,
                    local_files_only=True,  # Use cached files only
                    cache_dir=os.getenv('TRANSFORMERS_CACHE', None)
                )
                self._model.to(self.device)
            except Exception as e:
                raise Exception(f"Failed to load BLIP model: {str(e)}. Please ensure enough disk space and model cache exists.")
        return self._model
    
    async def generate_caption(self, image_path: str) -> str:
        """
        Generate a caption for the given image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Generated caption for the image
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            Exception: If the image is invalid or processing fails
        """
        try:
            # Load and preprocess the image
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(image, return_tensors="pt")
            
            # Move inputs to device if they're tensors
            if isinstance(inputs, dict):
                inputs = {k: v.to(self.device) if hasattr(v, 'to') else v for k, v in inputs.items()}
            
            # Generate caption
            output = self.model.generate(**inputs)
            caption = self.processor.decode(output[0], skip_special_tokens=True)
            
            return caption
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}") 