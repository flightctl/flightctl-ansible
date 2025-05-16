==================================
flightctl collection Release Notes
==================================

.. contents:: Topics

v1.0.0
======

Release Summary
---------------

Added support for Flight Control API v0.7.1.

Minor Changes
-------------

- Updated the Ansible collection to support Flight Control API version 0.7.1.
- Version bump for Automation Hub publishing

v0.7.0
======

Release Summary
---------------

Added support for Flight Control API v0.7.

Major Changes
-------------

- Added Flight Control console connection plugin
- Added support for dynamic inventory plugin
- Added support for new features in Flight Control API v0.7.
- Updated the Ansible collection to support Flight Control API version 0.7.

Bugfixes
--------

- auth documentation - fixed env var names to align with module usage

New Plugins
-----------

Connection
~~~~~~~~~~

- flightctl_console - Connect to Flight Control managed devices.

Inventory
~~~~~~~~~

- flightctl - Returns Ansible inventory using Flight Control as source.

v0.6.0
======

Release Summary
---------------

Added support for Flight Control API v0.6.

Major Changes
-------------

- Updated the Ansible collection to support Flight Control API version 0.6.

v0.5.0
======

Release Summary
---------------

Added support for Flight Control API v0.5.

Major Changes
-------------

- Added support for Device decommissioning.
- Updated the Ansible collection to support Flight Control API version 0.5.

v0.2.0
======

Release Summary
---------------

This release contains the initial documented release of the Flightctl collection

Breaking Changes / Porting Guide
--------------------------------

- Renamed `flightctl_certificate_management` module (previously `flightctl_certificate`)
- Renamed `flightctl_resource_info` module (previously `flightctl_info`)
- Renamed `flightctl_resource` module (previously `flightctl`)
- Renamed collection to `core` (previously `edge`)
