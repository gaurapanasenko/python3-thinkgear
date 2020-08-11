from setuptools import setup, find_packages

setup(
    name="thinkgear-py3",
    version="0.2",
    packages=find_packages(),
    author="Yehor Panasenko",
    author_email="gaura.panasenko@gmail.com",
    description="ThinkGear Serial Stream Protocol implementation",
    url="https://github.com/gaurapanasenko/python3-thinkgear",
    install_requires=["pybluez"],
)
