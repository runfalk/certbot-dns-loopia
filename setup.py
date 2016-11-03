from setuptools import setup

setup(
    name="certbot-loopia",
    py_modules=["certbot_loopia"],
    install_requires=[
        "certbot",
        "loopialib",
        "zope.interface",
    ],
    entry_points={
        "certbot.plugins": [
            "auth = certbot_loopia:LoopiaAuthenticator",
        ],
    },
)
