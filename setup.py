from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="glyphwork",
    version="0.1.0",
    author="muraleph",
    author_email="muraleph@muraleph.art",
    description="Generative ASCII art through code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muraleph/glyphwork",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    keywords="ascii art generative text unicode terminal",
)
