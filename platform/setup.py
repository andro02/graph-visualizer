from setuptools import setup, find_packages

setup(
    name="platform",
    version="0.1.0",
    author="KVT",
    description="Platforma za upravljanje grafovima i komunikaciju između pluginova",
    packages=find_packages(),
    install_requires=[
        "api>=0.1.0",
    ],
    python_requires=">=3.8",
)
