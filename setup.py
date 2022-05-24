from setuptools import setup


try:
    long_desc = open("README.rst").read()
except FileNotFoundError:
    print("Skipping README.rst for long description as it was not found")
    long_desc = None


setup(
    name="certbot-dns-loopia",
    version="1.0.0",
    description="Loopia DNS authentication plugin for Certbot",
    long_description=long_desc,
    license="BSD",
    author="Andreas Runfalk",
    author_email="andreas@runfalk.se",
    url="https://www.github.com/runfalk/certbot-loopia",
    py_modules=["certbot_dns_loopia"],
    install_requires=[
        "acme>=1.8.0",
        "certbot>=1.7.0",
        "loopialib>=0.2.0",
        "zope.interface>=4.4.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "wheel",
            "pylint>=2.13.9",
        ],
    },
    entry_points={
        "certbot.plugins": [
            "dns-loopia = certbot_dns_loopia:LoopiaAuthenticator",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
