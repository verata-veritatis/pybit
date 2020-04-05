# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2020-04-05

### Added

- Various logging features added to both HTTP and WebSocket classes.

### Modified

- Extensive WebSocket class updates.
  - Modified the WebSocketApp to send a heartbeat packet every 30 seconds,
    with a timeout of 10 seconds. These settings can be modified using the
    'ping_interval' and 'ping_timeout' arguments of the WebSocket
    constructor.
  - User no longer needs to manage the incoming stream; `pybit` does all the
  work (insert, update, delete).
  - Modified `ws.ping()` for ease of use; simply use the function to send
  heartbeat packets. When something happens to the connection, Python will
  raise an `Exception` which the end-user can catch and handle.
- Redundancy updates to the HTTP class.
- Modified the HTTP class to use an endpoint argument, allowing users to
  take advantage of the USDT endpoints.

## [1.0.1] - 2020-04-03

### Modified

- The setup.py file has been fixed to correctly install the pybit package.

## [1.0.0] - 2020-04-03

### Added

- The `pybit` module.
- MANIFEST, README, LICENSE, and CHANGELOG files.
