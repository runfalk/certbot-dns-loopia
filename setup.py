"""
Setup for certbot-dns-loopia.
"""
# pylint: disable=consider-using-with
from setuptools import setup, find_packages

try:
    LONG_DESC = open("README.md", encoding="utf-8").read()
except FileNotFoundError:
    print("Skipping README.md for long description as it was not found")
    LONG_DESC = None


setup(
    name="certbot-dns-loopia",
    version="1.0.1",
    description="Loopia DNS authentication plugin for Certbot",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    license="BSD",
    author="Andreas Runfalk",
    author_email="andreas@runfalk.se",
    url="https://www.github.com/runfalk/certbot-loopia",
    packages=find_packages(),
    install_requires=[
        "acme>=1.8.0",
        "certbot>=1.7.0",
        "tldextract>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "wheel",
            "pylint==2.13.9",
            "mypy==0.961",
        ],
    },
    entry_points={
        "certbot.plugins": [
            "dns-loopia = certbot_dns_loopia._internal.dns_loopia:Authenticator",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
