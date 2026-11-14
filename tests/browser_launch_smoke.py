#!/usr/bin/env python3
"""Run inside a fresh Kasm desktop, before opening Chromium.

Reproduce Java's closed-pipe URL launch without needing a JDK or an appliance.
Verify that XFCE and xdg-open deliver the exact URL to a loopback HTTP server.
"""
import http.server
import queue
import subprocess
import threading


def main():
    requests = queue.Queue()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            requests.put(self.path)
            body = b'<html><title>Kasm browser smoke test</title>Browser launch passed</html>'
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            for index, command in enumerate([
                ['exo-open', '--launch', 'WebBrowser'],
                ['xdg-open'],
            ]):
                path = f'/sso-smoke-{index}?state=alpha%2Bbeta&return=%2Fconsole%3Fa%3D1'
                url = f'http://127.0.0.1:{server.server_port}{path}'
                process = subprocess.Popen(command + [url], stdin=subprocess.DEVNULL,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    result = process.wait(timeout=15)
                finally:
                    # Java closes these when the immediate xdg/exo process exits,
                    # even if its GUI descendants still have inherited handles.
                    process.stdout.close()
                    process.stderr.close()
                if result:
                    raise RuntimeError(f'{command[0]} exited with {result}')
                while True:
                    try:
                        actual = requests.get(timeout=20)
                    except queue.Empty:
                        raise RuntimeError(f'{command[0]} did not open the test URL') from None
                    if actual == '/favicon.ico':
                        continue
                    if actual != path:
                        raise RuntimeError(f'{command[0]} changed the URL: {actual!r}')
                    break
                print(f'PASS: {command[0]} with closed caller pipes and intact URL')
        finally:
            server.shutdown()


if __name__ == '__main__':
    main()
