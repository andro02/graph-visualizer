from setuptools import setup, find_packages

setup(
    name="data_source_csv",
    version="0.1.0",
    author="KVT",
    description="Data source plugin koji parsira CSV fajlove i konstruiše graf model",
    packages=find_packages(),
    install_requires=[
        "api>=0.1.0",
    ],
    python_requires=">=3.8",
)
