Loopia DNS Authenticator for Certbot
====================================
This allows automatic completion of `Certbot's <https://github.com/certbot/certbot>`_
DNS01 challange for domains managed on `Loopia <https://www.loopia.se/>`_ DNS.


Installing
----------
.. code-block::

   $ sudo pip install certbot-dns-loopia

Note that you should normally install this as ``root``, unless you know what
you are doing.

Usage
-----
The plugin requires the following permissions enabled for your Loopia API user:

- addZoneRecord
- getZoneRecords
- removeSubdomain
- removeZoneRecord

To use the authenticator you need to provide some required options:

``--dns-loopia-credentials`` *(required)*
  INI file with ``user`` and ``password`` for your Loopia API user. ``user``
  normally has the format ``user@loopiaapi``.

The credentials file must have the folling format:

.. code-block::

   dns_loopia_user = user@loopiaapi
   dns_loopia_password = passwordgoeshere

For safety reasons the file must not be world readable. You can solve this by
running:

.. code-block::

   $ chmod 600 credentials.ini

Then you can run ``certbot`` using:

.. code-block::

    $ sudo certbot certonly \
        --authenticator dns-loopia \
        --dns-loopia-credentials credentials.ini \
        -d domain.com

If you want to obtain a wildcard certificate you can use the domain
``-d *.domain.com``.


Known issues
------------
- Due to caching on Loopia's side it can take up to 15 minutes before changes
  propagates. Therefore the plugin will wait 15 minutes before contacting the
  ACME server.
  It has been known to work with as little as 90 seconds and sometimes less
  and if you want to try something other than 15 minutes then add
  ``--dns-loopia-propagation-seconds 90`` to parameters for 90 seconds or
  how many seconds you want.


Changelog
---------
Version 1.0.0
~~~~~~~~~~~~~
Released 4th May 2021

**This is a breaking change. The CLI arguments and the name of the package has
changed to match other DNS authenticator plugins.**

Thank you Peter Magnusson (`@kmpm <https://github.com/kmpm>`_) for contributing
this change!

- Updated name to `certbot-dns-loopia` to match other DNS plugins
- Dropped Python < 3.6 support


Version 0.2.0
~~~~~~~~~~~~~
Released 21st August 2017

- Rewrote plugin to match the implementation of ``certbot-dns-*`` plugins
- Updated dependency requirements since the old release was completely broken
  for newer ``acme`` and ``certbot``
  (see `issue #2 <https://github.com/runfalk/certbot-dns-loopia/issues/2>`_)


Version 0.1.0
~~~~~~~~~~~~~
Released 10th May 2017

- Initial release


Disclaimer
----------
This plugin is neither affiliated with nor endorsed by Loopia AB.
