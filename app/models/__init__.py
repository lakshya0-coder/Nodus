from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import User, StaffRole
from app.models.menu import MenuCategory, MenuItem
from app.models.booking import Booking
from app.models.order import Order, OrderItem
from app.models.conversation import Conversation, ConversationMessage
from app.models.prediction import DemandPrediction, ModelVersion
from app.models.setting import Setting
from app.models.contact import ContactMessage
