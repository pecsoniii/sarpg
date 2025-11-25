from setuptools import setup, find_packages

setup(
    name="neon_drifter",
    version="1.0.0",
    description="A Neon Twin-Stick Roguelite",
    author="Jules",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.0"
    ],
    entry_points={
        "console_scripts": [
            "neon_drifter=src.main:main",
        ],
    },
)
