from app.models import db
from datetime import datetime
import json


class Conversation(db.Model):
    """AI chat conversation session."""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)  # Browser session ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    language = db.Column(db.String(5), default='en')
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    led_to_booking = db.Column(db.Boolean, default=False)
    led_to_order = db.Column(db.Boolean, default=False)

    messages = db.relationship('ConversationMessage', backref='conversation', lazy=True,
                                order_by='ConversationMessage.timestamp')

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'language': self.language,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'led_to_booking': self.led_to_booking,
            'led_to_order': self.led_to_order,
            'message_count': len(self.messages),
            'messages': [m.to_dict() for m in self.messages]
        }


class ConversationMessage(db.Model):
    """Individual message in a conversation."""
    __tablename__ = 'conversation_messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    message = db.Column(db.Text, nullable=False)
    recommended_items = db.Column(db.Text, default='[]')  # JSON array of menu item IDs
    feedback = db.Column(db.String(15), nullable=True)  # 'thumbs_up', 'thumbs_down', or null
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def get_recommended_items(self):
        try:
            return json.loads(self.recommended_items) if self.recommended_items else []
        except (json.JSONDecodeError, TypeError):
            return []

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender': self.sender,
            'message': self.message,
            'recommended_items': self.get_recommended_items(),
            'feedback': self.feedback,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
