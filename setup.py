"""Setup configuration for loglensx."""

from setuptools import setup, find_packages

setup(
    name="loglensx",
    version="1.0.2",
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
            "loglensx=loglensx.cli:main",
        ],
    },
    author="loglensx Contributors",
    author_email="faisal.cse16.kuet@gmail.com",
    description="Interactive log viewer with charts and visualizations for FastAPI and Flask",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/faisalahmedbijoy/loglensx",
    project_urls={
        "Bug Tracker": "https://github.com/faisalahmedbijoy/loglensx/issues",
        "Documentation": "https://loglensx.readthedocs.io",
        "Source Code": "https://github.com/faisalahmedbijoy/loglensx",
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
