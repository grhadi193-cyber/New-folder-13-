from decimal import Decimal
from typing import Generic, List, Optional, TypeVar
from datetime import datetime
from pydantic import BaseModel, computed_field, ConfigDict, field_validator


# ── Generic Paginated Response ─────────────────────────────────────────────

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """پاسخ صفحه‌بندی‌شده عمومی — قابل استفاده برای هر نوع داده."""
    count: int
    page: int
    page_size: int
    total_pages: int
    results: List[T]


# ── Category ─────────────────────────────────────────────────────────────────

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


# ── Product Images ────────────────────────────────────────────────────────────

class ProductImageOut(BaseModel):
    id: int
    image: str
    alt_text: str
    order: int
    is_cover: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator('image', mode='before')
    @classmethod
    def convert_image_to_str(cls, v):
        if v is None or v == '':
            return ''
        if hasattr(v, 'url'):
            return v.url
        return str(v)


# ── Product List (public) ─────────────────────────────────────────────────────

class ProductListOut(BaseModel):
    id: int
    name: str
    slug: str
    price: Decimal
    discount_price: Optional[Decimal] = None
    weight: Decimal = Decimal("0")
    length: Decimal = Decimal("0")
    width: Decimal = Decimal("0")
    height: Decimal = Decimal("0")
    stock: int
    image: Optional[str] = None
    category: Optional[CategoryOut] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('image', mode='before')
    @classmethod
    def convert_image_to_str(cls, v):
        if v is None or v == '':
            return None
        if hasattr(v, 'url'):
            return v.url
        return str(v)

    @computed_field
    @property
    def effective_price(self) -> Decimal:
        return self.discount_price if self.discount_price is not None else self.price

    @computed_field
    @property
    def is_on_sale(self) -> bool:
        return self.discount_price is not None and self.discount_price < self.price

    @computed_field
    @property
    def volumetric_weight(self) -> float:
        if self.length and self.width and self.height:
            return float(self.length * self.width * self.height) / 5000.0
        return 0.0

    @computed_field
    @property
    def effective_shipping_weight(self) -> float:
        return max(float(self.weight), self.volumetric_weight)


# ── Product Detail (public) ───────────────────────────────────────────────────

class ProductFeatureOut(BaseModel):
    text: str

    model_config = ConfigDict(from_attributes=True)


class ProductSpecificationOut(BaseModel):
    key: str
    value: str

    model_config = ConfigDict(from_attributes=True)


class ProductFAQOut(BaseModel):
    question: str
    answer: str

    model_config = ConfigDict(from_attributes=True)


class ProductReviewOut(BaseModel):
    name: str
    rating: int
    text: str
    date: str

    model_config = ConfigDict(from_attributes=True)


class ProductDetailOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: Decimal
    discount_price: Optional[Decimal] = None
    sku: Optional[str] = None
    meta_title: str = ""
    meta_description: str = ""
    view_count: int = 0
    stock: int
    weight: Decimal
    length: Decimal = Decimal("0")
    width: Decimal = Decimal("0")
    height: Decimal = Decimal("0")
    image: Optional[str] = None
    category: Optional[CategoryOut] = None
    images: List[ProductImageOut] = []
    features: List[ProductFeatureOut] = []
    specifications: List[ProductSpecificationOut] = []
    faqs: List[ProductFAQOut] = []
    reviews: List[ProductReviewOut] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator('image', mode='before')
    @classmethod
    def convert_image_to_str(cls, v):
        if v is None or v == '':
            return None
        if hasattr(v, 'url'):
            return v.url
        return str(v)

    @field_validator('images', mode='before')
    @classmethod
    def convert_images_to_list(cls, v):
        if hasattr(v, 'all'):
            return list(v.all())
        return v if isinstance(v, list) else []

    @field_validator('features', mode='before')
    @classmethod
    def convert_features_to_list(cls, v):
        if hasattr(v, 'all'):
            return list(v.all())
        return v if isinstance(v, list) else []

    @field_validator('specifications', mode='before')
    @classmethod
    def convert_specifications_to_list(cls, v):
        if hasattr(v, 'all'):
            return list(v.all())
        return v if isinstance(v, list) else []

    @field_validator('faqs', mode='before')
    @classmethod
    def convert_faqs_to_list(cls, v):
        if hasattr(v, 'all'):
            return list(v.all())
        return v if isinstance(v, list) else []

    @field_validator('reviews', mode='before')
    @classmethod
    def convert_reviews_to_list(cls, v):
        if hasattr(v, 'all'):
            return [
                ProductReviewOut(
                    name=r.user.full_name or r.user.phone_number or "کاربر",
                    rating=r.rating,
                    text=r.text,
                    date=r.created_at.strftime("%Y/%m/%d"),
                )
                for r in v.all() if r.is_approved
            ]
        return v if isinstance(v, list) else []

    @computed_field
    @property
    def rating(self) -> float:
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @computed_field
    @property
    def review_count(self) -> int:
        return len(self.reviews)

    @computed_field
    @property
    def effective_price(self) -> Decimal:
        return self.discount_price if self.discount_price is not None else self.price

    @computed_field
    @property
    def is_on_sale(self) -> bool:
        return self.discount_price is not None and self.discount_price < self.price

    @computed_field
    @property
    def volumetric_weight(self) -> float:
        if self.length and self.width and self.height:
            return float(self.length * self.width * self.height) / 5000.0
        return 0.0

    @computed_field
    @property
    def effective_shipping_weight(self) -> float:
        return max(float(self.weight), self.volumetric_weight)


