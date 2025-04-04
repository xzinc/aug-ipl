from setuptools import setup, find_packages

setup(
    name="ipl-telegram-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "telethon==1.37.0",
        "pymongo==4.6.1",
        "python-dotenv==1.0.0",
        "gunicorn==21.2.0",
        "kagglehub==0.2.5",
        "flask==2.0.1",
        "werkzeug==2.0.3",
        "google-generativeai==0.3.1",
    ],
    python_requires=">=3.9,<3.12",
)
