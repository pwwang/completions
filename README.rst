
completions
===========

`
.. image:: https://img.shields.io/pypi/v/completions.svg?style=flat-square
   :target: https://img.shields.io/pypi/v/completions.svg?style=flat-square
   :alt: pypi
 <https://pypi.org/project/completions/>`_ `
.. image:: https://img.shields.io/github/tag/pwwang/completions.svg?style=flat-square
   :target: https://img.shields.io/github/tag/pwwang/completions.svg?style=flat-square
   :alt: tag
 <https://github.com/pwwang/completions>`_ `
.. image:: https://img.shields.io/travis/pwwang/completions.svg?style=flat-square
   :target: https://img.shields.io/travis/pwwang/completions.svg?style=flat-square
   :alt: travis
 <https://travis-ci.org/pwwang/completions>`_ `
.. image:: https://img.shields.io/codacy/grade/98c8035ccd4c4f97b454086271a1b1c1.svg?style=flat-square
   :target: https://img.shields.io/codacy/grade/98c8035ccd4c4f97b454086271a1b1c1.svg?style=flat-square
   :alt: codacy quality
 <https://app.codacy.com/project/pwwang/completions/dashboard>`_ 
.. image:: https://img.shields.io/pypi/pyversions/completions.svg?style=flat-square
   :target: https://img.shields.io/pypi/pyversions/completions.svg?style=flat-square
   :alt: pyver


Shell completions for your program made easy.

Installation
------------

.. code-block:: shell

   pip install completions
   # install lastest version using poetry
   git clone https://github.com/pwwang/completions
   cd completions
   poetry install

Usage
-----

Defining your completions
^^^^^^^^^^^^^^^^^^^^^^^^^

You may define your completions, basically commands and options, by following schema (showed in ``yaml``\ , but can be any format supported by `\ ``python-simpleconf`` <https://github.com/pwwang/simpleconf>`_\ :
``example.yaml``

.. code-block:: yaml

   program:
       # your program, or path to your program
       name: completions-example
       desc: Shell completions for your program made easy.
       # whether global options should be inherited by commands
       inherit: true
       # options or global options if you have commands
       options:
           -s: The shell, one of bash, fish, zsh and auto.
           --shell: The shell, one of bash, fish, zsh and auto.
           -a: Automatically write completions to destination file.
           --auto: Automatically write completions to destination file.
   commands:
       # No other options for command, give the description
       self: Generate completions for myself.
       generate:
           desc: Generate completions from configuration files.
           options:
               -c: The configuration file to load.
               --config: The configuration file to load.

How it looks like in ``fish``\ :

.. image:: https://raw.githubusercontent.com/pwwang/completions/master/examples/command.png
   :target: https://raw.githubusercontent.com/pwwang/completions/master/examples/command.png
   :alt: command


.. image:: https://raw.githubusercontent.com/pwwang/completions/master/examples/option.png
   :target: https://raw.githubusercontent.com/pwwang/completions/master/examples/option.png
   :alt: option


Generating completion scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Bash
  .. code-block:: shell

       > completions generate --shell bash \
           --config example.yaml > ~/bash_completion.d/completions.bash-completion
    You may need to ``source`` it in your ``.bashrc`` and restart your shell for the changes to take effect.
* Fish
  .. code-block:: shell

       > completions generate --shell fish \
           --config example.yaml > ~/.config/fish/completions/completions.fish
    You may need to restart your shell for the changes to take effect.
* Zsh
  .. code-block:: shell

       > completions generate --shell zsh \
           --config example.yaml > ~/.zsh-completions/_completions
    Make sure ``fpath+=~/.zsh-completions`` is put before ``compinit`` in you ``.zshrc``

Saving completions scripts automatically
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* 
  Bash

  .. code-block:: shell

       > completions generate --shell bash --config example.yaml --auto

* 
  Fish

  .. code-block:: shell

       > completions generate --shell fish --config example.yaml --auto

* 
  Zsh

  .. code-block:: shell

       > completions generate --shell zsh --config example.yaml --auto

Python API
^^^^^^^^^^

.. code-block:: python

   from completions import Completions
   completions = Completions(
       # if not given, will be read from sys.argv[0]
       name    = 'completions',
       # Add global options to commands
       inherit = True,
       desc    = 'Shell completions for your program made easy.')
   completions.addOption(
       ['-s', '--shell'],
       'The shell, one of bash, fish, zsh and auto.')
   completions.addOption(
       ['-a', '--auto'],
       'Automatically write completions to destination file.')
   completions.addCommand(
       'self', 'Generate completions for myself.')
   completions.addCommand(
       'generate', 'Generate completions from configuration files.')
   completions.command('generate').addOption(
       ['-c', '--config'], 'The configuration file to load.')
   completions.generate(shell = 'fish', auto = False)
