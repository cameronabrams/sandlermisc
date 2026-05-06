# Changelog

All notable changes to sandlermisc will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.2] - 2026-02-04

### Changed

- `StateReporter` and `ThermodynamicState` refinements.

## [0.4.1] - 2026-02-03

### Added

- Pint incorporation; full smart-resolution of `ThermodynamicState`.

## [0.4.0] - 2026-02-03

### Added

- `ThermodynamicState` abstract class for handling thermodynamic states of pure components.
- `constants.py` with universal gas constant `R` as a pint `Quantity`.

### Changed

- Reorganized public API in `__init__.py`.

## [0.3.2] - 2026-01-10

### Fixed

- `unpackCp` now correctly handles `np.ndarray` inputs.

## [0.3.1] - 2026-01-06

### Fixed

- `unpackCp` now correctly handles `int` inputs.

## [0.3.0] - 2025-12-31

### Added

- `StateReporter` class for formatted thermodynamic state output.

## [0.1.0] - 2025-12-30

- Initial release.