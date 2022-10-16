import socket
from request import Request
from fs import valid_path


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


BLANK_RESPONSE = ResponseParamaters("HTTP/1.1", -1, "", {}, b"")


class Response:
    def __init__(self, paramaters: ResponseParamaters = BLANK_RESPONSE):
        self._http_version = paramaters.http_version
        self._status_code = paramaters.status_code
        self._status_phrase = paramaters.status_phrase
        self._headers = paramaters.headers
        self._body = paramaters.body

    def compose_response(self, request: Request):
        print(f"{request.is_valid()}")
        if request.is_valid() and valid_path(request.get_path()):
            self._status_code = 200
            self._status_phrase = "OK"
            with open(request.get_path(), "rb") as f:
                self._body = f.read()

    def _generate_status_line(self) -> str:
        return f"{self._http_version} {str(self._status_code)} {self._status_phrase}"

    def _generate_headers(self) -> str:
        headers = ""
        for key in self._headers.keys():
            headers += key + ": " + self._headers[key] + "\r\n"
        return headers

    def is_valid(self):
        return not (self._http_version == "" or self._status_code < 0 or self._status_phrase == ""
                    or self._headers == {} or self._body == b"")

    def __str__(self) -> str:
        if not self.is_valid():
            return ""
        status_line = self._generate_status_line()
        headers = self._generate_headers()
        body = self._body.decode()
        return f"{status_line}\r\n{headers}\r\n{body}"

    def __bytes__(self):
        return self.__str__().encode()
