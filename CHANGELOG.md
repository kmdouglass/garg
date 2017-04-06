# Change Log
All notable changes to this project will be documented in this file.

## [v0.1.0] - 2017-04-06
### Added
- Added a field to `Garg` called `ignore_positional_only`. When set to
  True, no errors will be raised when the function given to parsed by
  Garg contains parameters of the type POSITIONAL_ONLY.

### Changed
- The `Garg` field `ignore_errors` is now called
  `ignore_syntax_errors`. This reflects the fact that it ignores only
  errors that are raised when an argument is not syntactically-correct
  Python.
	
## v0.0.0
### Added
- Main program functionality.

[v0.1.0]: https://github.com/kmdouglass/garg/compare/v0.0.0...HEAD
