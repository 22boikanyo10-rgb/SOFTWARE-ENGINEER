from software_engineer.hello import greet


def test_greet() -> None:
    assert greet("World") == "Hello, World!"
