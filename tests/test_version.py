import resource_fula_ordboken


def test_version() -> None:
    assert resource_fula_ordboken.get_version() == "0.1.0"
