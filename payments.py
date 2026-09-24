import uuid
from typing import Dict, Any

PACKAGES = {
    "starter": {
        "id": "starter",
        "name": "باقة البداية (Starter)",
        "credits": 30,
        "price_usd": 4.99,
        "description": "مناسبة لتجربة المنصة وتنفيذ أول 10-15 خدمة فورية"
    },
    "growth": {
        "id": "growth",
        "name": "باقة النمو (Growth)",
        "credits": 120,
        "price_usd": 14.99,
        "popular": True,
        "description": "الأكثر طلباً لأصحاب المتاجر الإلكترونية وصناع المحتوى"
    },
    "pro": {
        "id": "pro",
        "name": "باقة المحترفين (Pro)",
        "credits": 350,
        "price_usd": 34.99,
        "description": "للمسوقين والوكالات لإدارة وتوليد خدمات يومية غير محدودة"
    }
}

SERVICE_COSTS = {
    "product_description": 3,
    "video_script": 2,
    "ad_copy": 2,
    "proofread": 1,
    "dialect_convert": 1,
    "clean_csv": 3,
    "parse_catalog": 3,
    "promo_badge": 2,
    "store_canvas": 2
}

def get_packages_list():
    return list(PACKAGES.values())

def create_checkout_session(user_id: int, package_id: str, gateway: str = "tap") -> Dict[str, Any]:
    package = PACKAGES.get(package_id)
    if not package:
        return {"success": False, "error": "الباقة المطلوبة غير متوفرة"}
    charge_id = f"chg_{gateway}_{uuid.uuid4().hex[:12]}"
    return {
        "success": True,
        "charge_id": charge_id,
        "gateway": gateway,
        "amount": package["price_usd"],
        "currency": "USD",
        "credits": package["credits"],
        "package_name": package["name"],
        "message": "تم إنشاء جلسة الدفع بنجاح"
    }
