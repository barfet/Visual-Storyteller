from setuptools import setup, find_packages

setup(
    name="visual_storyteller",
    version="0.1.0",
    packages=find_packages(),
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
) 