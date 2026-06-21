"""AI Chat API endpoints."""
import uuid
from flask import Blueprint, request, jsonify, session
from app.models import db
from app.models.conversation import Conversation, ConversationMessage
from app.services.ai_assistant import ai_assistant

api_ai_bp = Blueprint('api_ai', __name__)


@api_ai_bp.route('/chat', methods=['POST'])
def chat():
    """Handle AI chat messages."""
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'error': 'Message required'}), 400

    user_message = data['message']
    session_id = data.get('session_id', str(uuid.uuid4()))
    lang = data.get('language', session.get('lang', 'en'))
    conversation_id = data.get('conversation_id')

    # Find or create conversation
    conversation = None
    if conversation_id:
        conversation = Conversation.query.get(conversation_id)

    if not conversation:
        conversation = Conversation.query.filter_by(session_id=session_id).order_by(
            Conversation.started_at.desc()
        ).first()

    if not conversation:
        conversation = Conversation(
            session_id=session_id,
            language=lang
        )
        db.session.add(conversation)
        db.session.flush()

    # Save user message
    user_msg = ConversationMessage(
        conversation_id=conversation.id,
        sender='user',
        message=user_message
    )
    db.session.add(user_msg)

    # Get conversation history for context
    history = ConversationMessage.query.filter_by(
        conversation_id=conversation.id
    ).order_by(ConversationMessage.timestamp).all()

    history_list = [{'sender': m.sender, 'message': m.message} for m in history]

    # Get AI response
    result = ai_assistant.get_recommendation(user_message, history_list, lang)

    # Save AI response
    import json
    ai_msg = ConversationMessage(
        conversation_id=conversation.id,
        sender='ai',
        message=result['response'],
        recommended_items=json.dumps(result.get('recommended_items', []))
    )
    db.session.add(ai_msg)
    db.session.commit()

    # Get recommended item details
    recommended_details = []
    if result.get('recommended_items'):
        from app.models.menu import MenuItem
        for item_id in result['recommended_items']:
            item = MenuItem.query.get(item_id)
            if item:
                recommended_details.append(item.to_dict(lang))

    return jsonify({
        'response': result['response'],
        'conversation_id': conversation.id,
        'message_id': ai_msg.id,
        'recommended_items': recommended_details,
        'success': result['success']
    })


@api_ai_bp.route('/feedback', methods=['POST'])
def feedback():
    """Handle feedback on AI responses."""
    data = request.get_json()
    if not data or not data.get('message_id') or not data.get('feedback'):
        return jsonify({'error': 'message_id and feedback required'}), 400

    message = ConversationMessage.query.get(data['message_id'])
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    message.feedback = data['feedback']  # 'thumbs_up' or 'thumbs_down'
    db.session.commit()

    return jsonify({'success': True})


@api_ai_bp.route('/conversations', methods=['GET'])
def list_conversations():
    """List all conversations (admin use)."""
    from flask_login import current_user, login_required

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    lang_filter = request.args.get('language')
    search = request.args.get('search')

    query = Conversation.query.order_by(Conversation.started_at.desc())

    if lang_filter:
        query = query.filter_by(language=lang_filter)

    if search:
        # Search in messages
        query = query.join(ConversationMessage).filter(
            ConversationMessage.message.ilike(f'%{search}%')
        ).distinct()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'conversations': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })
