from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="laniakea-protocol",
    version="3.0.0",
    packages=find_packages(),
    install_requires=required,
    author="QalamHipHop",
    description="A comprehensive protocol for a decentralized, intelligent, and multi-dimensional metaverse.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/QalamHipHop/laniakea-protocol",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
