from django.contrib import admin, messages
from django.utils import timezone
from .models import ChatbotConfig, ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "content", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatbotConfig)
class ChatbotConfigAdmin(admin.ModelAdmin):
    list_display = ("__str__", "model", "is_active", "last_prompt_update")
    readonly_fields = ("last_prompt_update", "created_at", "updated_at")
    change_list_template = "admin/chatbot/chatbotconfig/change_list.html"

    fieldsets = (
        ("اتصال به Mimo API", {
            "fields": ("api_key", "api_base_url", "model"),
        }),
        ("تنظیمات پاسخ", {
            "fields": ("temperature", "max_tokens"),
        }),
        ("ظاهر چت", {
            "fields": ("welcome_message", "quick_replies", "is_active"),
        }),
        ("وضعیت", {
            "fields": ("last_prompt_update", "created_at", "updated_at"),
        }),
    )

    def has_add_permission(self, request):
        return not ChatbotConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="🔄 بروزرسانی دانش چت‌بات")
    def refresh_knowledge(self, request, queryset):
        from chatbot.services import clear_prompt_cache, build_system_prompt
        clear_prompt_cache()
        prompt = build_system_prompt()
        cache = ChatbotConfig.get()
        cache.cached_prompt = prompt
        cache.last_prompt_update = timezone.now()
        ChatbotConfig.objects.filter(pk=cache.pk).update(
            cached_prompt=prompt,
            last_prompt_update=cache.last_prompt_update,
        )
        self.message_user(
            request,
            f"دانش چت‌بات بروزرسانی شد ✅ — {len(prompt)} کاراکتر پرامپت بازسازی شد.",
            messages.SUCCESS,
        )

    actions = [refresh_knowledge]


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_key", "user", "message_count", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("session_key", "user__phone_number", "user__full_name")
    readonly_fields = ("session_key", "user", "created_at", "updated_at")
    inlines = [ChatMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "تعداد پیام"

    def has_add_permission(self, request):
        return False


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "content_preview", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content",)
    readonly_fields = ("session", "role", "content", "created_at")

    def content_preview(self, obj):
        return obj.content[:80] + "…" if len(obj.content) > 80 else obj.content
    content_preview.short_description = "متن"

    def has_add_permission(self, request):
        return False
