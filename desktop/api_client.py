"""API client for Django backend with Basic auth."""
import base64
import requests

DEFAULT_BASE = "http://localhost:8000/api"


class EquipmentAPI:
    def __init__(self, base_url=None, username=None, password=None):
        self.base = (base_url or DEFAULT_BASE).rstrip("/")
        self.username = username or ""
        self.password = password or ""
        self._auth_header = None
        if username and password:
            self._auth_header = self._make_auth(username, password)

    @staticmethod
    def _make_auth(username, password):
        raw = f"{username}:{password}"
        encoded = base64.b64encode(raw.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def set_credentials(self, username, password):
        self.username = username
        self.password = password
        self._auth_header = self._make_auth(username, password) if username and password else None

    def _headers(self):
        return dict(self._auth_header) if self._auth_header else {}

    def login(self, username, password):
        self.set_credentials(username, password)
        r = requests.get(f"{self.base}/history/", headers=self._headers(), timeout=10)
        r.raise_for_status()
        return True

    def upload_csv(self, path, name=None):
        with open(path, "rb") as f:
            files = {"file": (name or path, f, "text/csv")}
            data = {"name": name} if name else {}
            r = requests.post(
                f"{self.base}/upload/",
                headers=self._headers(),
                files=files,
                data=data,
                timeout=30,
            )
        r.raise_for_status()
        return r.json()

    def history(self):
        r = requests.get(f"{self.base}/history/", headers=self._headers(), timeout=10)
        r.raise_for_status()
        return r.json()

    def summary(self, dataset_id):
        r = requests.get(
            f"{self.base}/summary/{dataset_id}/",
            headers=self._headers(),
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def download_pdf(self, dataset_id, save_path):
        r = requests.get(
            f"{self.base}/report/{dataset_id}/pdf/",
            headers=self._headers(),
            timeout=30,
            stream=True,
        )
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return save_path
