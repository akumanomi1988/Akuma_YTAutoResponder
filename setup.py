from setuptools import setup, find_packages

setup(
    name="yt-autoresponder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'google-api-python-client>=2.0.0',
        'google-auth-oauthlib>=1.0.0',
        'g4f>=0.1.0',
        'python-dotenv>=0.19.0'
    ],
    author="Akuma No Mi Dev",
    author_email="Akumanomi1988@gmail.com",
    description="AI-powered YouTube Comment Auto-Responder",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Akuma_YTAutoResponder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)