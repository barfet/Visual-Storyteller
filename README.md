# Visual Storyteller

A FastAPI-based service that generates creative narratives from images using AI. The service combines image captioning, narrative generation, and text-to-speech capabilities to transform images into engaging stories.

## 🚀 Features

- **Image Processing**: Upload and process JPG/PNG images
- **AI Captioning**: Generate accurate image descriptions using BLIP model
- **Narrative Generation**: Create creative stories from image captions using GPT models
- **Text-to-Speech**: Convert narratives into audio using gTTS
- **RESTful API**: Full API support with FastAPI
- **Frontend Interface**: Simple web interface for direct interaction
- **Async Processing**: Efficient handling of concurrent requests

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI**: Web framework
- **Transformers**: BLIP image captioning
- **OpenAI API**: Narrative generation
- **gTTS**: Text-to-speech conversion
- **PyTest**: Testing framework
- **Docker**: Containerization
- **Playwright**: E2E testing

## 📁 Project Structure

```
visual_storyteller/
├── src/
│   ├── api/            # API endpoints and routing
│   ├── services/       # Core business logic
│   ├── static/         # Frontend assets
│   └── config.py       # Configuration management
├── tests/
│   ├── test_api/      # API integration tests
│   ├── test_services/ # Unit tests
│   └── test_e2e/      # End-to-end tests
├── data/
│   ├── sample_images/ # Image storage
│   └── audio/         # Generated audio files
└── docker/            # Docker configuration
```

## 🚦 Getting Started

### Prerequisites

- Python 3.10+
- ffmpeg (for audio processing)
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/visual-storyteller.git
cd visual-storyteller
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
UPLOAD_DIR=data/sample_images
AUDIO_DIR=data/audio
```

### Running with Docker

```bash
docker build -t visual-storyteller .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_api_key_here visual-storyteller
```

## 🔄 API Endpoints

- `POST /process/`: Process image and generate caption
- `POST /process_with_narrative/`: Generate caption and narrative
- `GET /audio/{filename}`: Retrieve generated audio file

## 🧪 Testing

Run tests using pytest:
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_services  # Unit tests
pytest tests/test_api      # Integration tests
pytest tests/test_e2e      # E2E tests
```

## 📊 Performance

- Image processing: ~2-3 seconds
- Narrative generation: ~5-10 seconds
- Audio generation: ~2-3 seconds
- Concurrent request handling: Up to 50 requests/minute

## 🔐 Security

- File type validation
- Size limits on uploads
- Automatic file cleanup
- Environment variable protection
- No sensitive data in logs

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [BLIP](https://github.com/salesforce/BLIP) for image captioning
- [OpenAI](https://openai.com/) for GPT models
- [FastAPI](https://fastapi.tiangolo.com/) framework
- [gTTS](https://gtts.readthedocs.io/) for text-to-speech

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/visual-storyteller](https://github.com/yourusername/visual-storyteller)
```
