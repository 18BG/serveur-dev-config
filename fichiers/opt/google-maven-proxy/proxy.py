#!/usr/bin/env python3
"""Proxy local vers dl.google.com (dépôt Maven de Google, utilisé par Gradle).

Depuis ce serveur, dl.google.com ne répond jamais aux téléchargements de plus
de ~200 Ko, ni aux HEAD/404 en HTTP/1.1 (le protocole de Gradle). curl, en
HTTP/2 et par morceaux de 128 Ko, passe sans problème : ce proxy reçoit les
requêtes de Gradle et les fait exécuter par curl de cette façon.

Gradle y est redirigé par ~/.gradle/init.d/google-maven-mirror.gradle.
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ORIGIN = "https://dl.google.com"
HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8765"))
CHUNK = 128 * 1024
PARALLEL = 6
RETRIES = 4
TIMEOUT = "20"


def curl(*args):
    for attempt in range(1, RETRIES + 1):
        result = subprocess.run(
            ["curl", "-sS", "--max-time", TIMEOUT, *args], capture_output=True
        )
        if result.returncode == 0 or attempt == RETRIES:
            return result


def probe(url):
    """Renvoie (statut, taille, content-type, last-modified) via un HEAD HTTP/2."""
    fmt = "%{http_code}|%header{content-length}|%header{content-type}|%header{last-modified}"
    result = curl("-I", "-o", "/dev/null", "-w", fmt, url)
    if result.returncode != 0:
        raise OSError(result.stderr.decode(errors="replace").strip())
    status, length, ctype, modified = result.stdout.decode().split("|", 3)
    return int(status), int(length or -1), ctype, modified


def fetch(url, start, end):
    result = curl("--fail", "-r", f"{start}-{end}", url)
    if result.returncode != 0 or len(result.stdout) != end - start + 1:
        raise OSError(f"bytes {start}-{end}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_HEAD(self):
        self.serve(with_body=False)

    def do_GET(self):
        self.serve(with_body=True)

    def serve(self, with_body):
        url = ORIGIN + self.path.split("?", 1)[0]
        try:
            status, length, ctype, modified = probe(url)
            body = b""
            if status == 200 and with_body and length != 0:
                if length < 0:
                    body = curl("--fail", url).stdout
                else:
                    # Tout est téléchargé avant de répondre : en cas d'échec,
                    # Gradle reçoit un 502 propre plutôt qu'un fichier tronqué.
                    ranges = [(s, min(s + CHUNK, length) - 1) for s in range(0, length, CHUNK)]
                    with ThreadPoolExecutor(PARALLEL) as pool:
                        body = b"".join(pool.map(lambda r: fetch(url, *r), ranges))
        except Exception as err:
            print(f"{self.command} {self.path}: {err}", file=sys.stderr, flush=True)
            self.reply(502)
            return

        if status != 200:
            self.reply(status)
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(body) if with_body else max(length, 0)))
        if ctype:
            self.send_header("Content-Type", ctype)
        if modified:
            self.send_header("Last-Modified", modified)
        self.end_headers()
        if with_body:
            self.wfile.write(body)

    def reply(self, status):
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # seules les erreurs sont journalisées (journalctl -u google-maven-proxy)


if __name__ == "__main__":
    print(f"google-maven-proxy sur http://{HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
