from setuptools import setup, find_packages

setup(
    name="ipl-telegram-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "telethon==1.37.0",
        "pymongo==4.6.1",
        "python-dotenv==1.0.0",
        "kagglehub==0.2.5",
        "pandas==2.0.3",
        "scikit-learn==1.2.2",
        "nltk==3.8.1",
        "transformers==4.30.2",
        "torch==2.0.1",
        "fasttext-wheel==0.9.2",
        "indic-nlp-library==0.91",
        "spacy==3.6.1",
        "gunicorn==21.2.0",
    ],
    python_requires=">=3.9,<3.12",
)
