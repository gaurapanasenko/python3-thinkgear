from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text()

setup(
    name="thinkgear-py3",
    version="2.3",
    packages=find_packages(),
    author="Yehor Panasenko",
    author_email="gaura.panasenko@gmail.com",
    description="ThinkGear Serial Stream Protocol implementation",
    url="https://github.com/gaurapanasenko/python3-thinkgear",
    install_requires=[],
    long_description=long_description,
    long_description_content_type="text/x-rst",
)
