from django.urls import path
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.contrib import messages as django_messages
from django.utils import timezone


@staff_member_required
def refresh_knowledge_view(request):
    from chatbot.services import clear_prompt_cache, build_system_prompt
    from chatbot.models import ChatbotConfig

    clear_prompt_cache()
    prompt = build_system_prompt()
    config = ChatbotConfig.get()
    config.cached_prompt = prompt
    config.last_prompt_update = timezone.now()
    ChatbotConfig.objects.filter(pk=config.pk).update(
        cached_prompt=prompt,
        last_prompt_update=config.last_prompt_update,
    )
    django_messages.success(request, f"دانش چت‌بات بروزرسانی شد ✅ ({len(prompt)} کاراکتر)")
    return HttpResponseRedirect("/admin/chatbot/chatbotconfig/")


urlpatterns = [
    path("refresh-knowledge/", refresh_knowledge_view, name="chatbot-refresh-knowledge"),
]
