import os
import uuid
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import (
    init_db, create_user, authenticate_user, get_user_by_id,
    deduct_credits, add_credits, record_task, get_user_tasks, get_user_transactions
)
from models import (
    RegisterRequest, LoginRequest,
    ProductDescRequest, VideoScriptRequest, AdCopyRequest,
    ProofreadRequest, DialectRequest, CleanCsvRequest, ParseCatalogRequest,
    PromoBadgeRequest, StoreCanvasRequest, CheckoutRequest, WebhookSimulationRequest
)
from payments import PACKAGES, SERVICE_COSTS, get_packages_list, create_checkout_session
from content_service import generate_product_description, generate_video_script, generate_ad_copy
from translation_service import proofread_arabic_text, convert_to_dialect
from data_service import clean_csv_records, parse_unstructured_catalog
from image_service import create_promo_badge, create_store_canvas

init_db()

app = FastAPI(
    title="منصة وكيل الخدمات الرقمية بالذكاء الاصطناعي",
    description="منصة متكاملة لتقديم الخدمات الرقمية الأكثر طلباً في السوق العربي بمقابل مالي ونظام نقاط.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "AI Services Platform API is running. Go to /docs for Swagger."}

# ==================== AUTHENTICATION & USER ====================

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    user = create_user(req.email, req.password, req.full_name, initial_credits=20)
    if not user:
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مسجل مسبقاً.")
    return {"success": True, "message": "تم إنشاء الحساب بنجاح وتمت إضافة 20 نقطة ترحيبية!", "user": user}

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="بيانات الدخول غير صحيحة.")
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return {"success": True, "user": safe_user}

