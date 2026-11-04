"""The CT scan of the medical imaging demo: downloads it, makes it small for the web, and writes `ct_chest.npz.bz2`.

The scan is LIDC-IDRI-0001, a chest CT of the LIDC-IDRI collection (The Cancer Imaging Archive, CC BY 3.0): 133 slices
of 512 x 512 pixels, 2.5 mm apart. This script keeps one slice in two (5 mm apart) from the kidneys up, halves their
size (256 x 256, 1.4 mm per pixel) and blanks the air outside the body: 1.9 MB in Hounsfield units, compressed with
bz2 (zlib gives 2.6 MB). Run it once, on the desktop:

    uv run --with pydicom --with numpy --with opencv-python-headless python make_ct_data.py

The repository does not carry the result: copy it into the website resources
(`docs/clone_website_resources/imgui-bundle.pages.dev/resources/explorables/medical_imaging/`), commit it there, and
deploy the site. The demo `medical_imaging.py` downloads it from the site at its first run.
"""
import bz2
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import cv2
import numpy as np
import pydicom  # type: ignore[import-not-found]

SERIES_UID = "1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192"  # LIDC-IDRI-0001, its CT
TCIA_API = "https://services.cancerimagingarchive.net/nbia-api/services/v1/"
SLICE_STEP = 2  # one slice in two
FIRST_SLICE = 16  # the kidneys, below the lungs, are dropped
SIDE = 256  # pixels, after the resize
OUTPUT = Path(__file__).parent / "ct_chest.npz.bz2"


def download_series() -> list[pydicom.Dataset]:
    """The series' slices, read from TCIA's public API, ordered from the feet to the head"""
    with urllib.request.urlopen(TCIA_API + "getImage?SeriesInstanceUID=" + SERIES_UID) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    slices = [pydicom.dcmread(io.BytesIO(archive.read(n))) for n in archive.namelist() if n.endswith(".dcm")]
    slices.sort(key=lambda s: float(s.ImagePositionPatient[2]))
    return slices


def body_mask(hu: np.ndarray) -> np.ndarray:
    """The body on a slice: its largest object denser than -400 HU, its holes (the lungs) filled"""
    dense = cv2.morphologyEx((hu > -400).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(dense)
    if count <= 1:
        return np.zeros(hu.shape, bool)
    largest = (labels == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    contours, _ = cv2.findContours(largest, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(largest)
    cv2.drawContours(filled, contours, -1, 1, -1)
    return cv2.dilate(filled, np.ones((7, 7), np.uint8)).astype(bool)


def main() -> None:
    slices = download_series()[FIRST_SLICE::SLICE_STEP]
    out = []
    for s in slices:
        hu = s.pixel_array.astype(np.float32) * float(s.RescaleSlope) + float(s.RescaleIntercept)
        hu = np.where(body_mask(hu), np.clip(hu, -1024, 3071), -1024)  # the table and the air around: blank
        out.append(cv2.resize(hu, (SIDE, SIDE), interpolation=cv2.INTER_AREA))
    volume = np.round(np.stack(out)).astype(np.int16)
    row_mm, col_mm = (float(v) * slices[0].Rows / SIDE for v in slices[0].PixelSpacing)
    z_mm = abs(float(slices[1].ImagePositionPatient[2]) - float(slices[0].ImagePositionPatient[2]))
    info = {"source": "LIDC-IDRI-0001, LIDC-IDRI collection, The Cancer Imaging Archive", "license": "CC BY 3.0"}
    npz = io.BytesIO()
    np.savez(npz, hu=volume, spacing_mm=np.array([z_mm, row_mm, col_mm]), info=json.dumps(info))
    OUTPUT.write_bytes(bz2.compress(npz.getvalue(), 9))
    size_mb = OUTPUT.stat().st_size / 1e6
    print(f"{OUTPUT.name}: {volume.shape}, spacing {z_mm} x {row_mm} x {col_mm} mm, {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
