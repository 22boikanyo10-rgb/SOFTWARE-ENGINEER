from software_engineer.app import greet_app


def test_greet_app_default_config() -> None:
    assert greet_app("World") == "Hello, World! (development)"
