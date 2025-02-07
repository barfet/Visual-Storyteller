import os
import pytest
from playwright.sync_api import Page, expect
from fastapi.testclient import TestClient
from src.api.main import app
import time
from pathlib import Path
from tests.test_api.fixtures import realistic_image

def test_complete_workflow(page: Page, test_server, realistic_image):
    """
    Test the complete workflow from the frontend perspective:
    1. Load the main page
    2. Upload an image
    3. Verify image preview
    4. Generate narrative with TTS
    5. Verify audio playback availability
    """
    print(f"\nTesting with image at: {realistic_image}")
    print(f"Image exists: {os.path.exists(realistic_image)}")
    print(f"Image size: {os.path.getsize(realistic_image)} bytes")
    
    # Navigate to the application
    page.goto(f"http://{test_server.host}:{test_server.port}")
    
    # Enable debug logging
    page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
    page.on("pageerror", lambda err: print(f"Browser error: {err}"))
    page.on("request", lambda req: print(f"Request: {req.method} {req.url}"))
    page.on("response", lambda res: print(f"Response: {res.status} {res.url}"))
    
    # Verify page title and main elements
    expect(page).to_have_title("Visual Storyteller")
    expect(page.get_by_text("Upload an image to begin")).to_be_visible()
    
    # Upload image
    with page.expect_file_chooser() as fc_info:
        page.click('.file-input-label')
    file_chooser = fc_info.value
    file_chooser.set_files(realistic_image)
    
    # Wait for image preview
    preview = page.locator(".image-preview img")
    expect(preview).to_be_visible(timeout=10000)
    
    # Enable TTS and click generate
    page.check('input[type="checkbox"]#tts_enabled')
    page.click("button:text('Generate Story')")
    
    # Wait for results with longer timeout and debug info
    caption_element = page.locator(".caption-text")
    narrative_element = page.locator(".narrative-text")
    audio_element = page.locator("audio")
    
    print("\nWaiting for caption...")
    expect(caption_element).to_be_visible(timeout=30000)
    caption = caption_element.text_content()
    print(f"Caption received: '{caption}'")
    
    print("\nWaiting for narrative...")
    expect(narrative_element).to_be_visible(timeout=30000)
    narrative = narrative_element.text_content()
    print(f"Narrative received: '{narrative}'")
    
    print("\nWaiting for audio player...")
    expect(audio_element).to_be_visible(timeout=30000)
    
    # Verify content
    assert len(caption) > 0, "Caption should not be empty"
    assert len(narrative) > 20, "Narrative should be meaningful length"
    assert audio_element.get_attribute("src").startswith("/audio/"), "Audio source should be set"

def test_error_handling(page: Page, test_server):
    """Test frontend error handling for invalid file uploads."""
    page.goto(f"http://{test_server.host}:{test_server.port}")
    
    # Try to upload invalid file
    with page.expect_file_chooser() as fc_info:
        page.click('.file-input-label')
    file_chooser = fc_info.value
    
    # Create temporary text file
    invalid_file = Path("temp_invalid.txt")
    invalid_file.write_text("Not an image")
    file_chooser.set_files(str(invalid_file))
    
    # Verify error message
    expect(page.locator(".error-message")).to_be_visible(timeout=5000)
    error_text = page.locator(".error-message").text_content()
    assert "Invalid file type" in error_text
    
    # Cleanup
    invalid_file.unlink()

def test_custom_narrative_options(page: Page, test_server, realistic_image):
    """Test custom narrative generation options."""
    page.goto(f"http://{test_server.host}:{test_server.port}")
    
    # Upload image
    with page.expect_file_chooser() as fc_info:
        page.click('.file-input-label')
    file_chooser = fc_info.value
    file_chooser.set_files(realistic_image)
    
    # Wait for image preview
    expect(page.locator(".image-preview img")).to_be_visible(timeout=10000)
    
    # Set custom options
    page.fill('input[name="max_tokens"]', "100")
    page.fill('input[name="temperature"]', "0.8")
    page.fill('textarea[name="prompt_template"]', "Create a mysterious story about: {caption}")
    
    # Generate narrative
    page.click("button:text('Generate Story')")
    
    # Wait for and verify results
    expect(page.locator(".narrative-text")).to_be_visible(timeout=30000)
    narrative = page.locator(".narrative-text").text_content()
    
    assert len(narrative.split()) <= 100, "Narrative should respect max tokens"
    mysterious_words = ["mysterious", "strange", "unknown", "curious", "wonder"]
    assert any(word in narrative.lower() for word in mysterious_words), "Narrative should follow custom prompt"

def test_responsive_design(page: Page, test_server):
    """Test responsive design behavior."""
    # Test mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"http://{test_server.host}:{test_server.port}")
    
    # Verify mobile menu/layout
    expect(page.locator(".mobile-menu")).to_be_visible()
    
    # Test tablet viewport
    page.set_viewport_size({"width": 768, "height": 1024})
    page.reload()
    
    # Verify tablet layout
    expect(page.locator(".tablet-layout")).to_be_visible()
    
    # Test desktop viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.reload()
    
    # Verify desktop layout
    expect(page.locator(".desktop-layout")).to_be_visible()

def test_performance_metrics(page: Page, test_server, realistic_image):
    """Test performance metrics and loading states."""
    page.goto(f"http://{test_server.host}:{test_server.port}")
    
    # Upload image and measure processing time
    start_time = time.time()
    
    with page.expect_file_chooser() as fc_info:
        page.click('.file-input-label')
    file_chooser = fc_info.value
    file_chooser.set_files(realistic_image)
    
    # Wait for image preview to load
    expect(page.locator(".image-preview img")).to_be_visible(timeout=5000)
    
    # Click generate button
    page.click('#generateBtn')
    
    # Wait for complete processing
    expect(page.locator(".narrative-text")).to_be_visible(timeout=30000)
    
    processing_time = time.time() - start_time
    assert processing_time <= 15, "Processing should complete within 15 seconds"
    
    # Verify loading states
    expect(page.locator(".loading-indicator")).not_to_be_visible()
    expect(page.locator(".error-message")).not_to_be_visible()
    
    # Verify content
    narrative = page.locator(".narrative-text").text_content()
    assert len(narrative) > 0, "Narrative should not be empty" 