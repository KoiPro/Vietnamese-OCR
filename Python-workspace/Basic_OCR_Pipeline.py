
from pathlib import Path
import sys


def ocr_with_paddle(image_path):
    try:
        from paddleocr import PaddleOCR
    except Exception as e:
        raise ImportError("paddleocr not available: " + str(e))

   # Setting up OCR engine
    try:
        ocr_engine = PaddleOCR(lang='vi')
    except Exception:
        # fallback to default constructor without args
        ocr_engine = PaddleOCR()

    try:
        result = ocr_engine.ocr(str(image_path))
    except TypeError:
        # older/newer APIs may use `predict`
        result = ocr_engine.predict(str(image_path))

    texts = []
    if not result:
        return texts

    # result can be nested lists so it need to extract new string each loop
    for item in result:
        if isinstance(item, list):
            for sub in item:
                if isinstance(sub, (list, tuple)) and len(sub) >= 2:
                    candidate = sub[1]
                    if isinstance(candidate, (list, tuple)) and len(candidate) > 0:
                        texts.append(candidate[0])
                    elif isinstance(candidate, str):
                        texts.append(candidate)
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            candidate = item[1]
            if isinstance(candidate, (list, tuple)) and len(candidate) > 0:
                texts.append(candidate[0])
            elif isinstance(candidate, str):
                texts.append(candidate)

    return texts

# Setting up Pytesseract for backup
def ocr_with_pytesseract(image_path):
    try:
        import pytesseract
        from PIL import Image
    except Exception as e:
        raise ImportError("pytesseract or Pillow not available: " + str(e))

    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    # split into non-empty lines
    return [line.strip() for line in text.splitlines() if line.strip()]


def run(image_path=None):
    default = Path("data") / "receipt_form_vietnam.webp"  # Image path was inserted here for testing
    image_path = Path(image_path) if image_path else default
    if not image_path.exists():
        print(f"Image not found: {image_path}")
        return 1

    print(f"Using image: {image_path}")

    # Try Paddle first, then pytesseract
    texts = None
    try:
        print("Trying PaddleOCR...")
        texts = ocr_with_paddle(image_path)
        print(f"PaddleOCR extracted {len(texts)} text items")
    except Exception as e:
        print("PaddleOCR not usable:", e)

    if not texts:
        try:
            print("Trying pytesseract fallback...")
            texts = ocr_with_pytesseract(image_path)
            print(f"pytesseract extracted {len(texts)} text items")
        except Exception as e:
            print("pytesseract fallback failed:", e)

    if not texts:
        print("No OCR result available. Install paddleocr (and paddlepaddle) or pytesseract + tesseract.")
        return 2

    # Print and save results
    out_text = "\n".join(texts)
    print("--- OCR RESULTS ---")
    print(out_text)

    out_dir = Path("temp")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "ocr_output.txt"
    out_file.write_text(out_text, encoding="utf-8")
    print(f"Saved OCR text to: {out_file}")
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    raise SystemExit(run(arg))

