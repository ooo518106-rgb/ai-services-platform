"""
Content & Marketing Service Engine
Generates e-commerce descriptions, viral video scripts, ad copy, and SEO content.
"""
import re

def generate_product_description(product_name: str, category: str = "عام", key_features: list = None, tone: str = "persuasive", audience: str = "الخليج العربي") -> dict:
    features_list = key_features or ["جودة تصنيع عالية", "تصميم عصري وأنيق", "سهولة الاستخدام"]
    features_formatted = "\n".join([f"• {f.strip()}" for f in features_list if f.strip()])
    
    seo_title = f"{product_name} - الخيار المثالي في {category} | تسوق بأفضل سعر"
    
    hook = (
        f"هل تبحث عن التميز والراحة معاً؟ إليك {product_name}، المنتج المصمم خصيصاً ليمنحك تجربة استثنائية تفوق توقعاتك. "
        f"يجمع بين الكفاءة العالية والشكل العصري ليناسب احتياجاتك اليومية بكل احترافية."
    )
    
    why_us = (
        f"لماذا تختار {product_name}؟\n"
        f"لأنه صُمم بعناية فائقة لتلبية تطلعاتك في سوق {audience}، مع ضمان الأداء الفائق والاعتمادية التي تبحث عنها."
    )
    
    cta = "⚡ الكمية محدودة! اطلب الآن واستفد من الشحن السريع والدفع الآمن عند الاستلام."
    
    full_markdown = f"""### {seo_title}

{hook}

#### أبرز المميزات والمواصفات:
{features_formatted}

#### {why_us}

> **{cta}**
"""
    return {
        "title": seo_title,
        "hook": hook,
        "features": features_list,
        "cta": cta,
        "full_markdown": full_markdown
    }

def generate_video_script(topic: str, platform: str = "TikTok", duration: int = 30) -> dict:
    hook_visual = "لقطة سينمائية سريعة، الكاميرا مقربة مع حركة خاطفة للمنتج/الفكرة."
    hook_audio = f"«لو لسا ما جربت هذا الحل، فانت بتضيع على حالك نص المتعة والراحة!»"
    
    body_visual = "استعراض للمشكلة الشائعة التي تواجه العميل، ثم الانتقال فوراً لإظهار كيف يحل {topic} المشكلة بثوانٍ معدودة."
    body_audio = f"كثير منا بعاني من المشاكل اليومية في {topic}، لكن مع هذا الابتكار الموضوع اختلف تماماً؛ سهولة، سرعة، ونتيجة مضمونة من أول استخدام."
    
    cta_visual = "إظهار شاشة المتجر مع كود الخصم وسهم يشير إلى الرابط في البايو."
    cta_audio = "الرابط موجود بالبايو، لا تفوت العرض قبل نفاد الكمية!"
    
    hashtags = f"#{topic.replace(' ', '_')} #ترند #اكسبلور #تيك_توك #عروض_خاصة"
    
    return {
        "platform": platform,
        "duration": f"{duration} ثانية",
        "hook": {"visual": hook_visual, "audio": hook_audio},
        "body": {"visual": body_visual, "audio": body_audio},
        "cta": {"visual": cta_visual, "audio": cta_audio},
        "hashtags": hashtags,
        "script_text": f"""🎬 **سكربت فيديو {platform} ({duration} ثانية)**

⏱ **[00:00 - 00:03] الخطاف (Hook):**
• بصري: {hook_visual}
• صوتي: {hook_audio}

⏱ **[00:03 - 00:20] جسم الفيديو (Body):**
• بصري: {body_visual}
• صوتي: {body_audio}

⏱ **[00:20 - 00:30] الدعوة لاتخاذ إجراء (CTA):**
• بصري: {cta_visual}
• صوتي: {cta_audio}

📌 **الهاشتاغات المقترحة:** {hashtags}"""
    }

def generate_ad_copy(product: str, target_audience: str = "الشباب والمهتمين بالتقنية") -> dict:
    copy_1 = f"🔥 وداعاً للحلول التقليدية! اكتشف {product} الآن واجعل يومك أسهل وأكثر إنتاجية. احصل عليه الآن بخصم إضافي لفترة محدودة! 🚀 الرابط بالأسفل."
    copy_2 = f"💡 هل تبحث عن الجودة الحقيقية؟ {product} هو استثمارك الأمثل للراحة والتوفير. موجه خصيصاً لـ {target_audience}. اطلب اليوم والدفع عند الاستلام! 🛒"
    copy_3 = f"⏱ الوقت من ذهب! لا تضيع وقتك بعد اليوم؛ وفر جهدك مع {product}. اضغط هنا واكتشف كيف غير حياة المئات من عملائنا! ✨"
    
    return {
        "headline": f"أفضل حل لـ {product} في 2026",
        "variants": [
            {"type": "مباشر ومحفز (Direct & Action)", "text": copy_1},
            {"type": "قيمة وضمان (Value & Trust)", "text": copy_2},
            {"type": "استعجال وفضول (Urgency & Curiosity)", "text": copy_3}
        ]
    }
