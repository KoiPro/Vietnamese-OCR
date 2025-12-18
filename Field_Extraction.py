import re
from pathlib import Path



"""
including English because most receipt use english 
since most machine is from forgein country ¯\_(ツ)_/¯
"""   

def extract_field_in_Vietnamese(ocr_texts):
    seller_keywords = ["CÔNG TY", "NGƯỜI BÁN", " CỬA HÀNG", "NHÀ HÀNG", "SHOP", "RESTAURANT"] 
    address_keywords = ["ĐỊA CHỈ", "ĐC", "Đ/C", "ADDRESS"]
    data_keywords = ["NGÀY", "DATE", "TIME", "THỜI GIAN"]
    total_keywords = ["TỔNG CỘNG", "THÀNH TIỀN", "TOTAL", "AMOUNT", "CỘNG", "TỔNG"]

    fields = {"SELLER:": "", "ADDRESS:": "", "DATE:": "", "TOTAL:": ""}

    for text in ocr_texts:
        text_upper = text.upper() #Convert all keyworld to upper to identify

    #Seller check
        if not fields["SELLER:"] and any(keyword in text_upper for keyword in seller_keywords):
            fields["SELLER:"] = text

    #Address check
        elif not fields["ADDRESS:"] and any(keyword in text_upper for keyword in address_keywords):
            fields["ADDRESS:"] = text

    #Date check
        elif not fields["DATE:"] and any(keyword in text_upper for keyword in data_keywords):
            fields["DATE:"] = text  

    #Total check
        elif not fields["TOTAL:"] and any(keyword in text_upper for keyword in total_keywords   ):
            fields["TOTAL:"] = text

            # Extact currency number
            cost_pattern = r'[\d,.]+(?:\s*VNĐ|\s*đ)' #Patter to recognise currency number
            match = re.search(cost_pattern, text)
            if match:
                fields["TOTAL:"] = match.group()

    return fields

#run test
#run test
if __name__ == "__main__":
    output_file = Path("temp") / "ocr_output.txt"
    
    # Read OCR output and split into lines
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            test_ocr_texts = f.read().splitlines()
    else:
        print(f"OCR output file not found: {output_file}")
        exit(1)
    
    extracted_fields = extract_field_in_Vietnamese(test_ocr_texts)
    for field, value in extracted_fields.items():
        print(f"{field} {value}")
