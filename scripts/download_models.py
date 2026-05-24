"""Download model files from GitHub Releases on first container start."""
import os
import sys
import urllib.request

REPO = "Okkootsu/Bitirme"
TAG = "v1.0-models"
BASE_URL = f"https://github.com/{REPO}/releases/download/{TAG}"

FILES = {
    "diabetes_model.pkl": "/app/diabetes_model.pkl",
    "model.onnx": "/app/onnx_model/model.onnx",
    "model.onnx.data": "/app/onnx_model/model.onnx.data",
    "tokenizer.json": "/app/onnx_model/tokenizer.json",
    "tokenizer_config.json": "/app/onnx_model/tokenizer_config.json",
    "index.faiss": "/app/faiss_index/index.faiss",
    "chunks.json": "/app/faiss_index/chunks.json",
}


def download_file(url: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"  Downloading {os.path.basename(dest)} ...", flush=True)
    urllib.request.urlretrieve(url, dest)
    size_mb = os.path.getsize(dest) / (1024 * 1024)
    print(f"  Done ({size_mb:.1f} MB)", flush=True)


def main() -> None:
    missing = {name: path for name, path in FILES.items() if not os.path.exists(path)}

    if not missing:
        print("All model files already present.", flush=True)
        return

    print(f"Downloading {len(missing)} model file(s) from GitHub Releases ...", flush=True)
    for name, path in missing.items():
        url = f"{BASE_URL}/{name}"
        try:
            download_file(url, path)
        except Exception as e:
            print(f"ERROR: Failed to download {name}: {e}", file=sys.stderr, flush=True)
            sys.exit(1)

    print("All model files downloaded successfully.", flush=True)


if __name__ == "__main__":
    main()
