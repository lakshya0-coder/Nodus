"""
AI Assistant Service — Gemini-powered, menu-grounded drink recommendation engine.
Supports English and Hindi, logs all conversations.
"""
import json
import re
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIAssistant:
    """Menu-grounded AI drink recommendation assistant."""

    def __init__(self, app=None):
        self.app = app
        self.model = None
        self._initialized = False

    def init_app(self, app):
        self.app = app

    def _get_api_key(self):
        """Get API key from settings or config."""
        from app.models.setting import Setting
        key = Setting.get('gemini_api_key', '')
        if not key and self.app:
            key = self.app.config.get('GEMINI_API_KEY', '')
        return key

    def _ensure_initialized(self):
        """Lazy initialization of the Gemini model."""
        if self._initialized and self.model:
            return True

        if not GEMINI_AVAILABLE:
            return False

        api_key = self._get_api_key()
        if not api_key:
            return False

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self._initialized = True
            return True
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            return False

    def _get_menu_context(self, lang='en'):
        """Build menu context string from live database items."""
        from app.models.menu import MenuItem, MenuCategory

        categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
        menu_text = []

        for cat in categories:
            cat_name = cat.name_hi if lang == 'hi' and cat.name_hi else cat.name_en
            items = MenuItem.query.filter_by(category_id=cat.id, is_available=True).all()
            if items:
                menu_text.append(f"\n### {cat_name} ({cat.name_en})")
                for item in items:
                    name = item.name_hi if lang == 'hi' and item.name_hi else item.name_en
                    name_alt = item.name_en if lang == 'hi' else item.name_hi
                    desc = item.description_hi if lang == 'hi' and item.description_hi else item.description_en
                    tags = item.get_tags()
                    tag_str = f" [{', '.join(tags)}]" if tags else ""
                    menu_text.append(f"- **{name}** (ID: {item.id}) ({name_alt}) — ₹{item.price}{tag_str}")
                    if desc:
                        menu_text.append(f"  {desc}")

        return "\n".join(menu_text)

    def _build_system_prompt(self, lang='en'):
        """Build the system prompt with live menu data."""
        menu_context = self._get_menu_context(lang)

        if lang == 'hi':
            return f"""तुम नोडस कैफ़े के AI ड्रिंक सलाहकार हो। तुम्हारा काम है ग्राहकों को उनकी पसंद के आधार पर मेन्यू से सही ड्रिंक सुझाना।

नियम:
1. सिर्फ नीचे दिए गए मेन्यू से ही आइटम सुझाओ। कभी भी ऐसी चीज़ मत सुझाओ जो मेन्यू में नहीं है।
2. 1-3 आइटम सुझाओ, हर एक के लिए कारण बताओ।
3. हिंदी में जवाब दो, लेकिन आइटम के नाम हिंदी और अंग्रेजी दोनों में बताओ।
4. ग्राहक के फॉलो-अप सवालों को संभालो ("कुछ सस्ता बताओ", "और मीठा कुछ")।
5. सिर्फ खाने-पीने के बारे में बात करो। बाकी सवालों पर विनम्रता से मना करो।
6. आपको एक JSON के रूप में उत्तर देना होगा, जिसमें `reply` (ग्राहक के लिए आपका संदेश) और `recommended_items` (आपके द्वारा सुझाए गए आइटम के ID का एरे) शामिल होना चाहिए।

यहाँ हमारा मौजूदा मेन्यू है:
{menu_context}"""
        else:
            return f"""You are the AI drink advisor for Nodus Cafe. Your job is to help customers discover the perfect drink or snack from our menu based on their preferences and mood.

Rules:
1. ONLY recommend items from the menu below. NEVER suggest items that don't exist on our menu.
2. Suggest 1-3 items, with a brief reason for each recommendation.
3. Respond in English, but mention item names in both English and Hindi if available.
4. Handle follow-up requests naturally ("something cheaper", "make it stronger", "anything cold").
5. Stay on topic — only discuss food and drinks. Politely decline unrelated questions.
6. Return a valid JSON response containing `reply` (your message to the customer) and `recommended_items` (array of integer IDs of the items you are recommending).

Here is our current live menu:
{menu_context}"""

    def get_recommendation(self, user_message, conversation_history=None, lang='en'):
        """
        Get AI drink recommendation.

        Returns:
            dict: {
                'response': str,
                'recommended_items': list[int],
                'success': bool,
                'error': str or None
            }
        """
        # Check if AI is available
        if not self._ensure_initialized():
            return self._fallback_response(user_message, lang)

        try:
            system_prompt = self._build_system_prompt(lang)

            # Re-initialize model with system instruction
            model = genai.GenerativeModel(
                'gemini-2.0-flash',
                system_instruction=system_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "reply": {"type": "string"},
                            "recommended_items": {
                                "type": "array",
                                "items": {"type": "integer"}
                            }
                        },
                        "required": ["reply", "recommended_items"]
                    }
                )
            )

            # Build conversation history
            messages = []
            if conversation_history:
                for msg in conversation_history[-6:]:  # Last 6 messages
                    role = 'user' if msg['sender'] == 'user' else 'model'
                    messages.append({'role': role, 'parts': [msg['message']]})

            # Add current message
            messages.append({'role': 'user', 'parts': [user_message]})

            # Generate response
            response = model.generate_content(messages)
            
            try:
                data = json.loads(response.text)
                clean_response = data.get('reply', '')
                recommended_ids = data.get('recommended_items', [])
            except json.JSONDecodeError:
                clean_response = response.text
                recommended_ids = []

            return {
                'response': clean_response,
                'recommended_items': recommended_ids,
                'success': True,
                'error': None
            }

        except Exception as e:
            print(f"AI Error: {e}")
            return self._fallback_response(user_message, lang)

    def _extract_item_ids(self, text):
        """Extract menu item IDs from AI response."""
        match = re.search(r'\[ITEMS:\s*([\d,\s]+)\]', text)
        if match:
            try:
                ids = [int(x.strip()) for x in match.group(1).split(',') if x.strip().isdigit()]
                return ids
            except (ValueError, AttributeError):
                pass
        return []

    def _fallback_response(self, user_message, lang='en'):
        """Rule-based fallback when API is unavailable."""
        from app.models.menu import MenuItem

        # Simple keyword matching
        keywords = user_message.lower()
        items = MenuItem.query.filter_by(is_available=True).all()

        matched = []

        # Keyword-based matching
        cold_words = ['cold', 'iced', 'cool', 'thanda', 'ठंडा', 'ठंडी', 'शीतल']
        hot_words = ['hot', 'warm', 'garam', 'गरम', 'गर्म']
        sweet_words = ['sweet', 'meetha', 'मीठा', 'मीठी']
        strong_words = ['strong', 'bold', 'kadak', 'कड़क', 'तेज़']
        light_words = ['light', 'mild', 'halka', 'हल्का']
        coffee_words = ['coffee', 'espresso', 'latte', 'cappuccino', 'कॉफ़ी']
        tea_words = ['tea', 'chai', 'चाय']

        for item in items:
            score = 0
            item_text = f"{item.name_en} {item.description_en} {item.name_hi} {item.description_hi}".lower()
            tags = [t.lower() for t in item.get_tags()]

            if any(w in keywords for w in cold_words) and any(w in item_text for w in ['iced', 'cold', 'frappe', 'shake', 'smoothie']):
                score += 2
            if any(w in keywords for w in hot_words) and any(w in item_text for w in ['hot', 'warm', 'espresso', 'latte', 'cappuccino']):
                score += 2
            if any(w in keywords for w in sweet_words) and any(w in item_text for w in ['sweet', 'caramel', 'vanilla', 'chocolate', 'mocha']):
                score += 2
            if any(w in keywords for w in strong_words) and any(w in item_text for w in ['strong', 'espresso', 'bold', 'double']):
                score += 2
            if any(w in keywords for w in light_words) and any(w in item_text for w in ['light', 'green', 'herbal', 'mild']):
                score += 2
            if any(w in keywords for w in coffee_words) and 'coffee' in item_text:
                score += 3
            if any(w in keywords for w in tea_words) and any(w in item_text for w in ['tea', 'chai']):
                score += 3
            if 'bestseller' in tags:
                score += 1

            if score > 0:
                matched.append((score, item))

        # Sort by score, take top 3
        matched.sort(key=lambda x: x[0], reverse=True)
        top_items = [item for _, item in matched[:3]]

        # If no matches, return bestsellers
        if not top_items:
            top_items = [item for item in items if 'Bestseller' in item.get_tags()][:3]
            if not top_items:
                top_items = items[:3]

        # Build response
        recommended_ids = [item.id for item in top_items]

        if lang == 'hi':
            response = "यहाँ आपके लिए मेरे सुझाव हैं:\n\n"
            for item in top_items:
                name = item.name_hi if item.name_hi else item.name_en
                desc = item.description_hi if item.description_hi else item.description_en
                response += f"☕ **{name}** ({item.name_en}) — ₹{item.price}\n"
                if desc:
                    response += f"   {desc}\n\n"
            response += "\nक्या आप कुछ और जानना चाहेंगे?"
        else:
            response = "Here are my suggestions for you:\n\n"
            for item in top_items:
                desc = item.description_en or ''
                response += f"☕ **{item.name_en}** ({item.name_hi}) — ₹{item.price}\n"
                if desc:
                    response += f"   {desc}\n\n"
            response += "\nWould you like to know more about any of these?"

        return {
            'response': response,
            'recommended_items': recommended_ids,
            'success': True,
            'error': None
        }


# Singleton instance
ai_assistant = AIAssistant()
