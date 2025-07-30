#!/usr/bin/env python3
"""
Setup script for Church Equipment Inventory System
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="church-inventory-tracker",
    version="1.0.0",
    author="Church Inventory System Team",
    author_email="contact@churchinventory.com",
    description="A comprehensive Flask-based web application for managing church technical equipment inventory",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/church-inventory-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Religion",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Topic :: Office/Business",
        "Topic :: Religion",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-flask>=1.2.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "church-inventory=app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="church, inventory, equipment, flask, web-application",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/church-inventory-tracker/issues",
        "Source": "https://github.com/yourusername/church-inventory-tracker",
        "Documentation": "https://github.com/yourusername/church-inventory-tracker#readme",
    },
) 