![Test](https://github.com/runfalk/certbot-dns-loopia/actions/workflows/test.yml/badge.svg)

# Loopia DNS Authenticator for Certbot


This allows automatic completion of
[Certbot's](https://github.com/certbot/certbot) DNS01 challenge for
domains managed on [Loopia](https://www.loopia.se/) DNS by leveraging
the [Loopia XML-RPC API](https://www.loopia.se/api/).

## Installing

```shell
$ sudo pip install certbot-dns-loopia
```

Note that you should normally install this as `root`, unless you know
what you are doing.

## Preconditions

### Loopia API user 

The plugin requires a Loopia API user with the following permissions:

- `addZoneRecord`
- `getZoneRecords`
- `removeSubdomain`
- `removeZoneRecord`

### Credentials file

An INI file with `user` and `password` for your Loopia API user needs to be created. `user`
normally has the format `user@loopiaapi`.

The credentials file must have the following format:

```INI
dns_loopia_user = user@loopiaapi
dns_loopia_password = passwordgoeshere
```

For safety reasons the file must not be world readable. You can solve
this by running:

```shell
$ chmod 600 credentials.ini
```


## Usage

### Parameters

When using `certbot` with `certbot-dns-loopia`, aside from the usual parameters accepted by `certbot`, the following
parameters may be used:

| Parameter                                    | Required?           | Default | Description                                                                                                      |
|----------------------------------------------|---------------------|---------|------------------------------------------------------------------------------------------------------------------|
| `--dns-loopia-credentials <path>`            | :heavy_check_mark:️ | -       | The path of the INI file containing your Loopia API user credentials                                             |
| `--dns-loopia-propagation-seconds <seconds>` |                     | 900     | Determines how many seconds to wait before contacting the ACME server after adding the zone record to Loopia DNS |

### Examples

To obtain a certificate for `domain.com`, run `certbot` using:

```shell
$ sudo certbot certonly \
    --authenticator dns-loopia \
    --dns-loopia-credentials credentials.ini \
    -d domain.com
```

To obtain a wildcard certificate for all subdomains of `domain.com`:

```shell
$ sudo certbot certonly \
    --authenticator dns-loopia \
    --dns-loopia-credentials credentials.ini \
    -d *.domain.com
```

To obtain a certificate valid for multiple domains using [SAN](https://en.wikipedia.org/wiki/Subject_Alternative_Name),
in this example for `foo.com` and `bar.com`:
```shell
$ sudo certbot certonly \
    --authenticator dns-loopia \
    --dns-loopia-credentials credentials.ini \
    -d foo.com \
    -d bar.com
```

## Known issues

- Due to caching on Loopia's side it can take up to 15 minutes before
  changes propagate. Therefore, the plugin will wait 15 minutes before
  contacting the ACME server.

  It has been known to work with as little as 90 seconds and sometimes
  less. If you want to try something other than 15 minutes, use
  `--dns-loopia-propagation-seconds 90` for 90 seconds
  or however many seconds you want.

Contributing
------------

How to set up a dev environment, test and publish new versions of the
project is described on the [DEVELOP page](DEVELOP.md).

Disclaimer
----------

This plugin is neither affiliated with nor endorsed by Loopia AB.
