# mcorr_pipeline.py

from paddleocr import PaddleOCR
from PIL import Image
from pathlib import Path
import Basic_OCR_Pipeline
import IQA_Check
import Field_Extraction


class MCORRSystem:
    def __init__(self):
        self.ocr = PaddleOCR(lang='vi')

    def process_receipt(self, image_path, ocr_engine='auto'):
        """Complete pipeline: IQA + KIE"""

        # 1. Quality Assessment (headless)
        quality = IQA_Check.simple_quality_score(image_path)

        # 2. Only extract if quality is reasonable
        if quality["quality_score"] > 0.3:
            # Ensure PaddleOCR-compatible path (convert WebP to JPG if necessary)
            img_path_obj = Path(image_path)
            converted = None
            if img_path_obj.suffix.lower() == ".webp":
                out_dir = Path("temp")
                out_dir.mkdir(parents=True, exist_ok=True)
                converted = out_dir / (img_path_obj.stem + ".jpg")
                try:
                    Image.open(image_path).convert("RGB").save(converted, "JPEG")
                    use_path = str(converted)
                except Exception:
                    use_path = image_path
            else:
                use_path = image_path

            # OCR extraction (engine selection)
            texts = []
            ocr_result = None
            # Option: pytesseract_first -> try pytesseract before Paddle
            if ocr_engine == 'pytesseract_first':
                try:
                    pytess_texts = Basic_OCR_Pipeline.ocr_with_pytesseract(use_path)
                    texts = [{'text': t, 'conf': None} for t in pytess_texts]
                except Exception:
                    texts = []

            # If no texts yet and Paddle allowed, run PaddleOCR
            if (ocr_engine in ('auto', 'paddle') and not texts) or ocr_engine == 'auto':
                try:
                    ocr_result = self.ocr.ocr(use_path)
                except TypeError:
                    ocr_result = self.ocr.predict(use_path)

                # Safe parse of PaddleOCR results into dicts
                try:
                    blocks = ocr_result[0] if isinstance(ocr_result, (list, tuple)) and len(ocr_result) > 0 else ocr_result
                    for line in blocks:
                        if isinstance(line, (list, tuple)) and len(line) >= 2:
                            candidate = line[1]
                            if isinstance(candidate, (list, tuple)) and len(candidate) >= 2:
                                texts.append({'text': candidate[0], 'conf': candidate[1]})
                            elif isinstance(candidate, str):
                                texts.append({'text': candidate, 'conf': None})
                except Exception:
                    # fallback: flatten simple string outputs
                    if isinstance(ocr_result, (list, tuple)):
                        for item in ocr_result:
                            if isinstance(item, str):
                                texts.append({'text': item, 'conf': None})

            # If still no texts and pytesseract is allowed/fallback, use it
            if (not texts) and ocr_engine in ('auto', 'pytesseract'):
                try:
                    pytess_texts = Basic_OCR_Pipeline.ocr_with_pytesseract(use_path)
                    texts = [{'text': t, 'conf': None} for t in pytess_texts]
                except Exception:
                    pass

            # Field extraction
            texts_only = [t['text'] if isinstance(t, dict) and 'text' in t else (t[0] if isinstance(t, (list, tuple)) else str(t)) for t in texts]
            fields = Field_Extraction.extract_field_in_Vietnamese(texts_only)

            return {
                "quality_assessment": quality,
                "fields_extracted": fields,
                "raw_text": texts,
            }
        else:
            return {
                "quality_assessment": quality,
                "fields_extracted": {},
                "raw_text": [],
                "error": "Image quality too low for extraction",
            }

    def batch_process(self, image_paths):
        """Process multiple receipts"""
        results = {}
        for img_path in image_paths:
            results[img_path] = self.process_receipt(img_path)
        return results


if __name__ == "__main__":
    system = MCORRSystem()
    sample = Path("data") / "receipt_form_vietnam.webp"
    if not sample.exists():
        print(f"Sample image not found: {sample}. Provide a valid image path.")
    else:
        result = system.process_receipt(str(sample))
        print(result)
