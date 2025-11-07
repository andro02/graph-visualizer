from setuptools import setup, find_packages

setup(
    name="block_visualizer",
    version="0.1.0",
    author="andro02",
    description="Napredni block-style vizualizer grafa sa dodatnim opcijama prikaza",
    packages=find_packages(),
    install_requires=[
        "api>=0.1.0",
    ],
    python_requires=">=3.8",
)
