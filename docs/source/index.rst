===================================
libtado - Control your tado devices
===================================

libtado is a simple Python library that provides methods to control the smart
heating devices from the German company `tado GmbH`_. It uses the undocumented
REST API of their website.

The library is in NO way connected to tado GmbH and is not officially
supported by them!

The source code is hosted on GitHub_. Feel free to report issues or open
pull requests.


.. toctree::
   :maxdepth: 2
   :titlesonly:
   :caption: Getting started

   installation
   usage

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :caption: Class methods

   api-usage
   api-methods
   api-examples

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :caption: Command Line Client

   cli-usage
   cli-examples


Installation
************

.. code-block:: bash

  pip install libtado


Usage
*****

After you installed libtado you can easily test it by using the included

.. code-block:: bash

   tado --username USERNAME --password PASSWORD whoami

To use the library in your own code you can start with this:

.. code-block:: python

  import tado.api
  t = tado.api('Username', 'Password')
  print(t.get_me())

Check out `all available API methods <api>` to learn what you can to with
libtado.


License
*******


  Copyright (C) 2020  Germain Lefebvre, Max Rosin

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.


References
**********

.. target-notes::
.. _`tado GmbH`: https://www.tado.com
.. _GitHub: https://github.com/germainlefebvre4/libtado
