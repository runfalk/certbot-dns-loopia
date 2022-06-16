# Developing certbot-dns-loopia


These examples uses a Debian 11 "bullseye".

# Setup
```shell
git clone https://github.com/runfalk/certbot-dns-loopia
cd certbot-dns-loopia

# create and activate a virtualenv
python3 -m venv venv
. venv/bin/activate

# install in editable mode and include dev dependencies
pip install -e .[dev]
```

# Test
Before you commit any code you should preferably run...
```shell
make lint
make test
```

## Live Testing
If you have a domain to play around with there is a way of running a live test.
You must create the `credentials.ini` file in the project root with the correct credentials.
```shell
# set some variables that are used
export EMAIL=<your email address>
export TESTDOMAIN=<yourdomain.com>


# run the live tests that will be using your email and test.sub.$TESTDOMAIN
make livetest
```



# Publish
## Build
```shell
# install tools
pip install build twine

# build to check that everything is fine
python -m build

# optionally verify contents
cd dist/
unzip certbot_dns_loopia-1.0.0-py3-none-any.whl -d certbot_dns_loopia-whl
tree certbot_dns_loopia-whl
# Should output somehting like this
certbot_dns_loopia-whl/
├── certbot_dns_loopia-1.0.0.dist-info
│   ├── LICENSE
│   ├── METADATA
│   ├── RECORD
│   ├── WHEEL
│   ├── entry_points.txt
│   └── top_level.txt
└── dns_loopia.py

# remove unzipped folder
rm -Rf  certbot_dns_loopia-whl
```

## Check and test
```shell
# check dist files
twine check dist/*


# upload to testpypi, this will require maintainer access
twine upload -r testpypi dist/*

# upload to production pypi, this will also require maintainer access
twine upload dist/*

```
