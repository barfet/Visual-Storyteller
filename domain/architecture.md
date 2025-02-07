Below is a detailed technical and architecture document for the Visual Storyteller project. This document is intended to serve as a reference for the engineering team during implementation and later for system maintenance and documentation. It covers the technical specifications, implementation guidance, component design, and deployment details.

Technical and Architecture Document

Project: Visual Storyteller
Date: 2025-02-07
Authors: [Your Team Names]

Table of Contents
	1.	Introduction
	2.	System Overview
	3.	Architecture Diagram & Components
	4.	Technology Stack
	5.	Component Specifications
5.1. Image Upload & Storage Service
5.2. Image Captioning Module
5.3. Narrative Generation Module
5.4. Text-to-Speech (TTS) Module
5.5. API Service Layer
	6.	Data Flow & Interaction
	7.	External Dependencies & Integrations
	8.	Deployment Architecture & Environment
	9.	Security, Error Handling, and Logging
	10.	Testing Strategy
	11.	CI/CD & Deployment Pipeline
	12.	Environment Configuration & Variables
	13.	Appendices

1. Introduction

The Visual Storyteller project is a multi-modal application that transforms an uploaded image into a creative narrative. The system first generates an image caption using a pre-trained computer vision (CV) model, then feeds that caption into a large language model (LLM) to produce an extended narrative. Optionally, the narrative is converted into an audio format using a Text-to-Speech (TTS) service. The service is exposed via a RESTful API, with scalability and cloud deployment in mind.

2. System Overview

High-Level Goals:
	•	Provide an end-to-end pipeline from image upload to multi-modal content generation.
	•	Demonstrate expertise in computer vision, language models, and audio synthesis.
	•	Ensure the system is production-ready with robust error handling, logging, and scalable deployment.

Key Functional Blocks:
	•	Image Upload/Storage: Accept and temporarily store image files.
	•	Image Captioning: Process images to produce descriptive captions.
	•	Narrative Generation: Generate creative narratives using LLMs based on captions.
	•	TTS Conversion (Optional): Convert narratives into audio files.
	•	API Exposure: Offer RESTful endpoints for client interactions.
	•	Cloud Deployment: Run in a containerized environment to ensure scalability and reliability.

3. Architecture Diagram & Components

Below is a textual representation of the architecture. (A diagram can be generated later using diagramming tools such as Lucidchart or Draw.io.)

            +-----------------------+
            |   Client / Frontend   |
            +----------+------------+
                       |
                       | HTTP(S) Request (Image Upload)
                       |
            +----------v------------+
            |   API Gateway (FastAPI)|
            +----------+------------+
                       |
        +--------------+--------------+
        |                             |
+-------v-------+              +------v-------+
|  Image Upload |              | API Routing  |
|  & Storage    |              | & Orchestration|
+-------+-------+              +------+-------+
        |                              |
        |  Local / Cloud File Storage  |
        +------------------------------+
                       |
          +------------v-------------+
          |  Processing Pipeline     |
          |  (Microservices/Modules) |
          +------------+-------------+
                       |
            +----------+-----------+-----------+
            |          |           |           |
+-----------v--+  +----v------+  +--v-------+  +---v----+
| Captioning   |  | Narrative |  |   TTS    |  | Logging|
| Module       |  | Generation|  |  Module  |  | Module |
+--------------+  +-----------+  +----------+  +--------+
                       |
                       |
            +----------v-----------+
            |  API Response Builder|
            +----------------------+
                       |
                       |
            +----------v----------+
            |  HTTP Response to   |
            |    Client (JSON +   |
            |   Audio Link if TTS)|
            +---------------------+

Components:
	•	Client/Frontend: Can be a web app, mobile app, or API consumer.
	•	API Gateway: The main entry point using FastAPI.
	•	Storage: Temporary storage for image files and generated audio.
	•	Processing Modules:
	•	Image Captioning Module: Uses a pre-trained model (e.g., BLIP).
	•	Narrative Generation Module: Interacts with LLM (OpenAI API or alternative).
	•	TTS Module: Uses a TTS engine (gTTS or AWS Polly) to convert text to speech.
	•	Logging Module: Handles logging of requests, responses, and errors.
	•	Deployment Environment: Dockerized service deployed in a cloud environment.

4. Technology Stack
	•	Programming Language: Python 3.9+
	•	Web Framework: FastAPI
	•	ML Libraries:
	•	Image Captioning: Hugging Face Transformers, PyTorch
	•	LLM Integration: OpenAI API or similar
	•	TTS Library: gTTS or AWS Polly SDK
	•	Containerization: Docker
	•	Cloud Platforms: AWS (Lambda/Fargate/API Gateway) or GCP (Cloud Run)
	•	Additional Tools: Uvicorn (ASGI server), python-dotenv for configuration

