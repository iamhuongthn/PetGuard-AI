"""Record the actual runtime rather than guessing historical versions."""
import hashlib, platform, sys, subprocess, shutil
from importlib.metadata import version, PackageNotFoundError

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def environment():
    packages = {}
    for name in ("ultralytics", "opencv-python", "opencv-python-headless", "numpy", "pandas", "gradio", "Pillow", "torch", "pytest", "tabulate"):
        try: packages[name] = version(name)
        except PackageNotFoundError: packages[name] = None
    return {"python": sys.version, "platform": platform.platform(), "packages": packages, "ffmpeg": subprocess.check_output(["ffmpeg", "-version"], text=True).splitlines()[0] if shutil.which("ffmpeg") else None}
