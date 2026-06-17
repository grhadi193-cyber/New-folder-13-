from datetime import datetime
from typing import Optional

from ninja import Schema


class PostListOut(Schema):
    id: int
    title: str
    slug: str
    featured_image: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @staticmethod
    def resolve_featured_image(obj) -> Optional[str]:
        if obj.featured_image:
            return obj.featured_image.url
        return None

    @staticmethod
    def resolve_summary(obj) -> Optional[str]:
        if obj.content:
            import re
            text = re.sub(r'<[^>]+>', '', obj.content)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:200] + ('...' if len(text) > 200 else '')
        return None


class PostDetailOut(Schema):
    id: int
    title: str
    slug: str
    content: str
    featured_image: Optional[str] = None
    published_at: Optional[datetime] = None
    is_published: bool
    created_at: datetime

    @staticmethod
    def resolve_featured_image(obj) -> Optional[str]:
        if obj.featured_image:
            return obj.featured_image.url
        return None
