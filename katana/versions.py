"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
import re

from .errors import KatanaError

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

# Regexp to remove duplicated '*' in versions
DUPLICATES = re.compile(r'(\*)\1+')


class VersionParser(object):
    """Parser for version strings.

    Parser is used to compare version string against a pattern.

    """

    def __init__(self, value):
        # Keep original version value without change
        self.__value = value
        # Use initial value as initial suffix
        self.__suffix = value
        self.parse_next()

    def __str__(self):
        return self.value

    def __repr__(self):
        return 'Version: {}'.format(self.value)

    @property
    def value(self):
        return self.__value

    @property
    def part(self):
        return self.__part

    @property
    def suffix(self):
        return self.__suffix

    @property
    def suffix_len(self):
        return self.__suffix_len

    @property
    def current_value(self):
        return '{}.{}'.format(self.part, self.suffix)

    def parse_next(self):
        self.__part, *extra = self.__suffix.split('.', 1)
        self.__suffix = extra[0] if extra else None
        self.__suffix_len = len(self.__suffix) if self.__suffix else 0
        return self


class VersionPattern(object):
    """Version pattern class.

    Patterns are used to find highest version strings.

    A pattern can contain any number of '*' which are subtituted
    by the highest version part. For example, given versions '1.2',
    '1.2-alpha1' '2.0', a pattern '1.*' would match '1.2-alpha1'.

    """

    def __init__(self, pattern):
        # Remove duplicated special chars from pattern
        pattern = DUPLICATES.sub(r'\1', pattern)

        self.__value = pattern
        self.__part = None
        self.__suffix_len = 0

        self.static = '*' not in pattern
        if not self.static:
            self.__suffix = pattern
            self.parse_next()
            self.latest_version = (pattern == '*')
        else:
            self.__suffix = None
            self.latest_version = False

    @property
    def value(self):
        return self.__value

    @property
    def part(self):
        return self.__part

    @property
    def suffix(self):
        return self.__suffix

    @property
    def suffix_len(self):
        return self.__suffix_len

    @property
    def highest(self):
        return self.part == '*'

    def parse_next(self):
        self.__part, *extra = self.__suffix.split('.', 1)
        self.__suffix = extra[0] if extra else None
        self.__suffix_len = len(self.__suffix) if self.__suffix else 0
        return self


def sort_versions(versions):
    """Sort a list of versions.

    :param versions: A list of version strings.
    :type versions: list

    :returns: A new list of version strings.
    :rtype: list

    """

    version_parts = sorted(version.split('.') for version in versions)
    return ['.'.join(part) for part in version_parts]


class VersionNotFound(KatanaError):
    """Exception raised when a version is not found."""

    message = 'Service version not found for pattern: "{}"'

    def __init__(self, pattern):
        super().__init__(message=self.message.format(pattern))
        self.pattern = pattern


def find_version(pattern, versions):
    """Find the highest version for a version pattern.

    Versions must be given as `VersionParser` objects instead of
    plain strings.

    :param pattern: A version pattern.
    :type pattern: VersionPattern
    :param versions: A list of VersionParser objects.
    :type versions: list

    :raises: VersionNotFound

    :returns: A version string.
    :rtype: str

    """

    if pattern.static:
        return pattern.value
    elif pattern.latest_version:
        # Patter value is '*' which means latest version is used
        return versions[-1].value
    elif not versions:
        # When a pattern has no versions to compare then there is no match
        raise VersionNotFound(pattern.value)

    # Get version for current pattern
    current_version = None
    if pattern.highest:
        # Iterate versions in reverse order from greater to lower
        for version in versions[::-1]:
            if pattern.suffix_len == version.suffix_len:
                # Get highest version that matches pattern length
                current_version = version
                break
    else:
        # Get version that matches current pattern part value
        for version in versions:
            if pattern.suffix_len != version.suffix_len:
                # Skip versions that are shorter than pattern
                continue
            elif pattern.part == version.part:
                # Current version part matches pattern part value
                current_version = version
                break

    if not current_version:
        raise VersionNotFound(pattern.value)

    if not pattern.suffix:
        # Return current version part when pattern has no suffix
        return current_version.part
    elif '*' not in pattern.suffix:
        # No more wildcards available in suffix. Return current version
        # part value as prefix and use the rest of the pattern as suffix.
        return '{}.{}'.format(current_version.part, pattern.suffix)

    # Filter versions by current version prefix
    prefix = '{}.'.format(current_version.part)
    prefix_len = len(prefix)
    # Remove versions that don't start with current version prefix
    versions = [
        version.parse_next()
        for version in versions
        if version.suffix and version.current_value[:prefix_len] == prefix
        ]

    # Keep parsing when version pattern suffix contains wildcards.
    # Current version part value will be used as prefix.
    return prefix + find_version(pattern.parse_next(), versions)
