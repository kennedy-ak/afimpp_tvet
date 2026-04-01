from django.conf import settings
from openai import OpenAI
from courses.models import Course, CourseModule
import re


def get_relevant_context(user_query, limit=5):
    """
    Retrieve relevant course information based on the user's query.
    Uses keyword matching and basic relevance scoring.
    """
    query_lower = user_query.lower()
    courses = Course.objects.filter(is_active=True)

    # Score each course based on relevance to the query
    scored_courses = []
    for course in courses:
        score = 0

        # Check for level mentions (Level 3, Level 4, Level 5)
        if f"level {course.level}" in query_lower or f"level{course.level}" in query_lower:
            score += 10

        # Check for course title matches
        if course.title.lower() in query_lower:
            score += 15

        # Check for partial title matches
        title_words = course.title.lower().split()
        for word in title_words:
            if len(word) > 3 and word in query_lower:
                score += 3

        # Check description matches
        desc_words = course.description.lower().split()
        for word in desc_words[:50]:  # Check first 50 words
            if len(word) > 4 and word in query_lower:
                score += 1

        # Check for keywords related to mining/fields
        keywords = ['mining', 'engineering', 'system', 'hnd', 'certificate', 'diploma', 'professional']
        for keyword in keywords:
            if keyword in query_lower and keyword in course.title.lower():
                score += 5

        # Check for price/cost questions
        if any(word in query_lower for word in ['price', 'cost', 'fee', 'much', 'afford']):
            score += 2

        # Check for duration questions
        if any(word in query_lower for word in ['long', 'duration', 'month', 'year']):
            score += 2

        if score > 0:
            scored_courses.append((course, score))

    # Sort by score descending and take top results
    scored_courses.sort(key=lambda x: x[1], reverse=True)
    top_courses = [course for course, score in scored_courses[:limit]]

    if not top_courses:
        # If no specific matches, return active courses as general context
        top_courses = list(courses[:3])

    # Format context for the AI
    context = {
        'courses': [],
        'total_count': courses.count(),
    }

    for course in top_courses:
        modules = list(course.modules.all()[:5])  # Get first 5 modules

        course_data = {
            'title': course.title,
            'slug': course.slug,
            'level': course.get_level_display(),
            'description': course.description,
            'duration_months': course.duration_months,
            'price': float(course.price),
            'requirements': course.requirements or 'Not specified',
            'learning_mode': course.learning_mode,
            'overview': course.overview or course.description,
            'modules': [{'title': m.title, 'description': m.description} for m in modules]
        }
        context['courses'].append(course_data)

    return context


def build_system_prompt(context):
    """Build the system prompt with course context"""
    courses_info = ""
    for course in context['courses']:
        courses_info += f"""
Course: {course['title']} (Level: {course['level']})
- Description: {course['description']}
- Duration: {course['duration_months']} months
- Price: GHS {course['price']}
- Requirements: {course['requirements']}
- Learning Mode: {course['learning_mode']}
"""

        if course['modules']:
            courses_info += f"- Modules: {', '.join(m['title'] for m in course['modules'])}\n"

    prompt = f"""You are a helpful AI assistant for AfIMMP (African Institute for Mining and Mineral Processing) Technical and Vocational Training Center.

Your role is to help prospective students learn about courses, enrollment procedures, and general information about the institute.

KEY INFORMATION ABOUT AVAILABLE COURSES:
{courses_info}

GENERAL INFORMATION:
- AfIMMP offers technical and vocational training in mining and mineral processing
- Course levels: Level 3 (Foundation), Level 4 (Intermediate), Level 5 (Advanced)
- Students must have a registration code to enroll
- Phone: +233 55 778 2728
- Email: info@afimpp.institute
- Location: Tarkwa, Ghana (WT-0661-1059, UNN Building, Adjacent EC)
- Website: www.afimpp.institute

ENROLLMENT PROCESS:
1. Express interest and get a registration code
2. Create an account with the registration code
3. Browse and select a course
4. Complete the registration form with personal details and documents
5. Make payment
6. Wait for admin approval

PAYMENT METHODS:
For course payments and membership fees, AfIMMP accepts two payment options:

1. BANK TRANSFER (GCB Bank):
   - Account Name: AFRICAN INSTITUTION OF MINING PROFESSIONALS AND PRACTITIONERS LTD
   - Account No: 4051130002466
   - Branch Name: TARKWA
   - Swift Code: GHCBGHAC
   - Bank Code: 040

2. MOBILE MONEY (MoMo):
   - MoMo Number: 0530531381
   - Account Name: African Institution of Mining Professionals and Practitioners
   - Merchant ID: 076923

GUIDELINES:
- Be friendly, professional, and helpful
- Provide specific course details when asked
- If you don't know something specific, direct them to contact info@afimpp.institute or call +233 55 778 2728
- Keep responses concise but informative
- For detailed course information, recommend visiting the course page at www.afimpp.institute
- Prices are in Ghanaian Cedis (GHS)
- Always mention the exact course title when discussing courses

If someone asks about courses not listed above, acknowledge that we offer various programs and suggest they contact us directly at info@afimpp.institute or call +233 55 778 2728 for the most current information.
"""
    return prompt


def get_chatbot_response(user_query, conversation_history=None):
    """
    Get a response from OpenAI's API with RAG context.

    Args:
        user_query: The user's message
        conversation_history: List of previous messages as dicts with 'role' and 'content'

    Returns:
        dict with 'response' (str) and 'context' (dict used for RAG)
    """
    # Get relevant course context
    context = get_relevant_context(user_query)

    # Build messages for OpenAI
    system_prompt = build_system_prompt(context)

    messages = [{'role': 'system', 'content': system_prompt}]

    # Add conversation history (last 10 messages to keep context but save tokens)
    if conversation_history:
        messages.extend(conversation_history[-10:])

    # Add current user message
    messages.append({'role': 'user', 'content': user_query})

    # Call OpenAI API
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheapest model
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        assistant_message = response.choices[0].message.content

        return {
            'response': assistant_message,
            'context': context,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens,
            }
        }

    except Exception as e:
        # Fallback response if API call fails
        return {
            'response': f"I apologize, but I'm having trouble connecting right now. Please try again later or contact us at info@afimpp.institute or call +233 55 778 2728 for assistance. (Error: {str(e)})",
            'context': context,
            'error': str(e)
        }


def get_conversation_history(conversation):
    """Get message history for a conversation"""
    messages = []
    for msg in conversation.messages.filter(role__in=['user', 'assistant']).order_by('created_at'):
        messages.append({
            'role': msg.role,
            'content': msg.content
        })
    return messages
