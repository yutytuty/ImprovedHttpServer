from enum import Enum
from fs import valid_path


class ERequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    INVALID = ""

    @classmethod
    def from_str(cls, other: str):
        """
        Converts a string to an enum literal
        :param other: str
        :return: ERequestType
        """
        for i in cls:
            if i.value == other:
                return i

        return cls.INVALID


class RequestParamaters:
    def __init__(self,
                 http_version: str,
                 method: ERequestMethod,
                 path: str,
                 headers: dict[str, str],
                 body: bytes):
        self.http_version = http_version
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body


BLANK_REQUEST = RequestParamaters("",
                                  ERequestMethod.INVALID,
                                  "",
                                  {},
                                  b"")


class Request:
    def __init__(self, params=BLANK_REQUEST):
        self._http_version = params.http_version
        self._method = params.method
        self._path = params.path
        self._headers: dict[str, str] = params.headers
        self._body: bytes = params.body

    def set(self, http_version: str,
            method: ERequestMethod,
            path: str,
            headers: dict[str, str],
            body: bytes):
        self.set_status_line(http_version, method, path)
        self.set_headers(headers)
        self.set_body(body)

    def set_status_line(self,
                        http_version: str,
                        method: ERequestMethod,
                        path: str):
        self._http_version = http_version
        self._method = method
        self._path = path

    def set_headers(self, headers: dict[str, str]):
        self._headers = headers

    def set_body(self, body: bytes):
        self._body = body

    def parse(self, raw_request: bytes) -> bool:
        request_split = raw_request.split(b"\r\n\r\n")
        if len(request_split) != 2:
            return False
        header, body = request_split
        header = header.decode()
        header_lines = header.split("\r\n")
        status_line_paramaters = header_lines[0].split(" ")
        if len(status_line_paramaters) != 3:
            return False
        request_method = ERequestMethod.from_str(status_line_paramaters[0])
        path = status_line_paramaters[1]
        http_version = status_line_paramaters[2]
        if request_method == ERequestMethod.INVALID or \
                not http_version.startswith("HTTP/") or \
                not path.startswith("/"):
            return False
        self._method = request_method
        self._path = path
        self._http_version = http_version

        headers: dict[str, str] = {}
        for line in header_lines[1:]:
            key, value = line.split(": ")
            headers[key] = value
        self._headers = headers
        self._body = body
        return True

    def is_valid(self) -> bool:
        """
        :return: whether all fields have been filled and path exists
        """
        return not (self._http_version == "" or
                    self._method == ERequestMethod.INVALID or
                    self._path == "" or
                    not valid_path(self._path))

    def get_path(self) -> str:
        return self._path

    def get_method(self) -> ERequestMethod:
        return self._method

    def _generate_status_line(self) -> str:
        return f"{self._method.value} {self._path} {self._http_version}"

    def _generate_headers(self) -> str:
        headers = ""
        for key in self._headers.keys():
            headers += key + ": " + self._headers[key] + "\r\n"
        return headers

    def __str__(self):
        if not self.is_valid():
            return ""
        status_line = self._generate_status_line()
        headers = self._generate_headers()
        return status_line + headers + "\r\n" + self._body.decode() + "\r\n"

    def __bytes__(self):
        return self.__str__().encode()
