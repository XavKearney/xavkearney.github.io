#!/usr/bin/env python3
"""
Process raw photos into web-friendly formats for the xav.ai photography gallery.

Usage: python3 scripts/process-photos.py /path/to/raw/photos

Requires: exiftool, cwebp, sips (macOS), Pillow
"""

import sys
import os
import json
import subprocess
import time
import base64
import re
import io
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
from urllib.request import Request, urlopen
from urllib.error import URLError

# Config
THUMB_MAX = 600
FULL_MAX = 2000
BLUR_WIDTH = 20
WEBP_QUALITY_THUMB = 75
WEBP_QUALITY_FULL = 80
NOMINATIM_DELAY = 1.1
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.heic'}

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_ROOT / 'photography'
THUMB_DIR = OUTPUT_DIR / 'photos' / 'thumb'
FULL_DIR = OUTPUT_DIR / 'photos' / 'full'
GEOCODE_CACHE_FILE = SCRIPT_DIR / '.geocode-cache.json'


def slugify(filename):
    """Convert a filename to a URL-safe ID."""
    name = Path(filename).stem.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = name.strip('-')
    return name


def extract_exif(source_dir):
    """Extract EXIF data from all photos using exiftool."""
    print("Extracting EXIF data...")
    files = []
    for f in sorted(Path(source_dir).iterdir()):
        if f.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(str(f))

    if not files:
        print("No supported image files found.")
        sys.exit(1)

    result = subprocess.run(
        ['exiftool', '-json', '-n',
         '-GPSLatitude', '-GPSLongitude',
         '-DateTimeOriginal', '-CreateDate',
         '-ImageWidth', '-ImageHeight',
         '-Orientation', '-Make', '-Model'] + files,
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"exiftool error: {result.stderr}")
        sys.exit(1)

    return json.loads(result.stdout)


