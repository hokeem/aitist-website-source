"""Sample the closed stone surfaces for the WebGL scene.

Run with Pillow, NumPy and SciPy installed:
    python3 build-stone-surfaces.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter


ROOT = Path(__file__).resolve().parent / "dist" / "assets"
GRAINS_PER_STONE = 16800

# Half-thickness relative to the stone width, followed by bevel width.
PROFILES = [(0.079, 0.028), (0.060, 0.020), (0.076, 0.027),
            (0.085, 0.023), (0.114, 0.033), (0.053, 0.022),
            (0.137, 0.047)]


def sample_surface(path, index, rng):
    image = Image.open(path).convert("RGBA")
    image = image.crop(image.getchannel("A").point(lambda alpha: 255 if alpha > 115 else 0).getbbox())
    image.thumbnail((420, 420))
    rgba = np.asarray(image) / 255.0
    height, width = rgba.shape[:2]
    mask = rgba[:, :, 3] > 0.48
    distance = distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    inner = np.maximum(0, distance - 1)
    y, x = np.indices(mask.shape, dtype=float)
    x = (x + .5 - width / 2) / width
    y = (y + .5 - height / 2) / width
    thickness, bevel = PROFILES[index]
    rim = np.sqrt(np.clip(inner / (bevel * width), 0, 1))
    luminance = gaussian_filter(np.sum(rgba[:, :, :3] * [0.2126, 0.7152, 0.0722], axis=-1), 1.8)

    # Bend and terrace the solids in depth while retaining each original outline.
    if index == 3:
        midline = .17 * np.abs(x + .20 * y) - .028
    elif index == 4:
        midline = .10 * np.tanh(np.sin((x + .55 * y) * 25)) + .06 * y
    elif index == 5:
        midline = .16 * y + .05 * x
    elif index == 6:
        midline = .038 * np.sin(8 * x + 5 * y) + .035 * y
    else:
        midline = .04 * x - .04 * y

    if index == 4:
        thickness *= .72 + .28 * np.cos((x + y) * 9) ** 2
    elif index == 6:
        thickness *= .80 + .20 * np.cos(x * 7 - y * 4)

    # Opposing surfaces meet at the bevel rim, including around the aperture.
    front = midline + rim * thickness
    back = midline - rim * thickness
    arrays = []
    for depth, facing in ((front, 1), (back, -1)):
        dy, dx = np.gradient(depth, 1 / width)
        normal = np.stack((-dx * facing, -dy * facing, np.full_like(dx, facing)), axis=-1)
        slope = np.linalg.norm(normal, axis=-1)
        normal /= slope[:, :, None]
        surface = np.dstack((x, y, depth, normal, luminance))
        arrays.append((surface[mask], np.minimum(slope[mask], 3.1)))

    surface = np.concatenate([entry[0] for entry in arrays])
    area = np.concatenate([entry[1] for entry in arrays])
    indices = rng.choice(len(surface), GRAINS_PER_STONE, p=area / area.sum())
    selected = surface[indices]
    selected[:, :2] += rng.uniform(-.45 / width, .45 / width, (GRAINS_PER_STONE, 2))
    return np.rint(selected * 32767).astype("<i2").tobytes()


def main():
    paths = sorted((ROOT / "stones").glob("*.webp"))
    if len(paths) != len(PROFILES):
        raise ValueError(f"Expected {len(PROFILES)} stone source assets, got {len(paths)}")
    rng = np.random.default_rng(20126)
    data = b"".join(sample_surface(path, index, rng) for index, path in enumerate(paths))
    (ROOT / "stone-surfaces.bin").write_bytes(data)


if __name__ == "__main__":
    main()
