"""WealthMind - AI-Powered Personal Finance Platform.

Setup configuration for package installation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="wealthmind",
    version="0.1.0",
    author="WealthMind Team",
    author_email="hello@wealthmind.ai",
    description="AI-Powered Personal Finance Platform with subscription-based revenue model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/22boikanyo10-rgb/SOFTWARE-ENGINEER",
    project_urls={
        "Bug Tracker": "https://github.com/22boikanyo10-rgb/SOFTWARE-ENGINEER/issues",
        "Documentation": "https://wealthmind.readthedocs.io",
        "Source Code": "https://github.com/22boikanyo10-rgb/SOFTWARE-ENGINEER",
    },
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "stripe>=7.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.2.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "isort>=5.13.0",
            "mypy>=1.7.0",
            "pylint>=3.0.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
    ],
    keywords="finance personal-finance budgeting ai subscription saas",
    entry_points={
        "console_scripts": [
            "wealthmind=wealthmind.cli:main",
        ],
    },
)