def load_geocode_cache():
    """Load cached geocoding results."""
    if GEOCODE_CACHE_FILE.exists():
        with open(GEOCODE_CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_geocode_cache(cache):
    """Save geocoding results to cache."""
    with open(GEOCODE_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


def cache_key(lat, lon):
    """Round lat/lon to 2dp for cache key."""
    return f"{round(lat, 2)},{round(lon, 2)}"


def reverse_geocode(lat, lon, cache):
    """Reverse geocode GPS coordinates to a location string."""
    key = cache_key(lat, lon)
    if key in cache:
        return cache[key]

    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?format=json&lat={lat}&lon={lon}&zoom=10&accept-language=en"
    )
    req = Request(url, headers={'User-Agent': 'xav-ai-gallery/1.0'})

    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except (URLError, json.JSONDecodeError) as e:
        print(f"  Geocoding failed for ({lat}, {lon}): {e}")
        cache[key] = None
        return None

    address = data.get('address', {})

    # Build location string: city/town + country/state
    city = (address.get('city') or address.get('town')
            or address.get('village') or address.get('municipality')
            or address.get('county'))

    country = address.get('country')
    state = address.get('state')

    # For some countries, use state instead of country for more specificity
    # e.g. "Edinburgh, Scotland" not "Edinburgh, United Kingdom"
    uk_nations = {'Scotland', 'Wales', 'England', 'Northern Ireland'}
    us_states = state if country == 'United States' else None

    if city and state and state in uk_nations:
        location = f"{city}, {state}"
    elif city and us_states:
        location = f"{city}, {state}"
    elif city and country:
        location = f"{city}, {country}"
    elif country:
        location = country
    else:
        location = None

    cache[key] = location
    return location


def convert_heic_to_jpeg(heic_path, output_path):
    """Convert HEIC to JPEG using sips (macOS native)."""
    result = subprocess.run(
        ['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '95',
         str(heic_path), '--out', str(output_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  sips conversion failed: {result.stderr}")
        return False
    return True


def convert_to_webp(input_path, output_path, quality):
    """Convert image to WebP using cwebp."""
    result = subprocess.run(
        ['cwebp', '-q', str(quality), '-quiet', str(input_path), '-o', str(output_path)],
        capture_output=True, text=True
    )
    return result.returncode == 0


def generate_blur_placeholder(img):
    """Generate a tiny base64-encoded blur placeholder from a PIL Image."""
    aspect = img.width / img.height
    blur_w = BLUR_WIDTH
    blur_h = max(1, round(blur_w / aspect))

    blurred = img.copy()
    blurred = blurred.resize((blur_w, blur_h), Image.Resampling.LANCZOS)
    blurred = blurred.filter(ImageFilter.GaussianBlur(radius=2))

    buf = io.BytesIO()
    blurred.save(buf, format='JPEG', quality=30)
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return f"data:image/jpeg;base64,{b64}"


def process_photo(source_path, photo_id, tmp_dir):
    """Process a single photo: resize, convert to WebP, generate blur."""
    source = Path(source_path)
    is_heic = source.suffix.lower() == '.heic'

    # Step 1: Get a JPEG/PIL-compatible version
    if is_heic:
        jpeg_tmp = tmp_dir / f"{photo_id}_converted.jpg"
        if not convert_heic_to_jpeg(source, jpeg_tmp):
            print(f"  Skipping {source.name}: HEIC conversion failed")
            return None
        work_path = jpeg_tmp
    else:
        work_path = source

    # Step 2: Open with Pillow and auto-orient
    try:
        img = Image.open(work_path)
        img = ImageOps.exif_transpose(img)
    except Exception as e:
        print(f"  Skipping {source.name}: {e}")
        return None

    # Ensure RGB (some images might be RGBA or other modes)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    original_w, original_h = img.size

    # Step 3: Generate full-size
    full_img = img.copy()
    full_img.thumbnail((FULL_MAX, FULL_MAX), Image.Resampling.LANCZOS)
    full_w, full_h = full_img.size

    full_jpg_tmp = tmp_dir / f"{photo_id}_full.jpg"
    full_img.save(full_jpg_tmp, format='JPEG', quality=92)

    full_webp = FULL_DIR / f"{photo_id}.webp"
    if not convert_to_webp(full_jpg_tmp, full_webp, WEBP_QUALITY_FULL):
        print(f"  WebP conversion failed for {source.name} (full)")
        return None

    # Step 4: Generate thumbnail
    thumb_img = img.copy()
    thumb_img.thumbnail((THUMB_MAX, THUMB_MAX), Image.Resampling.LANCZOS)

    thumb_jpg_tmp = tmp_dir / f"{photo_id}_thumb.jpg"
    thumb_img.save(thumb_jpg_tmp, format='JPEG', quality=85)

    thumb_webp = THUMB_DIR / f"{photo_id}.webp"
    if not convert_to_webp(thumb_jpg_tmp, thumb_webp, WEBP_QUALITY_THUMB):
        print(f"  WebP conversion failed for {source.name} (thumb)")
        return None

    # Step 5: Generate blur placeholder
    blur = generate_blur_placeholder(img)

    # Clean up temp files
    for tmp in [full_jpg_tmp, thumb_jpg_tmp]:
        tmp.unlink(missing_ok=True)
    if is_heic:
        (tmp_dir / f"{photo_id}_converted.jpg").unlink(missing_ok=True)

    img.close()

    return {
        'w': full_w,
        'h': full_h,
        'aspect': round(full_w / full_h, 3),
        'blur': blur,
    }


def parse_date(exif_entry):
    """Extract a sortable date string from EXIF data."""
    dt = exif_entry.get('DateTimeOriginal') or exif_entry.get('CreateDate')
    if not dt or not isinstance(dt, str):
        return '1970-01-01'
    # EXIF format: "2025:01:06 13:02:11" -> "2025-01-06"
    try:
        return dt[:10].replace(':', '-')
    except (IndexError, AttributeError):
        return '1970-01-01'


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} /path/to/raw/photos")
        sys.exit(1)

    source_dir = Path(sys.argv[1])
    if not source_dir.is_dir():
        print(f"Not a directory: {source_dir}")
        sys.exit(1)

    # Ensure output directories exist
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    FULL_DIR.mkdir(parents=True, exist_ok=True)

    # Create temp directory for intermediate files
    tmp_dir = SCRIPT_DIR / '.tmp'
    tmp_dir.mkdir(exist_ok=True)

    # Step 1: Extract EXIF
    exif_data = extract_exif(source_dir)
    print(f"Found {len(exif_data)} photos")

    # Step 2: Reverse geocode
    geocode_cache = load_geocode_cache()
    photos_needing_geocode = [
        e for e in exif_data
        if e.get('GPSLatitude') is not None and e.get('GPSLongitude') is not None
    ]
    print(f"{len(photos_needing_geocode)} photos have GPS data")

    new_geocodes = 0
    for entry in photos_needing_geocode:
        lat, lon = entry['GPSLatitude'], entry['GPSLongitude']
        key = cache_key(lat, lon)
        if key not in geocode_cache:
            new_geocodes += 1

    if new_geocodes > 0:
        print(f"Geocoding {new_geocodes} new locations (estimated {int(new_geocodes * NOMINATIM_DELAY)}s)...")
        for i, entry in enumerate(photos_needing_geocode):
            lat, lon = entry['GPSLatitude'], entry['GPSLongitude']
            key = cache_key(lat, lon)
            if key not in geocode_cache:
                location = reverse_geocode(lat, lon, geocode_cache)
                print(f"  [{i+1}/{len(photos_needing_geocode)}] ({lat:.2f}, {lon:.2f}) -> {location}")
                time.sleep(NOMINATIM_DELAY)
        save_geocode_cache(geocode_cache)
    else:
        print("All locations cached, skipping geocoding")

    # Step 3: Process each photo
    manifest = []
    for i, entry in enumerate(exif_data):
        source_path = entry['SourceFile']
        filename = Path(source_path).name
        photo_id = slugify(filename)

        print(f"[{i+1}/{len(exif_data)}] Processing {filename} -> {photo_id}")

        result = process_photo(source_path, photo_id, tmp_dir)
        if result is None:
            continue

        # Build location from geocode cache
        lat = entry.get('GPSLatitude')
        lon = entry.get('GPSLongitude')
        location = None
        if lat is not None and lon is not None:
            location = geocode_cache.get(cache_key(lat, lon))

        photo_entry = {
            'id': photo_id,
            'thumb': f"photos/thumb/{photo_id}.webp",
            'full': f"photos/full/{photo_id}.webp",
            'blur': result['blur'],
            'w': result['w'],
            'h': result['h'],
            'aspect': result['aspect'],
            'location': location,
            'date': parse_date(entry),
        }
        manifest.append(photo_entry)

    # Sort by date descending (newest first)
    manifest.sort(key=lambda p: p['date'], reverse=True)

    # Step 4: Write manifest
    manifest_path = OUTPUT_DIR / 'photos.js'
    with open(manifest_path, 'w') as f:
        f.write('var PHOTO_MANIFEST = ')
        json.dump(manifest, f, indent=2)
        f.write(';\n')

    print(f"\nDone! Processed {len(manifest)} photos")
    print(f"Manifest: {manifest_path}")
    print(f"Thumbnails: {THUMB_DIR}")
    print(f"Full size: {FULL_DIR}")

    # Summary stats
    thumb_size = sum(f.stat().st_size for f in THUMB_DIR.glob('*.webp'))
    full_size = sum(f.stat().st_size for f in FULL_DIR.glob('*.webp'))
    print(f"\nThumbnails total: {thumb_size / 1024 / 1024:.1f} MB")
    print(f"Full-size total: {full_size / 1024 / 1024:.1f} MB")

    with_location = sum(1 for p in manifest if p['location'])
    print(f"Photos with location: {with_location}/{len(manifest)}")

    # Clean up temp dir
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()


if __name__ == '__main__':
    main()
