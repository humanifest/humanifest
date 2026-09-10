"""Serve only a compiled synthetic probe, on loopback, without application API access."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; font-src 'self' data:; connect-src 'none'; "
            "object-src 'none'; base-uri 'none'; form-action 'none'",
        )
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(403)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()
    directory = args.directory.resolve(strict=True)
    if not (directory / "humanifest-probes/global-mapping-ui.html").is_file():
        parser.error("Expected the compiled synthetic probe directory")
    handler = partial(Handler, directory=str(directory))
    ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()
