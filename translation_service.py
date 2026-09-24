"""
Translation & Arabic Proofreading Service Engine
Provides spelling/grammar correction, style enhancement, and dialect conversion.
"""
import re

COMMON_ARABIC_CORRECTIONS = [
    (r'\bإنشاء\s+الله\b', 'إن شاء الله'),
    (r'\bان شاء الله\b', 'إن شاء الله'),
    (r'\bهاذا\b', 'هذا'),
    (r'\bهاذه\b', 'هذه'),
    (r'\bهاكذا\b', 'هكذا'),
    (r'\bلاكن\b', 'لكن'),
    (r'\bاللة\b', 'الله'),
    (r'\bشكراَ\b', 'شكراً'),
    (r'\bمرحباَ\b', 'مرحباً'),
    (r'\bجداَ\b', 'جداً'),
]

DIALECT_DICTIONARIES = {
    "gulf": {
        "أريد": "أبي / أبغى",
        "جداً": "وايد / حيل",
        "الآن": "الحين",
        "ماذا": "شنو / وش",
        "كيف حالك": "شلونك / كيفك",
        "أشاهد": "أطالع",
        "حسناً": "تمام / زين",
        "الكثير من": "وايد من",
        "هنا": "هني / هنا"
    },
    "levantine": {
        "أريد": "بدي",
        "جداً": "كتير",
        "الآن": "هلق / إسه",
        "ماذا": "شو",
        "كيف حالك": "كيفك / شو أخبارك",
        "أشاهد": "عم بتفرج",
        "حسناً": "ماشي / تمام",
        "لماذا": "ليش"
    },
    "egyptian": {
        "أريد": "عايز",
        "جداً": "أوي",
        "الآن": "دلوقتي",
        "ماذا": "إيه",
        "كيف حالك": "إزيك / عامل إيه",
        "أشاهد": "بتفرج",
        "حسناً": "ماشي / تمام",
        "لماذا": "ليه"
    }
}

def proofread_arabic_text(text: str) -> dict:
    refined_text = text
    corrections_made = []
    
    for pattern, replacement in COMMON_ARABIC_CORRECTIONS:
        if re.search(pattern, refined_text):
            refined_text = re.sub(pattern, replacement, refined_text)
            corrections_made.append(f"تصحيح إملائي: استبدال '{pattern}' بـ '{replacement}'")
            
    # Fix spacing around punctuation marks
    refined_text = re.sub(r'\s+([،.؛:؟])', r'\1', refined_text)
    refined_text = re.sub(r'([،.؛:؟])(?=[^\s\d])', r'\1 ', refined_text)
    
    # Word count and readability score
    words = refined_text.split()
    word_count = len(words)
    
    return {
        "original_text": text,
        "refined_text": refined_text,
        "word_count": word_count,
        "corrections_count": len(corrections_made),
        "notes": corrections_made if corrections_made else ["النص سليم وخالٍ من الأخطاء الإملائية الشائعة."]
    }

def convert_to_dialect(text: str, target_dialect: str = "gulf") -> dict:
    target_dialect = target_dialect.lower()
    mapping = DIALECT_DICTIONARIES.get(target_dialect, DIALECT_DICTIONARIES["gulf"])
    
    converted = text
    changes = []
    for fusha, dialectal in mapping.items():
        if fusha in converted:
            choice = dialectal.split(" / ")[0]
            converted = converted.replace(fusha, choice)
            changes.append(f"{fusha} ➔ {choice}")
            
    dialect_names = {
        "gulf": "اللهجة الخليجية (السعودية/الإماراتية)",
        "levantine": "اللهجة الشامية (الأردنية/السورية/اللبنانية)",
        "egyptian": "اللهجة المصرية"
    }
    
    return {
        "target_dialect": dialect_names.get(target_dialect, target_dialect),
        "converted_text": converted,
        "changes_applied": changes
    }
