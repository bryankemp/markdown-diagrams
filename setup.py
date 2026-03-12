from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ursula",
    version="0.1.0",
    author="Bryan Kemp",
    author_email="bryan@kempville.com",
    description="A tool for extracting and rendering Mermaid diagrams from Markdown files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bryankemp/ursula",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "ursula=src.main:cli",
        ],
    },
)
