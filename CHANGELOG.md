# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- Added support to run a component server and handle a single request
  where the payload is send from the CLI in a JSON file (#72).

### Changed
- Logging was changed to use byte strings without encoding them first.

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
- Initial release
