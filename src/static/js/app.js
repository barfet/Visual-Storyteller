document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const ttsToggle = document.getElementById('ttsToggle');
    const languageSelect = document.getElementById('languageSelect');
    const resultSection = document.getElementById('resultSection');
    const loadingSection = document.getElementById('loadingSection');
    const audioSection = document.getElementById('audioSection');
    const previewImage = document.getElementById('previewImage');
    const captionText = document.getElementById('captionText');
    const narrativeText = document.getElementById('narrativeText');
    const audioPlayer = document.getElementById('audioPlayer');
    const downloadAudio = document.getElementById('downloadAudio');

    // Handle drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('highlight');
    }

    function unhighlight(e) {
        dropZone.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        if (!file.type.startsWith('image/')) {
            showError('Please upload an image file');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            showError('File size should be less than 5MB');
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
        };
        reader.readAsDataURL(file);

        // Process the image
        processImage(file);
    }

    async function processImage(file) {
        try {
            showLoading();

            const formData = new FormData();
            formData.append('file', file);
            formData.append('tts', ttsToggle.checked);
            formData.append('language', languageSelect.value);

            const response = await fetch('/process_with_narrative/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            showError('Error processing image: ' + error.message);
        } finally {
            hideLoading();
        }
    }

    function displayResults(data) {
        captionText.textContent = data.caption;
        narrativeText.textContent = data.narrative;

        if (data.audio_file) {
            audioPlayer.src = `/audio/${data.audio_file.split('/').pop()}`;
            audioSection.classList.remove('hidden');
            
            // Update download button
            downloadAudio.onclick = () => {
                window.location.href = `/audio/${data.audio_file.split('/').pop()}`;
            };
        } else {
            audioSection.classList.add('hidden');
        }

        resultSection.classList.remove('hidden');
    }

    function showLoading() {
        loadingSection.classList.remove('hidden');
        resultSection.classList.add('hidden');
    }

    function hideLoading() {
        loadingSection.classList.add('hidden');
    }

    function showError(message) {
        // You can implement a more sophisticated error display
        alert(message);
    }

    // Add highlight class for upload box
    dropZone.addEventListener('dragenter', () => {
        dropZone.style.borderColor = 'var(--primary-color)';
        dropZone.style.backgroundColor = 'var(--background)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '';
        dropZone.style.backgroundColor = '';
    });

    // Handle language select visibility based on TTS toggle
    ttsToggle.addEventListener('change', () => {
        languageSelect.style.display = ttsToggle.checked ? 'block' : 'none';
    });
}); 