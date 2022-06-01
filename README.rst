.. image:: https://github.com/runfalk/certbot-dns-loopia/actions/workflows/test.yml/badge.svg
  :alt: Test

Loopia DNS Authenticator for Certbot
====================================
This allows automatic completion of `Certbot's <https://github.com/certbot/certbot>`_
DNS01 challenge for domains managed on `Loopia <https://www.loopia.se/>`_ DNS.


Installing
----------
.. code-block::

   $ sudo pip install certbot-dns-loopia

Note that you should normally install this as ``root``, unless you know what
you are doing.

Preconditions
-------------
The plugin requires the following permissions enabled for your Loopia API user:

- ``addZoneRecord``
- ``getZoneRecords``
- ``removeSubdomain``
- ``removeZoneRecord``

To use the authenticator you need to provide some required options:

``--dns-loopia-credentials`` *(required)*
  INI file with ``user`` and ``password`` for your Loopia API user. ``user``
  normally has the format ``user@loopiaapi``.

The credentials file must have the following format:

.. code-block::

   dns_loopia_user = user@loopiaapi
   dns_loopia_password = passwordgoeshere

For safety reasons the file must not be world readable. You can solve this by
running:

.. code-block::

   $ chmod 600 credentials.ini

Usage
-----



To obtain a certificate for ``domain.com``, run ``certbot`` using:

.. code-block::

    $ sudo certbot certonly \
        --authenticator dns-loopia \
        --dns-loopia-credentials credentials.ini \
        -d domain.com

To obtain a wildcart certificate:
If you want to obtain a wildcard certificate you can use the domain

.. code-block::

    $ sudo certbot certonly \
        --authenticator dns-loopia \
        --dns-loopia-credentials credentials.ini \
        -d *.domain.com

You can also obtain a certificate for multiple domains (using
`SAN <https://en.wikipedia.org/wiki/Subject_Alternative_Name>`_) by doing
``-d one.domain.com -d two.domain.com`` etc.

Known issues
------------
- Due to caching on Loopia's side it can take up to 15 minutes before changes
  propagate. Therefore, the plugin will wait 15 minutes before contacting the
  ACME server.

  It has been known to work with as little as 90 seconds and sometimes less.
  If you want to try something other than 15 minutes, add
  ``--dns-loopia-propagation-seconds 90`` to parameters for 90 seconds or
  however many seconds you want.

Contributing
------------
How to set up a dev environment, test and publish new versions of the project is
described on the `DEVELOP page <DEVELOP.md>`_.


Disclaimer
----------
This plugin is neither affiliated with nor endorsed by Loopia AB.
