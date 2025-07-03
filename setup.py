from setuptools import setup, find_packages

setup(
    name="universal_tts_system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'pyttsx3==2.90',
        'PyPDF2==3.0.1',
        'ebooklib==0.18',
        'beautifulsoup4==4.12.2',
        'pydub==0.25.1',
        'numpy==1.24.3',
        'pytest==7.4.0',
        'pytest-asyncio==0.21.1',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A universal text-to-speech system supporting multiple file formats",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/universal_tts_system",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
) 