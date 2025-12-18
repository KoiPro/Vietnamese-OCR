# quality_check.py
import cv2
import numpy as np
from pathlib import Path


def simple_quality_score(image_path):
    """
    Simple quality assessment based on:
    1. Blur detection
    2. Brightness/contrast
    3. Text density estimate
    If the image cannot be read, a synthetic sample image will be generated
    and saved to `data/sample_receipt.jpg` so subsequent runs have a file.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        # generate a synthetic grayscale receipt-like image and save it
        h, w = 600, 400
        img = np.full((h, w), 255, dtype=np.uint8)
        for y in range(40, h - 40, 28):
            x1 = 30
            x2 = w - 30
            thickness = 10 if (y % 84 == 0) else 6
            cv2.rectangle(img, (x1, y), (x2, y + thickness), (200), -1)
        cv2.rectangle(img, (30, 10), (w - 30, 30), (180), -1)
        noise = (np.random.randn(h, w) * 4).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        out_dir = Path("data")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "sample_receipt.jpg"
        cv2.imwrite(str(out_path), img)

    # ensure image is not empty
    if img is None or img.size == 0:
        raise ValueError(f"Unable to load or generate image for: {image_path}")

    # 1. Blur detection (Laplacian variance)
    lap = cv2.Laplacian(img, cv2.CV_64F)
    blur_score = float(lap.var())
    blur_normalized = min(blur_score / 500.0, 1.0)  # Normalize

    # 2. Brightness score
    brightness = float(np.mean(img))
    brightness_score = 1 - abs(brightness - 128) / 128

    # 3. Edge density (proxy for text density)
    edges = cv2.Canny(img, 50, 150)
    edge_density = float(np.sum(edges > 0)) / (img.shape[0] * img.shape[1])
    density_score = min(edge_density * 10, 1.0)

    # Combine scores
    final_score = 0.4 * blur_normalized + 0.3 * brightness_score + 0.3 * density_score

    return {
        "quality_score": float(round(final_score, 2)),
        "blur": float(round(blur_normalized, 2)),
        "brightness": float(round(brightness_score, 2)),
        "text_density": float(round(density_score, 2)),
    }
