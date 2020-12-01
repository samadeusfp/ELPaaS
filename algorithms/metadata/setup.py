import setuptools

import p_privacy_metadata

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name=p_privacy_metadata.__name__,
    version=p_privacy_metadata.__version__,
    author=p_privacy_metadata.__author__,
    author_email=p_privacy_metadata.__author_email__,
    description="Privacy metadata in process mining",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m4jidRafiei/privacy_metadata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
    ],
    project_urls={
        'Source': 'https://github.com/m4jidRafiei/privacy_metadata'
    }
)