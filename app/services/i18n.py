import os
import json

_translations = {}


def load_translations(app):
    """Load translation files on app startup."""
    global _translations
    translations_dir = os.path.join(app.root_path, 'translations')
    for lang_file in ['en.json', 'hi.json']:
        lang_code = lang_file.split('.')[0]
        filepath = os.path.join(translations_dir, lang_file)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                _translations[lang_code] = json.load(f)
        else:
            _translations[lang_code] = {}


def get_translation(key, lang='en'):
    """Get a translated string by key."""
    # Support nested keys with dot notation: "nav.home" → translations[lang]["nav"]["home"]
    keys = key.split('.')
    result = _translations.get(lang, {})
    for k in keys:
        if isinstance(result, dict):
            result = result.get(k, None)
        else:
            result = None
            break

    if result is None:
        # Fallback to English
        result = _translations.get('en', {})
        for k in keys:
            if isinstance(result, dict):
                result = result.get(k, None)
            else:
                result = None
                break

    # If still None, return the key itself as fallback
    return result if result is not None else key


def get_all_translations(lang='en'):
    """Get all translations for a language (for client-side JS)."""
    return _translations.get(lang, _translations.get('en', {}))


def init_app(app):
    load_translations(app)

    @app.context_processor
    def inject_i18n():
        from flask import request, session
        lang = session.get('lang', request.cookies.get('lang', 'en'))

        def translate(key):
            return get_translation(key, lang)

        return {
            '_': translate,
            'lang': lang,
            'get_translation': get_translation
        }
