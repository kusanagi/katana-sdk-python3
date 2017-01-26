from katana.versions import VersionString

GREATER = 1
EQUAL = 0
LOWER = -1


def test_simple_version_match():
    """
    Check versions matches for a fixed version string.

    """

    # Create a version string without wildcards
    version_string = VersionString('1.2.3')
    # Versions match
    assert version_string.match('1.2.3')
    # Versions don't match
    assert not version_string.match('A.B.C')


def test_wildcards_version_match():
    """
    Check versions matches for a version pattern with wildcards.

    """

    # Create a version with wildcards
    version_string = VersionString('1.*.*')

    # Version formats match
    for version in ('1.2.3', '1.4.3', '1.2.3-alpha'):
        assert version_string.match(version)

    # Version formats don't match
    for version in ('A.B.C', '2.2.3', '1.2.3.alpha'):
        assert not version_string.match(version)


def test_compare_none():
    """
    Check none comparison results.

    """

    compare_none = VersionString.compare_none

    assert compare_none(None, None) == EQUAL
    assert compare_none('A', None) == LOWER


def test_compare_sub_part():
    """
    Check comparison results for version string sub parts.

    """

    compare_sub_parts = VersionString.compare_sub_parts

    # Parts are equal
    assert compare_sub_parts('A', 'A') == EQUAL

    # First part is greater than second one
    assert compare_sub_parts('B', 'A') == LOWER
    assert compare_sub_parts('2', '1') == LOWER
    # First part is lower than second one
    assert compare_sub_parts('A', 'B') == GREATER
    assert compare_sub_parts('1', '2') == GREATER

    # Integer parts are always lower than string parts ...

    # First part is greater than second one
    assert compare_sub_parts('A', '1') == LOWER
    # First part is lower than second one
    assert compare_sub_parts('1', 'A') == GREATER


def test_compare_versions():
    """
    Check comparisons between different versions.

    """

    cases = (
        ('A.B.C', GREATER, 'A.B'),
        ('A.B-beta', GREATER, 'A.B'),
        ('A.B-beta', GREATER, 'A.B-alpha'),
        ('A.B.C', EQUAL, 'A.B.C'),
        ('A.B-alpha', EQUAL, 'A.B-alpha'),
        ('A.B', LOWER, 'A.B.C'),
        ('A.B', LOWER, 'A.B-alpha'),
        ('A.B-beta', LOWER, 'A.B-gamma'),
        )

    compare = VersionString.compare

    for ver2, expected, ver1 in cases:
        assert compare(ver1, ver2) == expected


def test_resolve_versions():
    """
    Check version pattern resolution.

    """

    # Format: pattern, expected, versions
    cases = (
        ('3.4.1', '3.4.1', ('3.4.0', '3.4.1', '3.4.a')),
        ('3.4.*', '3.4.0', ('3.4.0', '3.4.1', '3.4.a')),
        ('3.4.*', '3.4.0', ('3.4.a', '3.4.1', '3.4.0')),
        ('3.4.*', '3.4.alpha', ('3.4.alpha', '3.4.beta', '3.4.gamma')),
        ('3.4.*', '3.4.a', ('3.4.alpha', '3.4.a', '3.4.gamma')),
        ('3.4.*', '3.4.1', ('3.4.a', '3.4.12', '3.4.1')),
        ('3.4.*', '3.4.0', ('3.4.0', '3.4.0-a', '3.4.0-0')),
        ('3.4.*', '3.4.0-0', ('3.4.0-0', '3.4.0-a', '3.4.0-1')),
        ('3.4.*', '3.4.0-0', ('3.4.0-0', '3.4.0-1-0', '3.4.0-1')),
        )

    for pattern, expected, versions in cases:
        version_string = VersionString(pattern)

        # Compare pattern against all versions
        for version in versions:
            assert version_string.resolve(versions) == expected
