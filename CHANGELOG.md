# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.8rc0] - 2020-10-27

### Added

- Will now catch and handle `requests.exceptions.ConnectionError`.

## [1.1.7] - 2020-10-21

### Added

- Added `recv_window` error handler to `HTTP` `auth` method.
- Will now catch and handle `requests.exceptions.SSLError`.

## [1.1.6] - 2020-10-09

### Modified

- Added `recv_window` argument to `HTTP` class.

## [1.1.5] - 2020-09-30

### Modified

- Improved error handling.
- Added `max_retries` argument to `HTTP` class.

## [1.1.4] - 2020-09-17

### Modified

- Added `FailedRequestError` to differentiate between failed requests and
  invalid requests.
- Fixed `exit` method on `WebSocket` to now properly handle the closing of the socket.

## [1.1.3] - 2020-09-12

### Modified

- Increased expires time for WebSocket authentication to a full second.

## [1.1.2] - 2020-09-12

### Modified

- Add option to handle timeout on request submission.

## [1.1.1] - 2020-09-11

### Modified

- Fixed trailing decimal zero to prevent auth signature errors.

## [1.1.0] - 2020-09-08

### Added

- New `HTTP` methods.
- New argument for `HTTP` class to log each outgoing request.
- New argument for `WebSocket` class to attempt restart after an error is
  detected.

### Modified

- Mass simplification of all methods—each method now takes a series keyword
  arguments rather than a set number of required pre-defined arguments. This
  makes the library future-proof and prevents breaking on significant updates 
  to the REST API endpoints. This, however, requires the user to study the
  API documentation and know which arguments are required for each endpoint. 
- One new exception has been added—`InvalidRequestError`. This exception will be
  raised if Bybit returns with an error, or if `requests` is unable to complete
  the request.
- Inverse and Linear endpoints are now handled accordingly by differentiating
  from the symbol argument.
- Updated existing `HTTP` method names to follow the same naming procedure as 
  listed in the Bybit API documentation.
- Reformatting of code to follow PEP-8 standards.
- New docstring format.


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
