import argparse
import sys

from src.commands import server


def main():
    parser = argparse.ArgumentParser(
        prog="SystoolBox",
        description=(
            "SystoolBox — Nord Transit Logistics\n\n"
            "A CLI tool for monitoring system metrics: CPU, memory, OS.\n"
            "You can run the HTTP exporter server or extend with additional commands."
        ),
        formatter_class=argparse.RawTextHelpFormatter  # preserve newlines
    )

    # Register commands
    subparsers = parser.add_subparsers(
        title="Available Commands",
        dest="command",
        required=True,
        help="Choose a command to execute"
    )

    server.register(subparsers)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
