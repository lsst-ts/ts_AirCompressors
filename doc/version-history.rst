.. _Version_History:

===============
Version History
===============

v1.5.7
------

* Fixed conda build

v1.5.6
------

* fixes for new asyncio.TransportSocket, freezed pymodbus to 3.7.2 version

v1.5.5
------

* fixes for pymodbus>=3.6

v1.5.4
------

* fixes for pymodbus>=3.5

v1.5.3
------

* fixes for pymodbus>=3.4

v1.5.2
------

* remove reuse_addr completely

v1.5.1
------

* fix simulator - trivial Modbus TCP/IP server issue

v1.5.0
------

* timers (remaining service hours) are signed integers
* renamed to ts_mtaircompressor

v1.4.2
------

* Pinned pymodbus in conda recipe.

v1.4.1
------

* Adjusted to new pymodbus version, that dropped async versionn of the close call.

v1.4.0
------

* Fixed standby handling. Compressor connection was not reconnected after standby transition.

v1.3.3
------

* Don't call close_tasks on begin_standby - caused HB loss on standby

v1.3.2
------

* Pin pymodbus to version >= 3.

v1.3.1
------

* Fixed timeout handling.

v1.3.0
------

* Initial state is STANDBY.

v1.2.0
------

* Transition to pymodbus 3.
* Improved error handling - disconnected compressor.

v1.1.0
------

* Upgrade build to pyproject.toml.
* Adds errors & warnings events.

v1.0.2
------

* Updates for python 7.

v1.0.1
------

* Add pymodbus dependency to conda recipe.

v1.0.0
------

* Initial version of the MTAirCompressor CSC.