5. Component Specifications

5.1 Image Upload & Storage Service
	•	Responsibilities:
	•	Accept image files (JPG, PNG) via HTTP POST.
	•	Validate file types and sizes.
	•	Save images to a local/cloud directory with unique identifiers.
	•	Implementation Guidance:
	•	Use FastAPI’s File and UploadFile classes.
	•	Generate a UUID-based filename.
	•	Store files in a directory (e.g., /data/sample_images).
	•	Key Code Snippet:

import os, uuid, shutil
from fastapi import UploadFile

UPLOAD_DIR = "data/sample_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(file: UploadFile) -> str:
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path



5.2 Image Captioning Module
	•	Responsibilities:
	•	Load and preprocess the uploaded image.
	•	Generate a descriptive caption using a pre-trained model (e.g., Salesforce’s BLIP).
	•	Implementation Guidance:
	•	Use PIL for image handling.
	•	Utilize the Hugging Face Transformers library.
	•	Ensure proper model caching and error handling.
	•	Key Code Snippet:

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Initialize model and processor once at service startup
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(image_path: str) -> str:
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption



5.3 Narrative Generation Module
	•	Responsibilities:
	•	Accept an image caption as input.
	•	Generate a creative narrative using an LLM.
	•	Implementation Guidance:
	•	Leverage the OpenAI API (or another LLM provider).
	•	Format prompts carefully to guide the narrative generation.
	•	Include configurable parameters such as temperature and max tokens.
	•	Key Code Snippet:

import os, openai
from dotenv import load_dotenv

load_dotenv()  # Ensure .env contains the OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_narrative(caption: str) -> str:
    prompt = f"Using the following image description, write an engaging narrative:\n\n\"{caption}\"\n\nNarrative:"
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=200,
        temperature=0.7
    )
    return response.choices[0].text.strip()



5.4 Text-to-Speech (TTS) Module
	•	Responsibilities:
	•	Convert the generated narrative text into an audio file.
	•	Implementation Guidance:
	•	Use gTTS for quick TTS conversion or AWS Polly for more production-grade quality.
	•	Save the resulting audio file in a designated storage folder.
	•	Return a reference (filename/path) for later retrieval.
	•	Key Code Snippet:

from gtts import gTTS

def text_to_speech(text: str, output_filename: str = "output.mp3") -> str:
    tts = gTTS(text=text, lang='en')
    tts.save(output_filename)
    return output_filename



5.5 API Service Layer
	•	Responsibilities:
	•	Expose endpoints for image upload and processing.
	•	Orchestrate the sequence: file storage → caption generation → narrative creation → (optional) TTS conversion.
	•	Serve generated audio files via dedicated endpoints.
	•	Implementation Guidance:
	•	Use FastAPI to build the RESTful API.
	•	Provide proper endpoint documentation using FastAPI’s auto-generated OpenAPI docs.
	•	Ensure robust error handling and clear JSON responses.
	•	Key Endpoint Examples:

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse

app = FastAPI()

