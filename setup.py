from setuptools import setup, find_packages

setup(
    name="visual_storyteller",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "Pillow>=9.0.0",
        "python-dotenv>=0.19.0",
        "gtts>=2.3.0",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-playwright>=0.4.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.910",
        ]
    },
) 