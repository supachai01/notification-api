import os

PROVIDER_FEATURE_FLAGS = {
    'govdelivery': 'GOVDELIVERY_EMAIL_CLIENT_ENABLED'
}


def is_provider_enabled(current_app, provider_identifier):
    if provider_identifier in PROVIDER_FEATURE_FLAGS:
        return current_app.config.get(PROVIDER_FEATURE_FLAGS[provider_identifier])
    else:
        return True


def accept_recipient_identifiers_enabled():
    if os.getenv('ACCEPT_RECIPIENT_IDENTIFIERS_ENABLED', 'False') == 'True':
        return True
    else:
        return False


def is_gapixel_enabled(current_app):
    return current_app.config.get('GOOGLE_ANALYTICS_ENABLED')
