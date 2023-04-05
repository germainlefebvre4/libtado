.. _usage:

=======================
Usage
=======================

After you installed libtado you can easily test it by using the included
:ref:`command line client <cli>` like this:

.. code-block:: bash

   tado --username USERNAME --password PASSWORD whoami

To use the library in your own code you can start with this:

.. code-block:: python

  import tado.api
  t = tado.api('Username', 'Password')
  print(t.get_me())

Check out :ref:`all available API methods <api>` to learn what you can to with
libtado.