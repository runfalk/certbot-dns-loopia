from setuptools import setup


try:
    long_desc = open("README.rst").read()
except:
    print("Skipping README.rst for long description as it was not found")
    long_desc = None

setup(
    name="certbot-loopia",
    version="0.2.0",
    description="Loopia DNS authentication plugin for Certbot",
    long_description=long_desc,
    license="BSD",
    author="Andreas Runfalk",
    author_email="andreas@runfalk.se",
    url="https://www.github.com/runfalk/certbot-loopia",
    py_modules=["certbot_loopia"],
    install_requires=[
        "acme>=0.17.0",
        "certbot>=0.17.0",
        "loopialib>=0.2.0",
        "zope.interface>=4.4.0",
    ],
    entry_points={
        "certbot.plugins": [
            "auth = certbot_loopia:LoopiaAuthenticator",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
