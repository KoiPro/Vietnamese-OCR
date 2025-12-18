#  MC-OCR: Vietnamese Receipt OCR System with Tkinter GUI

A complete OCR system for extracting information from Vietnamese receipts captured by mobile devices. Features image quality assessment and key information extraction with a desktop GUI.

##  Features

- **Image Quality Assessment (IQA)**: Analyzes receipt images for OCR suitability
- **Key Information Extraction (KIE)**: Extracts 4 key fields from Vietnamese receipts
- **Desktop GUI**: Built with Tkinter for easy testing
- **Multi-format Support**: JPG, PNG, JPEG formats
- **Real-time Processing**: Instant feedback on image quality and extracted information

##  Extracted Information

The system extracts these 4 key fields from Vietnamese receipts:
1. **SELLER** (Người bán/Công ty)
2. **SELLER ADDRESS** (Địa chỉ)
3. **TIMESTAMP** (Ngày/Thời gian)
4. **TOTAL COST** (Tổng cộng/Tiền)

##  Installation

### Prerequisites
- Python 3.8 or higher
- Tkinter (usually comes with Python)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/mc-ocr-tkinter.git
cd mc-ocr-tkinter
