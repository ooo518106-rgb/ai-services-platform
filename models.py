from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)

class LoginRequest(BaseModel):
    email: str
    password: str

class ProductDescRequest(BaseModel):
    product_name: str
    category: Optional[str] = "عام"
    key_features: Optional[List[str]] = None
    tone: Optional[str] = "persuasive"
    audience: Optional[str] = "الخليج العربي"

class VideoScriptRequest(BaseModel):
    topic: str
    platform: Optional[str] = "TikTok"
    duration: Optional[int] = 30

class AdCopyRequest(BaseModel):
    product: str
    target_audience: Optional[str] = "الشباب والمهتمين بالتقنية"

class ProofreadRequest(BaseModel):
    text: str

class DialectRequest(BaseModel):
    text: str
    target_dialect: Optional[str] = "gulf"

class CleanCsvRequest(BaseModel):
    csv_content: str

class ParseCatalogRequest(BaseModel):
    raw_text: str

class PromoBadgeRequest(BaseModel):
    badge_text: str = "عرض خاص"
    badge_type: Optional[str] = "ribbon"
    color_theme: Optional[str] = "gold"

class StoreCanvasRequest(BaseModel):
    store_name: str = "متجر النخبة"

class CheckoutRequest(BaseModel):
    package_id: str
    gateway: Optional[str] = "tap"

class WebhookSimulationRequest(BaseModel):
    charge_id: str
    user_id: int
    package_id: str
    status: str = "CAPTURED"
