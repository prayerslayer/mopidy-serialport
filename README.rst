****************************
Mopidy-SerialPort
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-SerialPort.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-SerialPort/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-SerialPort.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-SerialPort/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/prayerslayer/mopidy-serialport/master.svg?style=flat
    :target: https://travis-ci.org/prayerslayer/mopidy-serialport
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/prayerslayer/mopidy-serialport/master.svg?style=flat
   :target: https://coveralls.io/r/prayerslayer/mopidy-serialport
   :alt: Test coverage

Mopidy extension for control via serial messages


Installation
============

Install by running::

    pip install Mopidy-SerialPort

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-SerialPort to your Mopidy configuration file::

    [serialport]
    # TODO: Add example of extension config

Signals
=======

- ``V+``: Volume up 1 step, but not more than ``max_volume``
- ``V-``: Volume down 1 step, but not less than ``min_volume``
- ``Cn``: Set channel to ``n`` (``n`` is a number >= 0)
- ``P1``: Pause playback
- ``P0``: Resume playback


Project resources
=================

- `Source code <https://github.com/prayerslayer/mopidy-serialport>`_
- `Issue tracker <https://github.com/prayerslayer/mopidy-serialport/issues>`_


Changelog
=========

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
