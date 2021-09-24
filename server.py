#  coding: utf-8
import socketserver
import os
from datetime import date, datetime


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# Copyright 2021 Xiaoyu Wang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class MyWebServer(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.base = os.path.realpath("./www")
        super().__init__(request, client_address, server)

    def getResponseHeader(self, http_code):
        status_map = {
            200: "OK",
            301: "Moved Permanently",
            400: "Bad Request",
            404: "Not Found",
            405: "Method Not Allowed",
        }
        return f"HTTP/1.1 {http_code} {status_map.get(http_code, 'N/A')}\r\nDate: {datetime.now()} MST\r\n"

    def handleFileRequest(self, request_dest, request_dir):
        MIMETYPE = {
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.css': 'text/css'
        }
        FILEPATH = os.path.normpath(self.base+request_dir)

        if os.path.commonpath([self.base]) != os.path.commonpath([self.base, FILEPATH]):
            request_dest.sendall((self.getResponseHeader(404)+"Connection: close\r\n\r\n").encode("utf-8"))
            return


        # Handle Files
        if os.path.isfile(FILEPATH):
            fname, ftype = os.path.splitext(FILEPATH)
            response = self.getResponseHeader(200)
            with open(FILEPATH) as f:
                content = f.read()
                response += f"Content-Length: {len(content)}\r\nConnection: close\r\nContent-Type:{MIMETYPE[ftype]};charset=UTF-8\r\n\r\n"
                response += content
            request_dest.sendall(response.encode("utf-8"))
            return
        # Handle Directories
        elif os.path.isdir(FILEPATH):
            # 301 redirection for directory name
            if request_dir[-1] != '/':
                request_dir+='/'
                request_dest.sendall((self.getResponseHeader(301) + f"Location: {request_dir}\r\n"+"Connection: close\r\n\r\n").encode("utf-8"))
                return


            FILEPATH = os.path.normpath(FILEPATH+"/index.html")
            response = self.getResponseHeader(200)
            if os.path.isfile(FILEPATH):
                with open(FILEPATH) as f:
                    content = f.read()
                    response += f"Content-Length: {len(content)}\r\nConnection: close\r\nContent-Type:text/html;charset=UTF-8\r\n\r\n"
                    response += content
                request_dest.sendall(response.encode("utf-8"))
                return
            else:
                request_dest.sendall((response + "\r\n").encode("utf-8"))
                return
        else:
            request_dest.sendall((self.getResponseHeader(404)+"Connection: close\r\n\r\n").encode("utf-8"))
            return

    def handle(self):
        try:
            # sanitize input
            self.data = [line.strip() for line in self.request.recv(1024).decode().strip().split('\n')]
            http_data = self.data[0]
            print("Got a request of: %s" % http_data.strip(), end='\n\n')

            request_type, request_dir = http_data.split()[:2]

            if request_type == "GET":

                self.handleFileRequest(self.request, request_dir)

            # POST, PUT, DELETE requests
            else:
                self.request.sendall(bytearray(self.getResponseHeader(405)+"Connection: close\r\n\r\n", 'utf-8'))
                return

            # response = self.getResponseHeader(200, "text/html")+"<html><p>hello world</p></html>\r\n\r\n"
            # self.request.sendall(bytearray(response, 'utf-8'))
            return

        except Exception as e:
            print(f"Error: {e}")

        return


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C

    server.serve_forever()
