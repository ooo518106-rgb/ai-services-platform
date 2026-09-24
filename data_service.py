"""
Data & Automation Service Engine
Processes CSV/Excel files, cleans customer records, extracts product catalogs, and prepares structured reports.
"""
import io
import pandas as pd
import re

def clean_csv_records(csv_string: str) -> dict:
    try:
        df = pd.read_csv(io.StringIO(csv_string))
    except Exception as e:
        return {"success": False, "error": f"تعذر قراءة ملف CSV: {str(e)}"}
    
    initial_rows = len(df)
    
    # 1. Strip whitespace from string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # 2. Remove exact duplicates
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    
    # 3. Clean and standardize phone numbers if a phone column exists
    phone_cols = [c for c in df.columns if any(p in c.lower() for p in ['phone', 'mobile', 'هاتف', 'جوال'])]
    for col in phone_cols:
        df[col] = df[col].apply(lambda x: re.sub(r'[^\d+]', '', str(x)))
    
    # 4. Fill NaN values with clean indicators
    df = df.fillna("غير محدد")
    
    cleaned_csv = df.to_csv(index=False)
    
    summary = {
        "total_initial_rows": initial_rows,
        "clean_rows": len(df),
        "duplicates_removed": duplicates_removed,
        "columns": list(df.columns),
        "sample_preview": df.head(5).to_dict(orient="records")
    }
    
    return {
        "success": True,
        "summary": summary,
        "cleaned_csv": cleaned_csv
    }

def parse_unstructured_catalog(raw_text: str) -> dict:
    """
    Parses messy product lists or chat messages into structured e-commerce rows.
    """
    lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]
    items = []
    
    for idx, line in enumerate(lines, 1):
        # Look for price patterns like 100$, 50 ريال, 20 دينار, 150
        price_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ريال|دينار|درهم|\$|usd|jd|sar)?', line, re.IGNORECASE)
        price = price_match.group(1) if price_match else "0.00"
        
        # Clean product title
        clean_name = re.sub(r'[-•*#\d+\.]', '', line)
        clean_name = re.sub(r'(\d+(?:\.\d+)?)\s*(?:ريال|دينار|درهم|\$|usd|jd|sar)?', '', clean_name, flags=re.IGNORECASE).strip()
        if not clean_name:
            clean_name = f"منتج رقم {idx}"
            
        items.append({
            "رقم": idx,
            "اسم المنتج": clean_name,
            "السعر التقديري": price,
            "حالة التوفر": "متوفر",
            "الفئة": "عام"
        })
        
    df = pd.DataFrame(items)
    csv_output = df.to_csv(index=False)
    
    return {
        "success": True,
        "count": len(items),
        "catalog": items,
        "csv_data": csv_output
    }
