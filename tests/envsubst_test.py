import pytest

from komposer.envsubst import envsubst


@pytest.mark.parametrize(
    "value, template",
    [
        pytest.param("test_val", "foo $FOO bar", id="simple"),
        pytest.param("test_val", "foo ${FOO} bar", id="bracketed"),
    ],
)
def test_envsubst_skip_non_komposer(
    monkeypatch: pytest.MonkeyPatch, value: str, template: str
) -> None:
    """
    GIVEN a value
        AND a template
            AND the template doesn't include Komposer vars
    WHEN envsubst is called
    THEN the expected result is returned
    """
    # GIVEN
    monkeypatch.setenv("FOO", value)

    # WHEN
    actual = envsubst(template)

    # THEN
    assert actual == template


@pytest.mark.parametrize(
    "value, template, expected",
    [
        pytest.param("test_val", "foo $KOMPOSER_FOO bar", "foo test_val bar", id="simple"),
        pytest.param("test_val", "foo ${KOMPOSER_FOO} bar", "foo test_val bar", id="bracketed"),
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
    monkeypatch.setenv("KOMPOSER_FOO", value)

    # WHEN
    actual = envsubst(template)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "value, template, expected",
    [
        pytest.param("", "foo ${KOMPOSER_FOO-a default} bar", "foo  bar"),
        pytest.param("", "foo ${KOMPOSER_FOO:-a default} bar", "foo a default bar"),
        pytest.param("value", "foo ${KOMPOSER_FOO-a default} bar", "foo value bar"),
        pytest.param("value", "foo ${KOMPOSER_FOO:-a default} bar", "foo value bar"),
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
    monkeypatch.setenv("KOMPOSER_FOO", value)

    # WHEN
    actual = envsubst(template)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "template, expected",
    [
        pytest.param("foo ${KOMPOSER_FOO-I am a default} bar", "foo I am a default bar"),
        pytest.param("foo ${KOMPOSER_FOO:-I am a default} bar", "foo I am a default bar"),
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


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(r"i am an \$KOMPOSER_ESCAPED variable"),
        pytest.param(r"i am an \${KOMPOSER_ESCAPED:-bracketed} \${expression}"),
    ],
)
def test_escaped(value: str) -> None:
    assert value == envsubst(value)


def test_simple_var_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # GIVEN
    default_val = "test default val"

    monkeypatch.setenv("KOMPOSER_DEFAULT", default_val)
    monkeypatch.setenv("KOMPOSER_TEST", "")

    test_fmt = "abc {0} def"
    test_str = test_fmt.format("${KOMPOSER_TEST:-$KOMPOSER_DEFAULT}")

    # WHEN
    actual = envsubst(test_str)

    # THEN
    expected = test_fmt.format(default_val)

    assert actual == expected