@app.get("/api/auth/me")
def get_current_user_info(user_id: int = Query(...)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود.")
    return {"success": True, "user": user}

# ==================== HELPER: EXECUTE WITH CREDITS ====================

def run_service_with_credits(user_id: int, service_key: str, desc: str, input_data: dict, executor_func):
    cost = SERVICE_COSTS.get(service_key, 2)
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود.")
    
    if user["credits_balance"] < cost:
        raise HTTPException(
            status_code=402,
            detail=f"رصيد النقاط غير كافٍ. تحتاج إلى {cost} نقاط ورصيدك الحالي هو {user['credits_balance']} نقطة. يرجى شحن الرصيد للاستمرار."
        )
    
    task_id = f"tsk_{uuid.uuid4().hex[:10]}"
    deducted = deduct_credits(user_id, cost, f"{desc} ({cost} نقاط)", task_id)
    if not deducted:
        raise HTTPException(status_code=400, detail="تعذر خصم النقاط من الرصيد.")
    
    try:
        result = executor_func()
        record_task(task_id, user_id, service_key, cost, input_data, result, status="COMPLETED")
        updated_user = get_user_by_id(user_id)
        return {
            "success": True,
            "task_id": task_id,
            "credits_deducted": cost,
            "remaining_credits": updated_user["credits_balance"],
            "result": result
        }
    except Exception as e:
        add_credits(user_id, cost, f"استرجاع رصيد لفشل العملية: {desc}", task_id)
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء تنفيذ الخدمة: {str(e)}")

# ==================== AI SERVICE ENDPOINTS ====================

@app.post("/api/services/product-description")
def api_product_description(req: ProductDescRequest, user_id: int = Query(...)):
    def execute():
        return generate_product_description(
            product_name=req.product_name,
            category=req.category,
            key_features=req.key_features,
            tone=req.tone,
            audience=req.audience
        )
    return run_service_with_credits(
        user_id, "product_description", f"كتابة وصف لمنتج {req.product_name}", req.dict(), execute
    )

@app.post("/api/services/video-script")
def api_video_script(req: VideoScriptRequest, user_id: int = Query(...)):
    def execute():
        return generate_video_script(
            topic=req.topic,
            platform=req.platform,
            duration=req.duration or 30
        )
    return run_service_with_credits(
        user_id, "video_script", f"توليد سكربت فيديو {req.topic}", req.dict(), execute
    )

@app.post("/api/services/ad-copy")
def api_ad_copy(req: AdCopyRequest, user_id: int = Query(...)):
    def execute():
        return generate_ad_copy(product=req.product, target_audience=req.target_audience)
    return run_service_with_credits(
        user_id, "ad_copy", f"صياغة إعلانات لـ {req.product}", req.dict(), execute
    )

@app.post("/api/services/proofread")
def api_proofread(req: ProofreadRequest, user_id: int = Query(...)):
    def execute():
        return proofread_arabic_text(text=req.text)
    return run_service_with_credits(
        user_id, "proofread", "تدقيق وتحسين نص عربي", req.dict(), execute
    )

@app.post("/api/services/convert-dialect")
def api_convert_dialect(req: DialectRequest, user_id: int = Query(...)):
    def execute():
        return convert_to_dialect(text=req.text, target_dialect=req.target_dialect)
    return run_service_with_credits(
        user_id, "dialect_convert", f"تحويل نص إلى {req.target_dialect}", req.dict(), execute
    )

@app.post("/api/services/clean-csv")
def api_clean_csv(req: CleanCsvRequest, user_id: int = Query(...)):
    def execute():
        return clean_csv_records(csv_string=req.csv_content)
    return run_service_with_credits(
        user_id, "clean_csv", "تنظيف وتنسيق ملف بيانات CSV", {"chars": len(req.csv_content)}, execute
    )

@app.post("/api/services/parse-catalog")
def api_parse_catalog(req: ParseCatalogRequest, user_id: int = Query(...)):
    def execute():
        return parse_unstructured_catalog(raw_text=req.raw_text)
    return run_service_with_credits(
        user_id, "parse_catalog", "استخراج وهيكلة كتالوج منتجات", {"lines": len(req.raw_text.splitlines())}, execute
    )

@app.post("/api/services/promo-badge")
def api_promo_badge(req: PromoBadgeRequest, user_id: int = Query(...)):
    def execute():
        return create_promo_badge(badge_text=req.badge_text, badge_type=req.badge_type, color_theme=req.color_theme)
    return run_service_with_credits(
        user_id, "promo_badge", f"توليد شارة تسويقية {req.badge_text}", req.dict(), execute
    )

@app.post("/api/services/store-canvas")
def api_store_canvas(req: StoreCanvasRequest, user_id: int = Query(...)):
    def execute():
        return create_store_canvas(store_name=req.store_name)
    return run_service_with_credits(
        user_id, "store_canvas", f"إنشاء قالب متجر {req.store_name}", req.dict(), execute
    )

# ==================== PAYMENTS & MONETIZATION ====================

@app.get("/api/payments/packages")
def api_get_packages():
    return {
        "success": True,
        "packages": get_packages_list(),
        "service_costs": SERVICE_COSTS
    }

@app.post("/api/payments/checkout")
def api_create_checkout(req: CheckoutRequest, user_id: int = Query(...)):
    session = create_checkout_session(user_id, req.package_id, req.gateway or "tap")
    if not session.get("success"):
        raise HTTPException(status_code=400, detail=session.get("error", "فشل إنشاء جلسة الدفع"))
    return session

@app.post("/api/payments/webhook")
def api_payment_webhook(req: WebhookSimulationRequest):
    if req.status.upper() in ["CAPTURED", "PAID", "SUCCESS"]:
        pkg = PACKAGES.get(req.package_id)
        if not pkg:
            raise HTTPException(status_code=400, detail="حزمة غير صالحة")
        credits_to_add = pkg["credits"]
        success = add_credits(
            req.user_id,
            credits_to_add,
            f"شحن رصيد - {pkg['name']} (${pkg['price_usd']})",
            reference_id=req.charge_id
        )
        if success:
            updated_user = get_user_by_id(req.user_id)
            return {
                "success": True,
                "message": f"تم استلام الدفعة بنجاح وإضافة {credits_to_add} نقطة إلى الحساب.",
                "new_balance": updated_user["credits_balance"]
            }
    raise HTTPException(status_code=400, detail="فشلت عملية الدفع أو أنها ملغاة")

# ==================== USER ACTIVITY & LOGS ====================

@app.get("/api/user/tasks")
def api_user_tasks(user_id: int = Query(...)):
    tasks = get_user_tasks(user_id)
    return {"success": True, "tasks": tasks}

@app.get("/api/user/transactions")
def api_user_transactions(user_id: int = Query(...)):
    transactions = get_user_transactions(user_id)
    return {"success": True, "transactions": transactions}

# ==================== AI SALES & NEGOTIATION AGENT ====================

SERVICE_PRICING = {
    "product_descriptions": {
        "title": "كتابة أوصاف 20 منتج لمتجرك",
        "base_price": 25,
        "floor_price": 15
    },
    "video_scripts": {
        "title": "سكربتات إعلانات تيك توك وريلز (5 سكربتات)",
        "base_price": 20,
        "floor_price": 12
    },
    "store_badges": {
        "title": "تصميم باقة شارات عروض للمتجر",
        "base_price": 18,
        "floor_price": 10
    },
    "catalog_formatting": {
        "title": "تنظيم وهيكلة كتالوج المنتجات",
        "base_price": 22,
        "floor_price": 14
    },
    "full_store_package": {
        "title": "الباقة الذهبية المتكاملة للمتجر",
        "base_price": 50,
        "floor_price": 35
    }
}

def process_sales_chat(user_message: str, current_state: dict = None) -> dict:
    state = current_state or {
        "greeted": False,
        "stage": "discovery",
        "service": None,
        "current_quote": 0,
        "negotiation_count": 0
    }
    
    msg = user_message.strip()
    msg_lower = msg.lower()

    # 1. إذا سأل الزبون: كم الأسعار / الأسعار
    if any(q in msg_lower for q in ["كم السعر", "كم الاسعار", "الاسعار", "قائمه الاسعار", "بكم", "اسعاركم", "الأسعار", "اسعار"]):
        state["greeted"] = True
        return {
            "success": True,
            "reply": (
                "أسعار خدماتنا التنافسية لمتجرك:\n\n"
                "• كتابة أوصاف تسويقية (20 منتج): $25\n"
                "• سكربتات إعلانات تيك توك وريلز (5 سكربتات): $20\n"
                "• باقة شارات عروض وبنرات للمتجر: $18\n"
                "• تنظيم وهيكلة كتالوج المنتجات: $22\n"
                "• الباقة الشاملة لكل الخدمات: $50\n\n"
                "شو الخدمة اللي بتهمك أكثر لنبدأ فيها ونرتب لك عرضاً مناسباً؟"
            ),
            "state": state,
            "deal_closed": False
        }

    # 2. إذا طلب العميل أوصاف منتجات
    if any(kw in msg_lower for kw in ["وصف", "اوصاف", "منتجات", "منتج"]):
        state["greeted"] = True
        state["service"] = "product_descriptions"
        state["service_title"] = "كتابة أوصاف 20 منتج لمتجرك"
        state["current_quote"] = 25
        state["stage"] = "quoted"
        return {
            "success": True,
            "reply": (
                "أهلاً بك! بخصوص كتابة أوصاف تسويقية احترافية لمنتجات متجرك:\n\n"
                "السعر الأساسي لباقة 20 منتج هو $25 مع صياغة متوافقة مع SEO تزيد المبيعات وتنسيق جاهز لمنصة سلة/زد.\n\n"
                "كم عدد المنتجات التي تحتاج كتابة أوصاف لها بمتجرك؟"
            ),
            "state": state,
            "deal_closed": False
        }

    # 3. إذا فاصل الزبون في السعر (غالي، خصم، راعينا)
    if state.get("current_quote") and any(kw in msg_lower for kw in ["غالي", "خصم", "راعينا", "نزل", "كثير", "كتير", "تخفيض", "غاليه", "غالية"]):
        current = state["current_quote"]
        new_quote = max(15, round(current * 0.8))
        state["current_quote"] = new_quote
        state["stage"] = "negotiating"
        return {
            "success": True,
            "reply": f"ولا يهمك، ما بنختلف معك! نقدر نحسب لك الباقة بـ ${new_quote} فقط بدلاً من ${current}. هل السعر هيك ممتاز لنعتمد ونبدأ؟",
            "state": state,
            "deal_closed": False
        }

    # 4. إذا وافق العميل (تمام، موافق، اعتمد)
    if state.get("current_quote") and any(kw in msg_lower for kw in ["تمام", "موافق", "اعتمد", "يلا", "اوكي", "ماشي"]):
        state["stage"] = "agreed"
        price = state["current_quote"]
        return {
            "success": True,
            "reply": f"ألف مبروك! تم اعتماد طلبك بمبلغ ${price}. سيبدأ النظام بالتنفيذ فوراً عبر رابط منصتنا.",
            "state": state,
            "deal_closed": True,
            "agreed_price": price
        }

    # 5. الترحيب الأولي (يحدث مرة واحدة فقط)
    if not state.get("greeted"):
        state["greeted"] = True
        return {
            "success": True,
            "reply": (
                "أهلاً وسهلاً بك في منصة وكيل الخدمات الذكي! 🤝\n\n"
                "بنقدم خدمات متكاملة لمتاجر سلة وزد: أوصاف منتجات، سكربتات إعلانية، وشارات عروض.\n"
                "شو الخدمة اللي حابب نساعدك فيها لمتجرك؟"
            ),
            "state": state,
            "deal_closed": False
        }

    # 6. رد سياقي ذكي
    return {
        "success": True,
        "reply": "أهلاً بك، وضح لي أكثر الخدمة التي تحتاجها لمتجرك لأعطيك التكلفة الدقيقة.",
        "state": state,
        "deal_closed": False
    }

from pydantic import BaseModel

class SalesChatRequest(BaseModel):
    message: str
    state: dict = None

@app.post("/api/chat/sales")
def api_sales_chat(req: SalesChatRequest):
    return process_sales_chat(req.message, req.state)

# ==================== WHATSAPP WEBHOOK (GREEN-API) ====================

whatsapp_sessions = {}

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        print("JSON parse error in webhook:", e)
        return {"status": "error", "message": "Invalid JSON"}
        
    type_webhook = body.get("typeWebhook")
    print(f"--> Received Webhook event: {type_webhook}")
    
    if type_webhook == "incomingMessageReceived":
        message_data = body.get("messageData", {})
        type_message = message_data.get("typeMessage")
        
        text = ""
        if type_message == "textMessage":
            text = message_data.get("textMessageData", {}).get("textMessage", "").strip()
        elif type_message == "extendedTextMessage":
            text = message_data.get("extendedTextMessageData", {}).get("text", "").strip()
        else:
            text = (
                message_data.get("textMessageData", {}).get("textMessage") or
                message_data.get("extendedTextMessageData", {}).get("text") or
                ""
            ).strip()
            
        sender_data = body.get("senderData", {})
        chat_id = sender_data.get("chatId")
        sender_name = sender_data.get("senderName", "")
        
        print(f"📩 WhatsApp Message: type={type_message} | chat_id={chat_id} | text='{text}'")
        
        if text and chat_id:
            user_state = whatsapp_sessions.get(chat_id)
            res = process_sales_chat(text, user_state)
            whatsapp_sessions[chat_id] = res["state"]
            
            reply_text = res["reply"].replace("**", "")
            if res.get("deal_closed"):
                reply_text += "\n\n🔗 رابط منصتنا لتأكيد طلبك والدفع الآمن:\nhttps://ai-services-platform.onrender.com"
                
            id_instance = os.getenv("GREEN_API_ID", "").strip()
            api_token = os.getenv("GREEN_API_TOKEN", "").strip()
            
            print(f"🔑 Using GREEN_API_ID: '{id_instance}', Token present: {bool(api_token)}")
            
            if not id_instance or not api_token:
                print("❌ ERROR: GREEN_API_ID or GREEN_API_TOKEN is missing in Environment Variables!")
                return {"status": "error", "message": "Missing Green API credentials"}
                
            import requests
            
            host_prefix = id_instance[:4] if len(id_instance) >= 4 else "api"
            endpoints = [
                f"https://{host_prefix}.api.green-api.com/waInstance{id_instance}/sendMessage/{api_token}",
                f"https://api.green-api.com/waInstance{id_instance}/sendMessage/{api_token}"
            ]
            
            sent_success = False
            for send_url in endpoints:
                try:
                    payload = {"chatId": chat_id, "message": reply_text}
                    print(f"🚀 Sending reply to {send_url} ...")
                    r = requests.post(send_url, json=payload, timeout=12)
                    print(f"📬 Green-API Response [{r.status_code}]: {r.text}")
                    if r.status_code == 200:
                        sent_success = True
                        break
                except Exception as ex:
                    print(f"⚠️ Failed calling {send_url}: {ex}")
                    
            if not sent_success:
                print("❌ All Green-API send attempts failed.")
                
    return {"status": "ok"}
