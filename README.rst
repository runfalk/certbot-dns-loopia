Loopia DNS Authenticator for Certbot
====================================
This allows automatic completion of `Certbot's
<https://github.com/certbot/certbot>` DNS01 challange for domains managed on
`Loopia <https://www.loopia.se/>` DNS.


Installing
----------
.. code-block::
   $ pip install certbot-loopia


Usage
-----
To use the authenticator you need to provide some required options.

``--certbot-loopia:auth-user <user>`` *(required)*
  API username for Loopia.
``--certbot-loopia:auth-password <password>`` *(required)*
  API password for Loopia.

There are also some optional arguments:

``--certbot-loopia:auth-time-limit <time>``
  Time limit for local verification. This is the maximum time the authenticator
  will try to self-verify before declaring that the DNS update was unsuccessful.
  Default: ``30m``.
``--certbot-loopia:auth-time-delay <time>``
  Time delay before first trying to self-verify the result of authentication.
  It is recommended to have a delay of at least 30 seconds to prevent the DNS
  server from caching that there are no TXT records for the challenge subdomain.
  Default: ``1m``.
``--certbot-loopia:auth-retry-interval <time>``
  How frequently to retry self-verification. This is time past since the start
  of the previous verification. It is not recommended to choose values smaller
  than 10 seconds. Default: ``30s``.

The format of ``<time>`` is ``AdBhCmDs`` where: ``A``is days, ``B``is hours,
``C``is minutes and ``D`` is seconds. Note that ``A``, ``B``, ``C`` and ``D``
must be integers. The units ``d``, ``h`` and ``m`` are required while ``s`` is
optional. Any value-unit pair may be omitted, but they must be ordered from most
to least significant unit. Examples of valid ``<time>`` expressions are:

- ``42`` or ``42s`` for 42 seconds
- ``1m30s`` or ``1m30`` for 1.5 minutes
- ``1h`` for 1 hour
- ``1d12h`` for 1.5 days


Known issues
------------
- Due to caching on Loopia's side it can take up to 15 minutes before changes
  are visible. The plugin will by default retry self-verification for at least
  30 minutes before sending the actual verification request to the ACME server.

Disclaimer
----------
This plugin is neither affiliated with nor endorsed by Loopia AB.
