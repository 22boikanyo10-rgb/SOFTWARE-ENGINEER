from argparse import ArgumentParser

from .config import load_config


def greet_app(name: str) -> str:
    config = load_config()
    return f"{config.greeting_prefix}, {name}! ({config.environment})"


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Greet someone with configurable environment settings."
    )
    parser.add_argument("name", help="The name to greet")
    parser.add_argument(
        "--env",
        dest="environment",
        choices=["development", "production"],
        help="Set the application environment",
    )
    parser.add_argument(
        "--prefix",
        dest="greeting_prefix",
        help="Override the greeting prefix",
    )
    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    config = load_config()

    if args.environment:
        config.environment = args.environment
    if args.greeting_prefix:
        config.greeting_prefix = args.greeting_prefix

    message = f"{config.greeting_prefix}, {args.name}! ({config.environment})"
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
