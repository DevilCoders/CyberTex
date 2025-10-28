from sapl.stdlib.extended import EXTRA_FUNCTIONS


def test_regex_findall_and_search():
    regex_findall = EXTRA_FUNCTIONS["regex_findall"]
    regex_search = EXTRA_FUNCTIONS["regex_search"]
    payload = "user=analyst id=42 user=guest id=10"
    matches = regex_findall(r"user=(\w+)", payload)
    assert matches == ["analyst", "guest"]
    search = regex_search(r"user=(?P<name>\w+)", payload)
    assert search["groupdict"]["name"] == "analyst"
    assert search["span"][0] == 0


def test_regex_flags_and_replace():
    regex_match = EXTRA_FUNCTIONS["regex_match"]
    regex_replace = EXTRA_FUNCTIONS["regex_replace"]
    text = "Host=EXAMPLE" \
        "\nHost=demo"
    match = regex_match(r"host=(\w+)", text, flags=["ignorecase"])
    assert match["groups"][0].lower() == "example"
    replaced = regex_replace(r"host=(\w+)", "host=[REDACTED]", text, flags="i")
    assert "[REDACTED]" in replaced
