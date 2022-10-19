import pytest

from komposer.envsubst import envsubst


@pytest.mark.parametrize(
    "value, template, expected",
    [
        pytest.param("test_val", "foo $FOO bar", "foo test_val bar", id="simple"),
        pytest.param("test_val", "foo ${FOO} bar", "foo test_val bar", id="bracketed"),
    ],
)
def test_envsubst(
    monkeypatch: pytest.MonkeyPatch, value: str, template: str, expected: str
) -> None:
    """
    GIVEN a value
        AND a template
    WHEN envsubst is called
    THEN the expected result is returned
    """
    # GIVEN
    monkeypatch.setenv("FOO", value)

    # WHEN
    actual = envsubst(template)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "value, template, expected",
    [
        pytest.param("", "foo ${FOO-i am a default} bar", "foo  bar"),
        pytest.param("", "foo ${FOO:-i am a default} bar", "foo i am a default bar"),
        pytest.param("I am a value", "foo ${FOO-i am a default} bar", "foo I am a value bar"),
        pytest.param("I am a value", "foo ${FOO:-i am a default} bar", "foo I am a value bar"),
    ],
)
def test_envsubst_default(
    monkeypatch: pytest.MonkeyPatch, value: str, template: str, expected: str
) -> None:
    """
    GIVEN a value
        AND a template
        AND a default
    WHEN envsubst is called
    THEN the expected result is returned
    """
    # GIVEN
    monkeypatch.setenv("FOO", value)

    # WHEN
    actual = envsubst(template)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "template, expected",
    [
        pytest.param("foo ${FOO-I am a default} bar", "foo I am a default bar"),
        pytest.param("foo ${FOO:-I am a default} bar", "foo I am a default bar"),
    ],
)
def test_envsubst_default_unset_env_var(
    monkeypatch: pytest.MonkeyPatch, template: str, expected: str
) -> None:
    """
    GIVEN a template
        AND the env var is unset
    WHEN envsubst is called
    THEN the default is returned
    """
    # GIVEN
    monkeypatch.delenv("FOO", raising=False)

    # WHEN
    actual = envsubst(template)

    # THEN
    assert actual == expected


def test_multiple(monkeypatch: pytest.MonkeyPatch) -> None:
    foo_val = "i am FOO value"
    bar_val = "i am BAR value"
    bar2_val = "i am BAR2 value"

    monkeypatch.setenv("FOO", foo_val)
    monkeypatch.setenv("BAR", bar_val)
    monkeypatch.setenv("BAR2", bar2_val)
    monkeypatch.delenv("NOPE", raising=False)

    nope_default = "var NOPE not there"

    test_fmt = "abc {0} def {1}{2} jkl {3} mno"
    test_str = test_fmt.format(
        "$FOO",
        "${BAR}",
        "${BAR2:-default for bar2}",
        "${NOPE-" + nope_default + "}",
    )

    actual = envsubst(test_str)

    expected = test_fmt.format(foo_val, bar_val, bar2_val, nope_default)

    assert actual == expected


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(r"i am an \$ESCAPED variable"),
        pytest.param(r"i am an \${ESCAPED:-bracketed} \${expression}"),
    ],
)
def test_escaped(value: str) -> None:
    assert value == envsubst(value)


def test_simple_var_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # GIVEN
    default_val = "test default val"

    monkeypatch.setenv("DEFAULT", default_val)
    monkeypatch.setenv("TEST", "")

    test_fmt = "abc {0} def"
    test_str = test_fmt.format("${TEST:-$DEFAULT}")

    # WHEN
    actual = envsubst(test_str)

    # THEN
    expected = test_fmt.format(default_val)

    assert actual == expected
