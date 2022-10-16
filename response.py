import socket
from request import Request
from fs import is_valid_path, read_file


class ResponseParamaters:
    def __init__(self,
                 http_version: str,
                 status_code: int,
                 status_phrase: str,
                 headers: dict[str, str],
                 body: bytes):
        self.http_version = http_version
        self.status_code = status_code
        self.status_phrase = status_phrase
        self.headers = headers
        self.body = body


BLANK_RESPONSE = ResponseParamaters("HTTP/1.1", -4, "", {}, b"")

REDIRECTS = {
    "/": "/index.html"
}


class Response:
    def __init__(self, paramaters: ResponseParamaters=BLANK_RESPONSE):
        self._http_version = paramaters.http_version
        self._status_code = paramaters.status_code
        self._status_phrase = paramaters.status_phrase
        self._headers = paramaters.headers
        self._body = paramaters.body

    def compose_response(self, request: Request):
        if request.is_valid() and is_valid_path(request.get_path()):
            self._status_code = 200
            self._status_phrase = "OK"
            self._body = read_file(request.get_path())

        elif request.is_valid and request.get_path() in REDIRECTS.keys():
            self._status_code = 301
            self._headers = {"Location": f"http://localhost:8888{REDIRECTS[request.get_path()]}"}
            self._status_phrase = "Moved Permanently"

        elif request.is_valid() and not is_valid_path(request.get_path()):
            self._status_code = 404
            self._status_phrase = "Not Found"
            self._body = b"Not Found"
            print(self.encode())

    def _generate_status_line(self) -> str:
        return f"{self._http_version} {str(self._status_code)} {self._status_phrase}"

    def _generate_headers(self) -> str:
        headers = ""
        for key in self._headers.keys():
            headers += key + ": " + self._headers[key] + "\r\n"
        return headers

    def is_valid(self):
        return not (self._http_version == "" or self._status_code < 0 or self._status_phrase == "")

    def encode(self):
        status_line = self._generate_status_line()
        headers = self._generate_headers()
        body = self._body
        resp = status_line.encode() + b"\r\n" + str(headers).encode() + b"\r\n" + body
        return resp
