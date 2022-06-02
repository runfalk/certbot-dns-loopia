from setuptools import setup


try:
    long_desc = open("README.md").read()
except FileNotFoundError:
    print("Skipping README.md for long description as it was not found")
    long_desc = None


setup(
    name="certbot-dns-loopia",
    version="1.0.1",
    description="Loopia DNS authentication plugin for Certbot",
    long_description=long_desc,
    long_description_content_type="text/x-rst",
    license="BSD",
    author="Andreas Runfalk",
    author_email="andreas@runfalk.se",
    url="https://www.github.com/runfalk/certbot-loopia",
    py_modules=["certbot_dns_loopia"],
    install_requires=[
        "acme>=1.8.0",
        "certbot>=1.7.0",
        "loopialib>=0.2.0",
        "tldextract>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "wheel",
            "pylint==2.13.9",
        ],
    },
    entry_points={
        "certbot.plugins": [
            "dns-loopia = certbot_dns_loopia:LoopiaAuthenticator",
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
