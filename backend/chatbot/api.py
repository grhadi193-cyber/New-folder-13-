import uuid
from django.contrib.auth.models import AnonymousUser
from ninja import Router, Schema
from typing import Optional

router = Router(tags=["chatbot"])


class ChatRequest(Schema):
    message: str
    session_id: Optional[str] = None
    auth_token: Optional[str] = None


class ChatResponse(Schema):
    reply: str
    session_id: str
    quick_replies: list[str] = []


class ChatbotStatusResponse(Schema):
    is_active: bool
    welcome_message: str
    quick_replies: list[str] = []


def _get_user_from_token(token: str):
    """Resolve user from JWT token."""
    if not token:
        return None
    try:
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import AccessToken
        User = get_user_model()
        decoded = AccessToken(token)
        return User.objects.filter(pk=decoded["user_id"]).first()
    except Exception:
        return None


@router.get("/status", response=ChatbotStatusResponse)
def chatbot_status(request):
    from chatbot.models import ChatbotConfig
    config = ChatbotConfig.get()
    return ChatbotStatusResponse(
        is_active=config.is_active,
        welcome_message=config.welcome_message,
        quick_replies=config.get_quick_replies_list(),
    )


@router.post("/send", response=ChatResponse)
def send_message(request, payload: ChatRequest):
    from chatbot.models import ChatbotConfig, ChatSession, ChatMessage
    from chatbot.services import call_mimo_api, build_user_context

    config = ChatbotConfig.get()

    if not config.is_active:
        return ChatResponse(
            reply="متأسفانه چت‌بات در حال حاضر غیرفعال است. لطفاً بعداً تلاش کنید.",
            session_id=payload.session_id or "",
            quick_replies=[],
        )

    text = payload.message.strip()
    if not text:
        return ChatResponse(
            reply="لطفاً پیام خود را بنویسید.",
            session_id=payload.session_id or "",
            quick_replies=config.get_quick_replies_list(),
        )

    session_id = payload.session_id
    if not session_id:
        session_id = uuid.uuid4().hex[:32]

    user = None
    if payload.auth_token:
        user = _get_user_from_token(payload.auth_token)
    if not user and not isinstance(request.user, AnonymousUser):
        user = request.user

    session, _ = ChatSession.objects.get_or_create(
        session_key=session_id,
        defaults={"user": user},
    )

    if not session.user and user:
        session.user = user
        session.save(update_fields=["user"])

    ChatMessage.objects.create(session=session, role="user", content=text)

    history = list(
        session.messages.order_by("-created_at")[:20].values("role", "content")
    )
    history.reverse()

    user_ctx = build_user_context(user) if user else None

    result = call_mimo_api(history, config=config, user_context=user_ctx)

    ChatMessage.objects.create(session=session, role="assistant", content=result["reply"])

    return ChatResponse(
        reply=result["reply"],
        session_id=session_id,
        quick_replies=config.get_quick_replies_list(),
    )
