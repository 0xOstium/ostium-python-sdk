from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent

# Read requirements.txt


def read_requirements(filename: str):
    return [line.strip()
            for line in (this_directory / filename).read_text().splitlines()
            if line.strip() and not line.startswith('#')]


# Read the contents of README.md and CHANGELOG.md
long_description = (this_directory / "README.md").read_text()

# Try to append CHANGELOG.md if it exists
changelog_path = this_directory / "CHANGELOG.md"
if changelog_path.exists():
    long_description += "\n\n" + changelog_path.read_text()

setup(
    name="ostium-python-sdk",
    version="3.0.1",
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        "dev": read_requirements('requirements-dev.txt'),
    },
    package_data={
        '': ['requirements.txt', 'requirements-dev.txt']
    },
    python_requires=">=3.8",

    author="ami@ostium.io",
    description="A python based SDK developed for interacting with Ostium, a leveraged trading application for trading currencies, commodities, indices, crypto and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0xOstium/ostium-python-sdk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
