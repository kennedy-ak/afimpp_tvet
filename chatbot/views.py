import json
import secrets
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import ChatConversation, ChatMessage
from .services import get_chatbot_response, get_conversation_history
from django.contrib.auth import get_user_model

User = get_user_model()


@require_http_methods(["POST"])
@csrf_exempt  # Allow public access without CSRF token for the widget
def chat_api(request):
    """
    API endpoint for chatbot interactions.

    Expects JSON body:
    {
        "message": "user message here",
        "session_id": "optional-session-id"
    }

    Returns JSON:
    {
        "response": "assistant response",
        "session_id": "session-id"
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        session_id = data.get('session_id')

        # Get or create conversation
        if session_id:
            conversation = ChatConversation.objects.filter(session_id=session_id).first()
            if not conversation:
                # Session ID provided but not found - create new
                session_id = secrets.token_urlsafe(32)
                conversation = ChatConversation.objects.create(
                    session_id=session_id,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
        else:
            # Create new conversation
            session_id = secrets.token_urlsafe(32)
            conversation = ChatConversation.objects.create(
                session_id=session_id,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )

        # Link to logged-in user if applicable
        if request.user.is_authenticated and not conversation.user:
            conversation.user = request.user
            conversation.save()

        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )

        # Get conversation history
        conversation_history = get_conversation_history(conversation)

        # Get chatbot response with RAG context
        result = get_chatbot_response(user_message, conversation_history)

        # Save assistant message
        ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['response'],
            context_used=result.get('context')
        )

        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()

        return JsonResponse({
            'response': result['response'],
            'session_id': session_id,
            'usage': result.get('usage', {})
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_client_ip(request):
    """Get the client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
