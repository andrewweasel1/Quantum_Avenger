from setuptools import find_packages, setup

setup(
    name="quantum_avenger",
    version="0.1.0",
    packages=find_packages(include=["new_pipeline", "new_pipeline.*"]),
    install_requires=[
        "pydantic>=2.0",
        "pyyaml>=6.0",
        "numpy>=1.25",
    ],
    python_requires=">=3.11",
)
