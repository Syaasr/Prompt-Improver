from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(CORSRequestHandler, self).end_headers()

def run(port=5173, directory=None):
    if directory:
        os.chdir(directory)
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print(f"Serving directory {os.getcwd()} on port {port} with CORS...")
    httpd.serve_forever()

if __name__ == '__main__':
    port = 5173
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    run(port=port, directory=directory)
