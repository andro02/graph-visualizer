from setuptools import setup, find_packages

setup(
    name="data_source_json",
    version="0.1.0",
    author="andro02",
    description="Data source plugin koji učitava JSON strukture i formira graf model",
    packages=find_packages(),
    install_requires=[
        "api>=0.1.0",
    ],
    python_requires=">=3.8",
)
