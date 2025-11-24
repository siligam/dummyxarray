"""Setup configuration for dummyxarray package."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="dummyxarray",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A lightweight xarray-like object for building dataset metadata specifications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dummyxarray",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/dummyxarray/issues",
        "Documentation": "https://yourusername.github.io/dummyxarray/",
        "Source Code": "https://github.com/yourusername/dummyxarray",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20.0",
        "xarray>=0.19.0",
        "pyyaml>=5.4.0",
        "zarr>=2.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=24.0.0",
            "isort>=5.13.0",
            "flake8>=7.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings>=0.24.0",
            "mkdocstrings-python>=1.7.0",
        ],
    },
    keywords="xarray metadata netcdf zarr climate data",
)
