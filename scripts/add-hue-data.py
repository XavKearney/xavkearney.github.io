#!/usr/bin/env python3
"""Add dominant hue data to photos.js manifest by analysing thumbnail images."""

import json
import re
from pathlib import Path
from PIL import Image
import colorsys

REPO_ROOT = Path(__file__).parent.parent
THUMB_DIR = REPO_ROOT / 'photography' / 'photos' / 'thumb'
MANIFEST_PATH = REPO_ROOT / 'photography' / 'photos.js'


def dominant_hue(img_path):
    """Extract dominant hue (0-360) from an image using histogram analysis."""
    img = Image.open(img_path).convert('RGB')
    img = img.resize((50, 50), Image.Resampling.LANCZOS)
    pixels = list(img.getdata())

    # Build hue histogram, weighted by saturation
    # 36 bins = 10° each
    bins = [0.0] * 36
    total_sat = 0
    sat_count = 0

    for r, g, b in pixels:
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        # Skip very dark, very light, or very desaturated pixels
        if s < 0.08 or v < 0.08:
            continue
        bin_idx = int(h * 36) % 36
        weight = s * v  # weight by saturation and value
        bins[bin_idx] += weight
        total_sat += s
        sat_count += 1

    if sat_count == 0:
        # Greyscale image — assign hue=0, low saturation
        return 0, 0.0

    # Find peak bin
    peak_bin = max(range(36), key=lambda i: bins[i])
    peak_hue = (peak_bin * 10 + 5)  # centre of bin, in degrees
    avg_sat = total_sat / sat_count

    return peak_hue, round(avg_sat, 3)


def main():
    # Read existing manifest
    text = MANIFEST_PATH.read_text()
    # Strip the "var PHOTO_MANIFEST = " prefix and ";\n" suffix
    json_str = re.sub(r'^var PHOTO_MANIFEST = ', '', text).rstrip().rstrip(';')
    manifest = json.loads(json_str)

    print(f"Processing {len(manifest)} photos...")

    for entry in manifest:
        thumb_path = THUMB_DIR / f"{entry['id']}.webp"
        if not thumb_path.exists():
            print(f"  Missing: {thumb_path.name}")
            entry['hue'] = 0
            entry['sat'] = 0
            continue

        hue, sat = dominant_hue(thumb_path)
        entry['hue'] = hue
        entry['sat'] = sat
        print(f"  {entry['id']}: hue={hue}° sat={sat}")

    # Sort by hue
    manifest.sort(key=lambda p: p['hue'])

    # Write updated manifest
    with open(MANIFEST_PATH, 'w') as f:
        f.write('var PHOTO_MANIFEST = ')
        json.dump(manifest, f, indent=2)
        f.write(';\n')

    print(f"\nDone! Photos sorted by hue.")


if __name__ == '__main__':
    main()
