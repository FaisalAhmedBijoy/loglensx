"""Setup configuration for LogLens."""

from setuptools import setup, find_packages

setup(
    name="loglens",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "plotly>=5.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "fastapi": ["fastapi>=0.68.0", "uvicorn[standard]>=0.15.0"],
        "flask": ["flask>=2.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "loglens-info=loglens.cli:main",
        ],
    },
    author="LogLens Contributors",
    author_email="support@loglens.dev",
    description="Interactive log viewer with charts and visualizations for FastAPI and Flask",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/loglens",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/loglens/issues",
        "Documentation": "https://loglens.readthedocs.io",
        "Source Code": "https://github.com/yourusername/loglens",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: System :: Logging",
        "Topic :: Utilities",
    ],
)
