from urllib.parse import quote


class RTSPClient:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 554,
        path: str = "/onvif1"
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.path = path

    @property
    def url(self) -> str:
        username = quote(
            self.username,
            safe=""
        )

        password = quote(
            self.password,
            safe=""
        )

        path = self.path.strip()

        if not path.startswith("/"):
            path = "/" + path

        return (
            f"rtsp://{username}:{password}"
            f"@{self.host}:{self.port}{path}"
        )