import uuid
from django.contrib.auth.models import AnonymousUser
from ninja import Router, Schema
from typing import Optional

router = Router(tags=["chatbot"])


class ChatRequest(Schema):
    message: str
    session_id: Optional[str] = None


class ChatResponse(Schema):
    reply: str
    session_id: str
    quick_replies: list[str] = []


class ChatbotStatusResponse(Schema):
    is_active: bool
    welcome_message: str
    quick_replies: list[str] = []


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
    from chatbot.services import call_mimo_api

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

    session, _ = ChatSession.objects.get_or_create(
        session_key=session_id,
        defaults={"user": request.user if not isinstance(request.user, AnonymousUser) else None},
    )

    if not session.user and not isinstance(request.user, AnonymousUser):
        session.user = request.user
        session.save(update_fields=["user"])

    ChatMessage.objects.create(session=session, role="user", content=text)

    history = list(
        session.messages.order_by("-created_at")[:20].values("role", "content")
    )
    history.reverse()

    result = call_mimo_api(history, config=config)

    ChatMessage.objects.create(session=session, role="assistant", content=result["reply"])

    return ChatResponse(
        reply=result["reply"],
        session_id=session_id,
        quick_replies=config.get_quick_replies_list(),
    )
