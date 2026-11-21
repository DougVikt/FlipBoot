"""Setup script for FlipBoot."""
from setuptools import setup, find_packages

setup(
    name="flipboot",
    version="0.1.0-alpha",
    description="Cross-platform, cross-OS boot switcher for UEFI and Legacy BIOS",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="Lord_Doug",
    python_requires=">=3.8",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "flipboot=flipboot.main:main",
        ],
    },
)