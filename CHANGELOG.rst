==================================
flightctl collection Release Notes
==================================

.. contents:: Topics

v1.7.0
======

Release Summary
---------------

Added support for Flight Control API v1.3.

Major Changes
-------------

- Updated the Ansible collection to support Flight Control API version 1.3.

Minor Changes
-------------

- Added the ``deployments`` option to ``flightctl_resource_info`` for querying the device and fleet deployments of a named ``CatalogItem``.
- Added the ``flightctl_application`` module to start, stop, and restart applications on Devices and Fleets.
- Updated collection requirements to install ``flightctl-client==1.3.0`` from PyPI instead of the client repository's ``main`` branch.

Bugfixes
--------

- Added a pydantic ``ValidationError`` fallback to the shared API module (``module_utils/api_module.py``) so that ``get()`` and ``list()`` retry against the client SDK's raw JSON endpoints instead of crashing. This fixes unhandled tracebacks in ``flightctl_resource_info`` and other modules when the API returns mount-only application volumes without the required ``image`` field, matching the fix previously applied to the inventory plugin. The pydantic-detection helper is now shared via ``module_utils/sdk_utils.py``.
- Replaced broken HTTP Basic Auth with an OIDC Resource Owner Password Grant flow in the shared API module (``module_utils/api_module.py``) and the image builder module (``module_utils/imagebuilder_module.py``). Modules such as ``flightctl_resource``, ``flightctl_resource_info``, ``flightctl_certificate_management``, ``flightctl_enrollment_config_info`` and the image builder modules now authenticate with a Bearer token when given ``username``/``password``, fixing authentication against Flight Control servers that only accept OIDC. This matches the fix previously applied to the inventory plugin. The OIDC discovery and password-grant logic is now shared via ``module_utils/oidc_auth.py``.

New Modules
-----------

- flightctl_application - Start, stop, or restart Flight Control applications.

v1.6.1
======

Release Summary
---------------

Bug fix release addressing inventory plugin crashes and authentication issues.

Bugfixes
--------

- Added a pydantic ``ValidationError`` fallback in the inventory plugin that retries device list calls using raw JSON endpoints, fixing crashes when the API returns mount-only application volumes without the required ``image`` field.
- Added missing ``env`` declarations to all inventory plugin connection options so that environment variables (``FLIGHTCTL_TOKEN``, ``FLIGHTCTL_HOST``, etc.) are no longer silently ignored by ``get_option()``, restoring AAP Credential Type injection support.
- Deferred ``jsonschema`` and ``pyyaml`` import checks in ``ConfigLoader`` to ``_load_config_file()`` so that the inventory plugin no longer raises ``ImportError`` when these packages are absent and no config file is used.
- Replaced broken HTTP Basic Auth with an OIDC Resource Owner Password Grant flow in the inventory plugin, matching the ``flightctl`` CLI behavior and fixing authentication against RHEM servers that only accept Bearer tokens.

v1.6.0
======

Release Summary
---------------

Added support for Flight Control API v1.2.

Major Changes
-------------

- Updated the Ansible collection to support Flight Control API version 1.2.

v1.5.0
======

Release Summary
---------------

Added Image Builder modules, v1alpha1 API support, and new resource types for Flight Control API v1.1.

Major Changes
-------------

- Added ``flightctl_image_builder`` and ``flightctl_image_builder_info`` modules.
- Added support for AuthProvider, Catalog, CatalogItem, Event, Organization, and EnrollmentConfig resource types.
- Added v1alpha1 API support for Catalog and CatalogItem resources.
- Updated the Ansible collection to support Flight Control API version 1.1.

New Modules
-----------

- flightctl_image_builder - Manage Flight Control Image Builder resources.
- flightctl_image_builder_info - Get information about Flight Control Image Builder resources.

v1.4.0
======

Release Summary
---------------

Added support for Flight Control API v1.0.

Major Changes
-------------

- Added support for new features in Flight Control API v1.0.
- Updated the Ansible collection to support Flight Control API version 1.0.

v1.3.0
======

Release Summary
---------------

Added support for Flight Control API v0.10.0 and improved the FlightCtl inventory plugin robustness.

Minor Changes
-------------

- Added `hostnames` option for selecting the device field (dot path) as the inventory hostname.
- Added support for Basic auth (username/password) in the inventory plugin for environments with proxies that accept HTTP Basic.
- Improved documentation and examples for `flightctl_config_file` (FlightCtl config) and config precedence.
- Inventory plugin now supports `group_by` option for grouping devices by a field value.
- Updated the Ansible collection to support Flight Control API version 0.10.0.

Bugfixes
--------

- Inventory plugin now sends Authorization headers explicitly for list operations, resolving authentication failures when the client library does not auto-attach tokens.
- Remove noisy warning when no configuration file is provided; plugin proceeds quietly without a config file.
- Treat `host` as a string (not a path) to prevent URLs from being coerced into file paths, fixing "No host specified" errors.

v1.2.0
======

Release Summary
---------------

Added support for Flight Control API v0.9.0.

Minor Changes
-------------

- Updated the Ansible collection to support Flight Control API version 0.9.0.
- Version bump for Automation Hub publishing

v1.1.0
======

Release Summary
---------------

Added support for Flight Control API v0.8.0.

Minor Changes
-------------

- Updated the Ansible collection to support Flight Control API version 0.8.0.
- Version bump for Automation Hub publishing

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
