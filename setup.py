import os
from setuptools import setup


version = '1.0.1'
cb_required = '1.8.0'

install_requires = [
    'loopialib>=0.2.0',
    'zope.interface>=4.4.0',
]


if not os.environ.get('SNAP_BUILD'):
    install_requires.extend([
        f'acme>={cb_required}',
        f'certbot>={cb_required}',
    ])


if os.environ.get('SNAP_BUILD'):
    install_requires.append('packaging')


BASE_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(BASE_PATH, 'README.rst')) as f:
    long_desc = f.read()



setup(
    name="certbot-dns-loopia",
    version=version,
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
        'certbot.plugins': [
            'dns-loopia = certbot_dns_loopia:LoopiaAuthenticator',
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
