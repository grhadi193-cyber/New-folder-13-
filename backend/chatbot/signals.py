from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


def _clear_cache(sender, **kwargs):
    from chatbot.services import clear_prompt_cache
    clear_prompt_cache()


def _connect():
    from store.models import Product, Category
    from core.models import SiteSettings

    for model in (Product, Category, SiteSettings):
        post_save.connect(_clear_cache, sender=model, dispatch_uid=f"chatbot_cache_{model.__name__}")
        post_delete.connect(_clear_cache, sender=model, dispatch_uid=f"chatbot_cache_del_{model.__name__}")


_connect()
