from django.db import migrations


def seed_chatbot_config(apps, schema_editor):
    ChatbotConfig = apps.get_model("chatbot", "ChatbotConfig")
    ChatbotConfig.objects.get_or_create(
        pk=1,
        defaults={
            "welcome_message": "سلام! 👋 من دستیار فروش آتی فرزام هستم. چطور می‌تونم کمکتون کنم؟",
            "quick_replies": [
                "مشاهده محصولات",
                "راهنمای خرید",
                "استعلام قیمت",
                "تماس با پشتیبانی",
                "پیگیری سفارش",
            ],
            "is_active": True,
            "api_base_url": "https://api.mimo.org/v1",
            "model": "mimo-v2.5-pro",
            "temperature": 0.7,
            "max_tokens": 1024,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_chatbot_config, migrations.RunPython.noop),
    ]
