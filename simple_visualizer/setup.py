from setuptools import setup, find_packages

setup(
    name="simple_visualizer",
    version="0.1.0",
    author="KVT",
    description="Jednostavan vizualizer grafa zasnovan na D3.js force-layoutu",
    packages=find_packages(),
    install_requires=[
        "api>=0.1.0",
    ],
    python_requires=">=3.8",
)
