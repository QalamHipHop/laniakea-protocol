"""
LaniakeA Protocol - Setup Configuration
Author: LaniakeA Dev
Copyright © 2025 LaniakeA Dev. All Rights Reserved.
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="laniakea-protocol",
    version="3.0.0",
    packages=find_packages(exclude=["tests", "tests.*", "archived_old_patterns"]),
    install_requires=required,
    author="LaniakeA Dev",
    author_email="dev@laniakea-protocol.org",
    maintainer="LaniakeA Dev Team",
    description=(
        "LaniakeA Protocol: The Cosmic Evolution Engine — "
        "an 8-dimensional blockchain superprotocol for collective intelligence, "
        "SCDA evolution, knowledge markets, and metaverse diplomacy."
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/QalamHipHop/laniakea-protocol",
    project_urls={
        "Documentation": "https://github.com/QalamHipHop/laniakea-protocol/blob/main/README.md",
        "Source": "https://github.com/QalamHipHop/laniakea-protocol",
        "Live": "https://laniakea-protocol.onrender.com",
        "Bug Reports": "https://github.com/QalamHipHop/laniakea-protocol/issues",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Blockchain :: Cryptocurrencies",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    keywords="blockchain web3 metaverse ai scda evolution 8d-hypercube",
    entry_points={
        "console_scripts": [
            "laniakea=laniakea.cli.commands:main",
        ],
    },
)
