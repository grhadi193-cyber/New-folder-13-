from typing import Optional, List

from ninja import Router
from pydantic import BaseModel

router = Router(tags=["core"])


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────

class SiteSettingsOut(BaseModel):
    site_name:        str
    banner_text:      str
    announcement:     str
    primary_color:    str
    maintenance_mode: bool
    shop_enabled:     bool
    max_order_quantity: int = 20
    social_instagram: str
    social_telegram:  str
    support_phone:    str
    support_email:    str = ""
    address:          str = ""
    work_hours:       str = ""
    logo:             Optional[str] = None
    hero_title:       str = ""
    hero_text:        str = ""
    hero_banner:      Optional[str] = None
    hero_bg_image:    Optional[str] = None
    about_us:         str = ""
    google_play_url:  str = ""
    app_store_url:    str = ""
    software_login_url: str = ""
    software_description: str = ""
    about_image:         Optional[str] = None
    software_image:      Optional[str] = None
    app_image:           Optional[str] = None
    why_us_icon_1:       Optional[str] = None
    why_us_icon_2:       Optional[str] = None
    why_us_icon_3:       Optional[str] = None
    category_image_1:    Optional[str] = None
    category_image_2:    Optional[str] = None
    category_image_3:    Optional[str] = None
    category_image_4:    Optional[str] = None
    testimonial_bg:      Optional[str] = None
    newsletter_bg:       Optional[str] = None
    otp_test_mode:       bool = False

    model_config = {"from_attributes": True}


class BannerOut(BaseModel):
    id:       int
    title:    str
    subtitle: str = ""
    image:    Optional[str] = None
    link:     str = ""
    cta_text: str = ""
    cta_link: str = ""
    cta2_text: str = ""
    cta2_link: str = ""

    model_config = {"from_attributes": True}


class PartnerOut(BaseModel):
    id:    int
    name:  str
    logo:  Optional[str] = None
    website: str = ""

    model_config = {"from_attributes": True}


class PageOut(BaseModel):
    id:      int
    title:   str
    slug:    str
    content: str = ""

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/settings", response=SiteSettingsOut, summary="تنظیمات عمومی سایت")
def get_site_settings(request):
    from core.models import SiteSettings
    s = SiteSettings.get()

    def _url(field):
        if field and hasattr(field, "url"):
            try:
                return request.build_absolute_uri(field.url)
            except Exception:
                return None
        return None

    return SiteSettingsOut(
        site_name        = s.site_name,
        banner_text      = s.banner_text,
        announcement     = s.announcement,
        primary_color    = s.primary_color,
        maintenance_mode = s.maintenance_mode,
        shop_enabled     = s.shop_enabled,
        max_order_quantity = s.max_order_quantity,
        social_instagram = s.social_instagram,
        social_telegram  = s.social_telegram,
        support_phone    = s.support_phone,
        support_email    = s.support_email,
        address          = s.address,
        work_hours       = s.work_hours,
        logo             = _url(s.logo),
        hero_title       = s.hero_title,
        hero_text        = s.hero_text,
        hero_banner      = _url(s.hero_banner),
        hero_bg_image    = _url(s.hero_bg_image),
        about_us         = s.about_us,
        google_play_url  = s.google_play_url,
        app_store_url    = s.app_store_url,
        software_login_url = s.software_login_url,
        software_description = s.software_description,
        about_image         = _url(s.about_image),
        software_image      = _url(s.software_image),
        app_image           = _url(s.app_image),
        why_us_icon_1       = _url(s.why_us_icon_1),
        why_us_icon_2       = _url(s.why_us_icon_2),
        why_us_icon_3       = _url(s.why_us_icon_3),
        category_image_1    = _url(s.category_image_1),
        category_image_2    = _url(s.category_image_2),
        category_image_3    = _url(s.category_image_3),
        category_image_4    = _url(s.category_image_4),
        testimonial_bg      = _url(s.testimonial_bg),
        newsletter_bg       = _url(s.newsletter_bg),
        otp_test_mode       = s.otp_test_mode,
    )


@router.get("/banners", response=List[BannerOut], summary="لیست بنرها")
def list_banners(request):
    from core.models import Banner
    banners = Banner.objects.filter(is_active=True)

    def _url(field):
        if field and hasattr(field, "url"):
            try:
                return request.build_absolute_uri(field.url)
            except Exception:
                return None
        return None

    return [
        BannerOut(
            id=b.pk, title=b.title, subtitle=b.subtitle,
            image=_url(b.image), link=b.link,
            cta_text=b.cta_text, cta_link=b.cta_link,
            cta2_text=b.cta2_text, cta2_link=b.cta2_link,
        )
        for b in banners
    ]


@router.get("/partners", response=List[PartnerOut], summary="لیست شرکا")
def list_partners(request):
    from core.models import Partner
    partners = Partner.objects.filter(is_active=True)

    def _url(field):
        if field and hasattr(field, "url"):
            try:
                return request.build_absolute_uri(field.url)
            except Exception:
                return None
        return None

    return [
        PartnerOut(id=p.pk, name=p.name, logo=_url(p.logo), website=p.website)
        for p in partners
    ]


@router.get("/pages/{slug}", response=PageOut, summary="دریافت صفحه بر اساس slug")
def get_page(request, slug: str):
    from core.models import Page
    from django.http import JsonResponse
    try:
        page = Page.objects.get(slug=slug, is_active=True)
        return PageOut(id=page.pk, title=page.title, slug=page.slug, content=page.content)
    except Page.DoesNotExist:
        return JsonResponse({"error": "not_found"}, status=404)


# ── Contact Form ─────────────────────────────────────────────────────────────

class ContactIn(BaseModel):
    name:    str
    phone:   str
    message: str


class ContactOut(BaseModel):
    detail: str


@router.post("/contact", response=ContactOut, auth=None, summary="ارسال پیام تماس")
def submit_contact(request, payload: ContactIn):
    from core.models import ContactMessage
    from django.http import JsonResponse

    if len(payload.name) < 2:
        return JsonResponse({"error": True, "message": "نام حداقل ۲ کاراکتر باشد"}, status=400)
    if len(payload.phone) < 10:
        return JsonResponse({"error": True, "message": "شماره موبایل نامعتبر است"}, status=400)
    if len(payload.message) < 10:
        return JsonResponse({"error": True, "message": "پیام حداقل ۱۰ کاراکتر باشد"}, status=400)

    ContactMessage.objects.create(
        name=payload.name,
        phone=payload.phone,
        message=payload.message,
    )
    return ContactOut(detail="پیام شما با موفقیت ارسال شد")
