import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.narrative_service import NarrativeService, NarrativeGenerationError
from src.config import settings

@pytest.fixture
def mock_openai_client():
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test narrative"))]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client

@pytest.fixture
def narrative_service(mock_openai_client):
    with patch('src.services.narrative_service.AsyncOpenAI', return_value=mock_openai_client):
        service = NarrativeService(api_key="test_key")
        return service

@pytest.mark.asyncio
async def test_generate_narrative(narrative_service, mock_openai_client):
    """Test successful narrative generation from a caption."""
    test_caption = "a beautiful mountain landscape with snow peaks"
    
    # Generate narrative
    narrative = await narrative_service.generate_narrative(test_caption)
    
    # Verify the narrative
    assert isinstance(narrative, str)
    assert narrative == "Test narrative"
    
    # Verify OpenAI API was called with correct parameters
    mock_openai_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == settings.OPENAI_MODEL
    assert call_kwargs["max_tokens"] == settings.OPENAI_MAX_TOKENS
    assert call_kwargs["temperature"] == settings.OPENAI_TEMPERATURE
    assert len(call_kwargs["messages"]) == 2
    assert call_kwargs["messages"][0]["role"] == "system"
    assert call_kwargs["messages"][1]["role"] == "user"
    assert test_caption in call_kwargs["messages"][1]["content"]

@pytest.mark.asyncio
async def test_empty_caption(narrative_service):
    """Test that empty caption raises an error."""
    with pytest.raises(ValueError) as exc_info:
        await narrative_service.generate_narrative("")
    
    assert "Caption cannot be empty" in str(exc_info.value)

@pytest.mark.asyncio
async def test_api_error(narrative_service, mock_openai_client):
    """Test handling of OpenAI API errors."""
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
    
    with pytest.raises(NarrativeGenerationError) as exc_info:
        await narrative_service.generate_narrative("test caption")
    
    assert "Failed to generate narrative" in str(exc_info.value)

@pytest.mark.asyncio
async def test_custom_prompt():
    """Test narrative generation with custom prompt template."""
    custom_prompt = "Create a mysterious story about this scene: {caption}"
    
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test narrative"))]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    with patch('src.services.narrative_service.AsyncOpenAI', return_value=mock_client):
        service = NarrativeService(
            api_key="test_key",
            prompt_template=custom_prompt
        )
        
        narrative = await service.generate_narrative("a dark forest at night")
        
        # Verify the narrative
        assert narrative == "Test narrative"
        
        # Verify custom prompt was used
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert "mysterious story" in call_kwargs["messages"][1]["content"]

@pytest.mark.asyncio
async def test_long_caption(narrative_service, mock_openai_client):
    """Test handling of very long captions."""
    long_caption = "a " * 1000  # Very long caption
    
    await narrative_service.generate_narrative(long_caption)
    
    # Verify the API call
    call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
    # Check that the message content is within reasonable limits
    assert len(call_kwargs["messages"][1]["content"]) <= 2000  # Reasonable limit for API 