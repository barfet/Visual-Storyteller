# Visual Storyteller

A FastAPI-based service that generates creative narratives from images using AI. The service combines image captioning, narrative generation, and text-to-speech capabilities to transform images into engaging stories.

## 🚀 Features

- **Image Processing**: Upload and process JPG/PNG images
- **AI Captioning**: Generate accurate image descriptions using BLIP model
- **Narrative Generation**: Create creative stories from image captions using GPT-4
- **Text-to-Speech**: Convert narratives into audio using gTTS
- **RESTful API**: Full API support with FastAPI
- **Frontend Interface**: Simple web interface for direct interaction
- **Async Processing**: Efficient handling of concurrent requests
- **CI/CD Pipeline**: Automated testing and deployment to AWS App Runner

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI**: Web framework
- **Transformers**: BLIP image captioning
- **OpenAI API**: GPT-4 for narrative generation
- **gTTS**: Text-to-speech conversion
- **PyTest**: Testing framework with Playwright
- **Docker**: Containerization and AWS ECR
- **AWS**: App Runner, ECR, and IAM

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
├── .github/
│   └── workflows/     # CI/CD configuration
└── Dockerfile         # Container configuration
```

## 🚦 Getting Started

### Prerequisites

- Python 3.10+
- ffmpeg (for audio processing)
- OpenAI API key
- AWS credentials (for deployment)

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
pip install -r requirements-dev.txt  # For development
```

4. Create `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-0125-preview
OPENAI_MAX_TOKENS=200
OPENAI_TEMPERATURE=0.7
UPLOAD_DIR=data/sample_images
AUDIO_DIR=data/audio
```

### Running with Docker

```bash
docker build -t visual-storyteller .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key_here \
  -e UPLOAD_DIR=/app/data/sample_images \
  -e AUDIO_DIR=/app/data/audio \
  visual-storyteller
```

## 🔄 API Endpoints

- `POST /process/`: Process image and generate caption
- `POST /process_with_narrative/`: Generate caption and narrative
- `GET /audio/{filename}`: Retrieve generated audio file
- `GET /health`: Health check endpoint

## 🧪 Testing

Run tests using pytest:
```bash
# Run all tests
python tests/run_tests.py --stage all

# Run specific test categories
python tests/run_tests.py --stage unit
python tests/run_tests.py --stage integration
```

## 📊 Performance

- Image processing: ~2-3 seconds
- Narrative generation: ~5-10 seconds
- Audio generation: ~2-3 seconds
- Concurrent request handling: Up to 50 requests/minute
- App Runner configuration: 1 CPU, 2GB memory

## 🔐 Security

- File type validation
- Size limits on uploads
- Automatic file cleanup
- Environment variable protection
- No sensitive data in logs
- AWS IAM role-based access

## 🚀 Deployment

The application uses GitHub Actions for CI/CD:
1. Automated testing on pull requests
2. Docker image build and push to AWS ECR
3. Deployment to AWS App Runner
4. Health check monitoring

Required AWS secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `APPRUNNER_SERVICE_ROLE_ARN`
- `OPENAI_API_KEY`

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
- [AWS App Runner](https://aws.amazon.com/apprunner/) for deployment

