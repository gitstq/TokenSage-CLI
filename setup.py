import os
from setuptools import setup, find_packages

setup(
    name="tokensage-cli",
    version="0.1.0",
    description="Lightweight Terminal AI Token Compression & Cost Optimization Engine",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="TokenSage Team",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    package_dir={"": "."},
    entry_points={
        "console_scripts": [
            "tokensage=tokensage.cli:main",
        ],
    },
    extras_require={
        "rich": ["rich>=13.0.0"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Text Processing",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
)
