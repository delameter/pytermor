.. _install:

#####################
Installation
#####################

Python 3.8 or later should be installed and available in ``$PATH``; that's
basically it if intended usage of the package is as a library.

---------------------------
Installing into a project
---------------------------

For injecting the library into an existing project. No extra dependencies
required.

.. code-block:: console

   $ python -m pip install pytermor

If approximation time is essential, there is an option to install few extra
dependencies (``numpy`` and ``scipy``), which allows to perform the approximation
about 10x times faster (`details <guide.approximators>`):

.. code-block:: console

   $ python -m pip install 'pytermor[fast]'

.. _install.demo:

---------------------------
Demo installation
---------------------------

Downloading source code for running some predefined examples (see `Examples —
Demo <examples.demo>`).

.. code-block:: console

   $ git clone git@github.com:delameter/pytermor.git
   $ cd pytermor
   $ ./run-cli examples/tone_neighbours.py
   Virtual environment is not present
   Initialize it in '/home/pt/venv-demo'? (y/n): y
   [...]

----------------------------------------
Development installation
----------------------------------------

For library development (editable mode).

.. code-block:: console

   $ git clone git@github.com:delameter/pytermor.git --branch dev
   $ cd pytermor
   $ python -m venv venv
   $ ./venv/bin/python -m pip install -e .
   $ ./venv/bin/python -m pytermor
   2.110.0.dev0
   2023-11-24 20:58:30+03:00
