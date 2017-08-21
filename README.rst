Loopia DNS Authenticator for Certbot
====================================
This allows automatic completion of `Certbot's <https://github.com/certbot/certbot>`_
DNS01 challange for domains managed on `Loopia <https://www.loopia.se/>`_ DNS.


Installing
----------
.. code-block::

   $ pip install certbot-loopia


Usage
-----
To use the authenticator you need to provide some required options:

``--certbot-loopia:credentials`` *(required)*
  INI file with ``user`` and ``password`` for your Loopia API user. ``user``
  normally has the format ``user@loopiaapi``.

The credential file must have the folling format:

.. code-block::

   certbot_loopia:auth_user = user@loopiaapi
   certbot_loopia:auth_password = passwordgoeshere

For safety reasons the file must not be world readable. You can solve this by
running:

.. code-block::

   $ chmod 600 credentials.ini


Known issues
------------
- Due to caching on Loopia's side it can take up to 15 minutes before changes
  propagates. Therefore the plugin will wait 15 minutes before contacting the
  ACME server.


Changelog
---------

Version 0.2.0
~~~~~~~~~~~~~
Released 21st August 2017

- Rewrote plugin to match the implementation of ``certbot-dns-*`` plugins
- Updated dependency requirements since the old release was completely broken
  for newer ``acme`` and ``certbot``
  (see `issue #2 <https://github.com/runfalk/certbot-loopia/issues/2>`_)


Version 0.1.0
~~~~~~~~~~~~~
Released 10th May 2017

- Initial release


Disclaimer
----------
This plugin is neither affiliated with nor endorsed by Loopia AB.