@app.post("/process_image/")
async def process_image(file: UploadFile = File(...), tts: bool = False):
    file_path = save_uploaded_file(file)
    try:
        caption = generate_caption(file_path)
        narrative = generate_narrative(caption)
        response = {"caption": caption, "narrative": narrative}
        if tts:
            audio_filename = f"audio_{uuid.uuid4()}.mp3"
            audio_path = os.path.join("data", audio_filename)
            text_to_speech(narrative, audio_path)
            response["audio_file"] = audio_filename
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{audio_filename}")
def get_audio(audio_filename: str):
    audio_path = os.path.join("data", audio_filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(audio_path, media_type="audio/mpeg")

6. Data Flow & Interaction
	1.	Client Interaction:
	•	The client (web/mobile app or API consumer) sends an HTTP POST request with an image file (and optional TTS flag) to /process_image/.
	2.	File Storage:
	•	The API saves the file locally or to a cloud storage bucket with a unique ID.
	3.	Processing Pipeline:
	•	The image captioning module reads the stored file, processes it, and returns a caption.
	•	The narrative generation module receives the caption, formats a prompt, and calls the LLM API to generate a narrative.
	•	If TTS is requested, the TTS module converts the narrative into an audio file.
	4.	Response:
	•	The API aggregates the caption, narrative, and (if applicable) audio file reference, then returns a JSON response.
	5.	Audio Retrieval:
	•	Clients can request the audio file via /audio/{audio_filename}.

7. External Dependencies & Integrations
	•	Hugging Face Transformers:
For the image captioning model.
	•	OpenAI API:
For narrative generation. Requires secure API key management.
	•	TTS Engine:
gTTS (or AWS Polly) for audio synthesis.
	•	Cloud Storage (Optional):
AWS S3, GCP Cloud Storage, or similar for storing images/audio if not using local storage.
	•	CI/CD & Logging Tools:
GitHub Actions, CloudWatch (AWS), or equivalent for deployment and monitoring.

8. Deployment Architecture & Environment
	•	Containerization:
Package the application using Docker.
Sample Dockerfile:

FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


	•	Cloud Deployment:
	•	AWS: Deploy on AWS Fargate, Lambda (via API Gateway), or Elastic Beanstalk.
	•	GCP: Deploy using Cloud Run or App Engine.
	•	Scaling:
Ensure that the API layer and processing modules can scale horizontally based on load. Use auto-scaling features of your chosen cloud provider.
	•	Environment Management:
Use environment variables (managed via a .env file or cloud secrets manager) to store API keys, file paths, and other configurations.

9. Security, Error Handling, and Logging
	•	Security:
	•	Validate file types and sizes at upload.
	•	Sanitize user inputs and prompt parameters.
	•	Secure API endpoints with authentication if necessary (e.g., API keys or OAuth).
	•	Use HTTPS for all communications.
	•	Error Handling:
	•	Implement try/except blocks around external API calls (LLM, TTS).
	•	Return clear HTTP status codes (e.g., 400 for bad requests, 500 for server errors).
	•	Provide descriptive error messages in JSON responses.
	•	Logging:
	•	Log all incoming requests, processing steps, and errors.
	•	Integrate with centralized logging (e.g., AWS CloudWatch, ELK stack) for production monitoring.
	•	Ensure logs do not leak sensitive information.

10. Testing Strategy
	•	Unit Testing:
	•	Write tests for individual modules (e.g., file storage, caption generation, narrative generation).
	•	Use mocking for external API calls (e.g., OpenAI and TTS service).
	•	Integration Testing:
	•	Test the complete workflow by simulating end-to-end API calls.
	•	Performance Testing:
	•	Use load testing tools (e.g., Locust, JMeter) to validate response times under load.
	•	User Acceptance Testing (UAT):
	•	Perform tests with representative sample images to ensure that the narrative quality and audio generation meet requirements.

11. CI/CD & Deployment Pipeline
	•	CI/CD Pipeline:
	•	Use GitHub Actions (or similar) to run automated tests on each commit.
	•	Linting (using Black or Flake8) and static code analysis.
	•	Automated Docker builds and deployment to the chosen cloud environment upon merge to the main branch.
	•	Deployment Automation:
	•	Use infrastructure-as-code tools (e.g., AWS CloudFormation, Terraform) to manage cloud resources.
	•	Ensure rollback mechanisms are in place in case of deployment failures.

12. Environment Configuration & Variables
	•	Essential Environment Variables:
	•	OPENAI_API_KEY: API key for accessing the OpenAI API.
	•	STORAGE_PATH: Path for file storage (if not using defaults).
	•	TTS_SERVICE: Selector for which TTS engine to use (e.g., gTTS or AWS_POLLY).
	•	LOG_LEVEL: Configure log verbosity.
	•	Configuration Management:
	•	Use a .env file during development.
	•	In production, use a secrets manager (AWS Secrets Manager, GCP Secret Manager) to securely store credentials.

13. Appendices

Appendix A: Sample API Endpoints
	•	POST /process_image/
Request: Multipart form data including file (image) and optional tts flag.
Response:

{
  "caption": "A scenic view of a mountain lake.",
  "narrative": "The calm lake reflects the towering mountains, evoking a sense of peace and adventure...",
  "audio_file": "audio_123e4567-e89b-12d3-a456-426614174000.mp3" // if TTS enabled
}


	•	GET /audio/{audio_filename}
Response: Returns the requested audio file with content-type audio/mpeg or a 404 if not found.

Appendix B: Known Limitations and Future Enhancements
	•	Limitations:
	•	Response times may be affected by external API latencies (LLM/TTS).
	•	Local storage may need to be replaced with scalable cloud storage for high-volume use.
	•	Enhancements:
	•	Integrate caching for repeated image uploads.
	•	Implement user authentication and rate limiting.
	•	Expand multi-language support for captioning and narrative generation.

Summary

This document outlines the full technical and architectural blueprint for the Visual Storyteller project. By following this guidance, the implementation team will have a clear understanding of each component, their interactions, and the overall system design. This ensures that the final product is robust, scalable, and maintainable while meeting all functional and non-functional requirements.

End of Document