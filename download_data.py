"""Download the pinned public dataset mirror and verify the expected bytes."""
import hashlib
from pathlib import Path
from urllib.request import urlopen

URL = ("https://raw.githubusercontent.com/Quantique-Realm/cookie-cats-ab-test/"
       "5fff3ae4e17de6cecb31a46650110bc1bc2f8f77/data/cookie_cats.csv")
SHA256 = "5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd"


def main():
    path = Path(__file__).resolve().parent / "data" / "cookie_cats.csv"
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == SHA256:
        print(f"Verified existing dataset: {path}")
        return
    with urlopen(URL, timeout=60) as response:
        payload = response.read()
    if hashlib.sha256(payload).hexdigest() != SHA256:
        raise ValueError("Dataset checksum mismatch; no file was written.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    print(f"Downloaded and verified: {path}")


if __name__ == "__main__":
    main()
