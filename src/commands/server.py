import argparse
import logging

from modules import server


def run(args):
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    server.app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


def register(subparsers):
    parser = subparsers.add_parser(
        "server",
        help="Start the HTTP system metrics exporter",
        description=(
            "Starts an HTTP server exposing system metrics.\n\n"
            "Available endpoints:\n"
            "  /status?i=os   -> OS information\n"
            "  /status?i=mem  -> Memory status\n"
            "  /status?i=cpu  -> CPU status\n\n"
            "Example usage:\n"
            "  systoolbox server\n"
            "  curl http://localhost:5000/status?i=cpu"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.set_defaults(func=run)