# ── Order (Create) ────────────────────────────────────────────────────────────

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int


class CreateOrderIn(BaseModel):
    address_id: int
    shipping_method_id: int
    items: List[OrderItemIn]
    idempotency_key: str = ""


# ── Order (Response) ──────────────────────────────────────────────────────────

_STATUS_DISPLAY_MAP = {
    "pending":    "درحال تایید",
    "paid":       "تایید شده",
    "processing": "آماده سازی",
    "shipped":    "تحویل به پست",
    "delivered":  "تحویل شده",
    "cancelled":  "لغو شده",
}


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: int
    status: str
    total_price: Decimal
    shipping_cost: Decimal
    tracking_number: str = ""
    payment_url: Optional[str] = None
    items: List[OrderItemOut] = []

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def status_display(self) -> str:
        """نام فارسی وضعیت سفارش — از روی مقدار status محاسبه می‌شود."""
        return _STATUS_DISPLAY_MAP.get(self.status, self.status)


# ── Order Tracking ────────────────────────────────────────────────────────────

# نگه‌داشته می‌شود برای سازگاری با بقیه کدهای موجود
STATUS_DISPLAY = _STATUS_DISPLAY_MAP


class OrderItemTrackingOut(BaseModel):
    product_name: str
    quantity: int
    unit_price: Decimal


class OrderStatusHistoryOut(BaseModel):
    status: str
    status_display: str
    note: str
    created_at: datetime


class UserOrderOut(BaseModel):
    id: int
    tracking_number: str
    postal_tracking: str
    carrier_name: str
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    customer_notes: str
    status: str
    status_display: str
    total_price: Decimal
    shipping_cost: Decimal
    created_at: datetime
    shipping_address_snapshot: Optional[dict] = None
    items: List[OrderItemTrackingOut]
    history: List[OrderStatusHistoryOut] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        items = [
            OrderItemTrackingOut(
                product_name=i.product_name_snapshot or i.product.name,
                quantity=i.quantity,
                unit_price=i.unit_price,
            )
            for i in obj.items.all()
        ]
        history = [
            OrderStatusHistoryOut(
                status=h.status,
                status_display=_STATUS_DISPLAY_MAP.get(h.status, h.status),
                note=h.note,
                created_at=h.created_at,
            )
            for h in obj.history.all()
        ]
        return cls(
            id=obj.pk,
            tracking_number=obj.tracking_number,
            postal_tracking=obj.postal_tracking,
            carrier_name=obj.carrier_name,
            shipped_at=obj.shipped_at,
            delivered_at=obj.delivered_at,
            customer_notes=obj.customer_notes,
            status=obj.status,
            status_display=_STATUS_DISPLAY_MAP.get(obj.status, obj.status),
            total_price=obj.total_price,
            shipping_cost=obj.shipping_cost,
            created_at=obj.created_at,
            shipping_address_snapshot=obj.shipping_address_snapshot,
            items=items,
            history=history,
        )