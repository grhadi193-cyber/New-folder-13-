import logging
from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone
import requests

logger = logging.getLogger(__name__)

CACHE_KEY = "chatbot_system_prompt"
CACHE_TTL = 60 * 60 * 24  # 24 hours


def build_system_prompt() -> str:
    from store.models import Product, Category
    from core.models import SiteSettings
    from blog.models import Post

    site = SiteSettings.get()

    products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .order_by("category__name", "name")
    )
    categories = Category.objects.filter(is_active=True).order_by("name")

    product_lines = []
    for p in products:
        cat = p.category.name if p.category else "بدون دسته‌بندی"
        price = f"{int(p.price):,} تومان"
        if p.discount_price:
            eff = f"{int(p.discount_price):,} تومان"
            price_info = f"قیمت: {price} | 🔥 تخفیف: {eff}"
        else:
            price_info = f"قیمت: {price}"
        stock = "موجود ✅" if p.stock > 0 else "ناموجود ❌"
        product_lines.append(
            f"- [{cat}] {p.name} — {price_info} | موجودی: {stock} | /products/{p.slug}"
        )

    category_lines = [f"- {c.name}" for c in categories]

    blog_section = ""
    latest_post = (
        Post.objects.filter(is_published=True)
        .order_by("-published_at")
        .first()
    )
    if latest_post:
        excerpt = latest_post.content[:200].replace("\n", " ")
        blog_section = f"\n\nآخرین مقاله وبلاگ:\n- {latest_post.title}\n  {excerpt}…\n  /blog/{latest_post.slug}"

    contact_parts = []
    if site.support_phone:
        contact_parts.append(f"📞 تلفن: {site.support_phone}")
    if site.support_email:
        contact_parts.append(f"📧 ایمیل: {site.support_email}")
    if site.address:
        contact_parts.append(f"📍 آدرس: {site.address}")
    if site.work_hours:
        contact_parts.append(f"🕐 ساعت کاری: {site.work_hours}")
    socials = []
    if site.social_instagram:
        socials.append(f"اینستاگرام: {site.social_instagram}")
    if site.social_telegram:
        socials.append(f"تلگرام: {site.social_telegram}")
    contact_section = "\n".join(contact_parts + socials)

    products_text = "\n".join(product_lines) if product_lines else "محصولی ثبت نشده."
    categories_text = "\n".join(category_lines) if category_lines else "دسته‌بندی ثبت نشده."

    prompt = f"""تو یک دستیار فروش حرفه‌ای و صمیمی برای «{site.site_name}» هستی.
تخصص شما فروش ردیاب‌های GPS و سیستم‌های ردیابی خودرو، ناوگان و اشخاص است.

قوانین رفتاری:
- همیشه به فارسی صحبت کن — گرم، حرفه‌ای و مختصر
- مثل یک فروشنده باتجربه راهنمایی کن: نیاز مشتری را بشناس، محصول مناسب پیشنهاد بده
- اگر محصولی موجود نیست، جایگزین پیشنهاد بده
- برای خرید، مشتری را به صفحه محصول راهنمایی کن
- از ایموجی مناسب استفاده کن (نه زیاد)
- اگر سوال خارج از حوزه فروش بود، مؤدبانه به موضوع برگردان
- قیمت‌ها و موجودی را دقیق از اطلاعات زیر بخوان — هرگز قیمت حدس نزن

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 دسته‌بندی محصولات:
{categories_text}

🛍️ محصولات ({products.count()} عدد):
{products_text}{blog_section}

📞 اطلاعات تماس:
{contact_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

راهنمای مسیرها:
- /products/[slug] → صفحه محصول
- /cart → سبد خرید
- / → صفحه اصلی

پاسخ کوتاه و کاربردی بده. اگر مشتری مردد بود، سوال بپرس تا بهترین پیشنهاد را بدهی."""

    return prompt


def get_system_prompt() -> str:
    prompt = cache.get(CACHE_KEY)
    if prompt:
        return prompt
    prompt = build_system_prompt()
    cache.set(CACHE_KEY, prompt, CACHE_TTL)
    from chatbot.models import ChatbotConfig
    config = ChatbotConfig.get()
    config.cached_prompt = prompt
    config.last_prompt_update = timezone.now()
    ChatbotConfig.objects.filter(pk=config.pk).update(
        cached_prompt=prompt,
        last_prompt_update=config.last_prompt_update,
    )
    return prompt


def clear_prompt_cache():
    cache.delete(CACHE_KEY)


def call_mimo_api(messages: list, config=None) -> dict:
    if config is None:
        config = ChatbotConfig.get()

    if not config.api_key:
        raise ValueError("کلید API میمو تنظیم نشده است. لطفاً از پنل مدیریت کلید API را وارد کنید.")

    system_prompt = get_system_prompt()
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    url = f"{config.api_base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": config.model,
        "messages": full_messages,
        "temperature": float(config.temperature),
        "max_tokens": int(config.max_tokens),
    }

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        assistant_message = data["choices"][0]["message"]["content"]
        return {
            "reply": assistant_message,
            "usage": data.get("usage", {}),
        }
    except requests.exceptions.Timeout:
        logger.error("Mimo API timeout")
        raise ValueError("پاسخ‌گویی سرور بیش از حد طول کشید. لطفاً دوباره تلاش کنید.")
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Mimo API")
        raise ValueError("خطا در اتصال به سرور. لطفاً بعداً تلاش کنید.")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else 0
        body = e.response.text[:500] if e.response else ""
        logger.error("Mimo API HTTP %s: %s", status, body)
        if status == 401:
            raise ValueError("کلید API نامعتبر است.")
        if status == 429:
            raise ValueError("تعداد درخواست‌ها زیاد است. لطفاً کمی صبر کنید.")
        raise ValueError(f"خطای سرور ({status}). لطفاً بعداً تلاش کنید.")
    except (KeyError, IndexError) as e:
        logger.error("Unexpected Mimo response: %s", e)
        raise ValueError("پاسخ غیرمنتظره از سرور. لطفاً دوباره تلاش کنید.")
