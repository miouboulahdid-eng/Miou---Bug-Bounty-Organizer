from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="bugbounty-organizer",
    version="1.0.0",
    author="Miou",
    author_email="miou@bugbounty.com",
    description="Real-time dashboard for organizing bug bounty recon outputs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/miou/bugbounty-organizer",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "Miou = cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)