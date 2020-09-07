import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pid-plotter-godzilla-but-nicer",
    version="0.0.1",
    author="Pat Wall",
    author_email="patgwall@iu.edu",
    description="plot a pid",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/godzilla-but-nicer/pid_plotter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)