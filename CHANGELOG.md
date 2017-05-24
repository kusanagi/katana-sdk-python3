# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.0.7] - Unreleased

## [1.0.6] - 2017-05-24
### Added
- Added "binary" type support for parameters and return value.

## [1.0.5] - 2017-05-09
### Added
- Added getter for origin duration to transport.

## [1.0.4] - 2017-05-04
### Added
- Added support to get service return value in response middlewares.

## [1.0.3] - 2017-04-27
### Added
- Added support to run a component server and handle a single request
  where the payload is send from the CLI in a JSON file (#72).

### Changed
- Logging was changed to use byte strings without encoding them first.
- `HttpActionSchema.get_method()` now returns method names in lower case.

### Fixed
- Engine variables now works with request and response middlewares.

## [1.0.2] - 2017-03-28
### Added
- Version wildcards support for single '*' to match all.

### Changed
- The wildcard ('*') in the last version part now matches any character.

## [1.0.1] - 2017-03-07
### Added
- Transport merge support for run-time calls.

### Changed
- Updated payload argument names for "action" and "callee" to be consistent
  between transactions and calls in API `Action` class.

## [1.0.0] - 2017-03-01
- Initial release.
