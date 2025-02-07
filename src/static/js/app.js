document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const fileInput = document.getElementById('fileInput');
    const imagePreview = document.querySelector('.image-preview');
    const generateBtn = document.getElementById('generateBtn');
    const ttsEnabled = document.getElementById('tts_enabled');
    const maxTokens = document.getElementById('max_tokens');
    const temperature = document.getElementById('temperature');
    const promptTemplate = document.getElementById('prompt_template');
    const loadingIndicator = document.querySelector('.loading-indicator');
    const errorMessage = document.querySelector('.error-message');
    const captionText = document.querySelector('.caption-text');
    const narrativeText = document.querySelector('.narrative-text');
    const audioSection = document.querySelector('.audio-section');
    const audioPlayer = document.querySelector('.audio-player');
    const resultsSection = document.querySelector('.results-section');

    // File upload handling
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showError('Invalid file type. Please upload an image file.');
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    });

    // Generate story
    generateBtn.addEventListener('click', async () => {
        if (!fileInput.files[0]) {
            showError('Please select an image first.');
            return;
        }

        try {
            showLoading(true);
            resultsSection.style.display = 'none';
            resultsSection.classList.remove('visible');

            // Prepare form data
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('tts', ttsEnabled.checked);
            
            if (maxTokens.value) {
                formData.append('max_tokens', maxTokens.value);
            }
            
            if (temperature.value) {
                formData.append('temperature', temperature.value);
            }
            
            if (promptTemplate.value) {
                formData.append('prompt_template', promptTemplate.value);
            }

            // Process image
            const response = await fetch('/process_with_narrative/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Validate response data
            if (!data.caption && !data.narrative) {
                throw new Error('Invalid response: missing caption and narrative');
            }

            // Update UI with results
            resultsSection.style.display = 'block';
            resultsSection.classList.add('visible');
            
            if (data.caption) {
                captionText.textContent = data.caption;
                captionText.parentElement.style.display = 'block';
            }

            if (data.narrative) {
                narrativeText.textContent = data.narrative;
                narrativeText.parentElement.style.display = 'block';
            }

            if (data.audio_file) {
                audioPlayer.src = `/audio/${data.audio_file}`;
                audioSection.style.display = 'block';
            } else {
                audioSection.style.display = 'none';
            }

        } catch (error) {
            showError('Error processing image: ' + error.message);
        } finally {
            showLoading(false);
        }
    });

    // Helper functions
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    function showLoading(show) {
        loadingIndicator.style.display = show ? 'flex' : 'none';
        generateBtn.disabled = show;
    }

    // Mobile menu handling
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');

    if (menuToggle && mobileNav) {
        menuToggle.addEventListener('click', () => {
            mobileNav.classList.toggle('active');
        });
    }

    // Responsive layout handling
    function updateLayout() {
        const width = window.innerWidth;
        const desktopLayout = document.querySelector('.desktop-layout');
        const tabletLayout = document.querySelector('.tablet-layout');
        const mobileMenu = document.querySelector('.mobile-menu');

        if (width > 768) {
            desktopLayout.style.display = 'block';
            tabletLayout.style.display = 'none';
            mobileMenu.style.display = 'none';
        } else if (width > 480) {
            desktopLayout.style.display = 'none';
            tabletLayout.style.display = 'block';
            mobileMenu.style.display = 'block';
        } else {
            desktopLayout.style.display = 'none';
            tabletLayout.style.display = 'none';
            mobileMenu.style.display = 'block';
        }
    }

    window.addEventListener('resize', updateLayout);
    updateLayout();
}); 