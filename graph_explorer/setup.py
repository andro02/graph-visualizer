from setuptools import setup, find_packages

setup(
    name="graph_explorer",
    version="0.1.0",
    author="graph_visualizer",
    description="Django aplikacija za vizualizaciju i upravljanje grafovima koristeći platform i pluginove",
    packages=find_packages(),
    install_requires=[
        "platform>=0.1.0",
        "data_source_csv>=0.1.0",
        "data_source_json>=0.1.0",
        "simple_visualizer>=0.1.0",
        "block_visualizer>=0.1.0",
    ],
    python_requires=">=3.8",
)
