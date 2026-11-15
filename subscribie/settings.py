from collections import namedtuple
import strictyaml
from strictyaml import (
    load,
    Map,
    Email,
    Float,
    Str,
    Url,
    Int,
    Bool,
    Regex,
    CommaSeparated,
)
import os

# Load application settings according to schema

Setting = namedtuple("Setting", ["validator", "example"])

# Single source of truth for Subscribie settings validators and example values
# See also https://hitchdev.com/strictyaml/
SETTINGS = {
    "FLASK_ENV": Setting(Str(), example="development"),
    "SENTRY_ENABLED": Setting(Bool(), example=True),
    "SENTRY_SDK_DSN": Setting(
        Str(),
        example="https://changeme@changeme.ingest.de.sentry.io/123456789",
    ),
    "SENTRY_SDK_SESSION_REPLAY_ID": Setting(Str(), example="changeme"),
    "SAAS_URL": Setting(Url(), example="https://subscribie.co.uk/"),
    "SAAS_API_KEY": Setting(Str(), example="changeme"),
    "SAAS_ACTIVATE_ACCOUNT_PATH": Setting(Str(), example="/activate"),
    "SUBSCRIBIE_REPO_DIRECTORY": Setting(Str(), example="./"),
    "SQLALCHEMY_TRACK_MODIFICATIONS": Setting(Bool(), example=False),
    "SQLALCHEMY_DATABASE_URI": Setting(
        Regex("sqlite:///.*"), example="sqlite:////tmp/data.db"
    ),
    "SECRET_KEY": Setting(
        Str(),
        example=(
            "random string. e.g. echo -e "
            "'from os import urandom\\nprint urandom(25)' | python"
        ),
    ),
    "DB_FULL_PATH": Setting(Str(), example="/tmp/data.db"),
    "MODULES_PATH": Setting(Str(), example="./modules/"),
    "TEMPLATE_BASE_DIR": Setting(Str(), example="./subscribie/themes/"),
    "THEME_NAME": Setting(Str(), example="jesmond"),
    "CUSTOM_PAGES_PATH": Setting(Str(), example="./subscribie/custom_pages/"),
    "UPLOADED_IMAGES_DEST": Setting(Str(), example="./subscribie/static/"),
    "UPLOADED_FILES_DEST": Setting(Str(), example="./subscribie/uploads/"),
    "MAX_CONTENT_LENGTH": Setting(Str(), example="52428800"),
    "SUCCESS_REDIRECT_URL": Setting(
        Str(), example="http://127.0.0.1:5000/complete_mandate"
    ),
    "THANKYOU_URL": Setting(Str(), example="http://127.0.0.1:5000/thankyou"),
    "EMAIL_LOGIN_FROM": Setting(Str(), example="hello@example.com"),
    "EMAIL_QUEUE_FOLDER": Setting(Str(), example="/var/email-queue/"),
    "SERVER_NAME": Setting(Str(), example="127.0.0.1:5000"),
    "PERMANENT_SESSION_LIFETIME": Setting(Int(), example=1800),
    "MAIL_DEFAULT_SENDER": Setting(Email(), example="noreply@example.com"),
    "STRIPE_LIVE_PUBLISHABLE_KEY": Setting(
        Regex("pk_live_..*"), example="pk_live_changeme"
    ),
    "STRIPE_LIVE_SECRET_KEY": Setting(Regex("sk_live_..*"), example="sk_live_changeme"),
    "STRIPE_TEST_PUBLISHABLE_KEY": Setting(
        Regex("pk_test_..*"), example="pk_test_changeme"
    ),
    "STRIPE_TEST_SECRET_KEY": Setting(Regex("sk_test_..*"), example="sk_test_changeme"),
    "STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST": Setting(
        Url(), example="http://127.0.0.1:8001"
    ),
    "PYTHON_LOG_LEVEL": Setting(Str(), example="DEBUG"),
    "PATH_TO_SITES": Setting(Str(), example="/path/to/sites/subscribie/"),
    "PATH_TO_RENAME_SCRIPT": Setting(
        Str(), example="/path/to/sites/subscribie/rename-shop.sh"
    ),
    "SUBSCRIBIE_DOMAIN": Setting(Str(), example="subscriby.shop"),
    "PRIVATE_KEY": Setting(Str(), example="/tmp/private.pem"),
    "PUBLIC_KEY": Setting(Str(), example="/tmp/public.pem"),
    "SUPPORTED_CURRENCIES": Setting(CommaSeparated(Str()), example="GBP,USD,EUR"),
    "ANTI_SPAM_SHOP_NAMES_MODEL_FULL_PATH": Setting(
        Str(), example="/path/to/classifier.pkl"
    ),
    "TELEGRAM_TOKEN": Setting(Str(), example=""),
    "TELEGRAM_CHAT_ID": Setting(Str(), example=""),
    "TELEGRAM_PYTHON_LOG_LEVEL": Setting(Str(), example="ERROR"),
    "TEST_SHOP_OWNER_EMAIL_ISSUE_704": Setting(Email(), example="admin@example.com"),
    "TEST_SUBSCRIBER_EMAIL_USER": Setting(Email(), example="test@example.co.uk"),
    "TEST_SHOP_OWNER_LOGIN_URL": Setting(
        Url(), example="http://127.0.0.1:5000/auth/login"
    ),
    "PLAYWRIGHT_HOST": Setting(Url(), example="http://127.0.0.1:5000/"),
    "PLAYWRIGHT_HEADLESS": Setting(Bool(), example=True),
    "PLAYWRIGHT_SLOWMO": Setting(Int(), example=500),
    "PLAYWRIGHT_MAX_RETRIES": Setting(Int(), example=1),
    "IMAP_SEARCH_UNSEEN": Setting(Str(), example="1"),
    "IMAP_SEARCH_SINCE_DATE": Setting(Str(), example="21-Aug-2024"),
    "EMAIL_SEARCH_API_HOST": Setting(Str(), example="email-search-api.example.com"),
    "SHOP_OWNER_EMAIL_HOST": Setting(Str(), example="email.example.co.uk"),
    "SHOP_OWNER_EMAIL_USER": Setting(Email(), example="alice@example.co.uk"),
    "SHOP_OWNER_MAGIC_LOGIN_IMAP_SEARCH_SUBJECT": Setting(
        Str(), example="Subscribie Magic Login"
    ),
    "SHOP_OWNER_EMAIL_PASSWORD": Setting(Str(), example="secret"),
    "SUBSCRIBER_EMAIL_HOST": Setting(Str(), example="email.example.co.uk"),
    "SUBSCRIBER_EMAIL_USER": Setting(Email(), example="test@example.co.uk"),
    "SUBSCRIBER_EMAIL_PASSWORD": Setting(Str(), example="secret"),
    "RESET_PASSWORD_IMAP_SEARCH_SUBJECT": Setting(Str(), example="Password Reset"),
    "SUBSCRIBIE_APPLICATION_FEE_DECIMAL_PERCENTAGE": Setting(Float(), example=0.025),
    "SUBSCRIBIE_FIXED_FEE_PENCE_INT": Setting(Int(), example=40),
}

schema = Map({key: setting.validator for key, setting in SETTINGS.items()})


def load_raw_settings_string(path="settings.yaml"):
    with open(path) as fp:
        return fp.read()


def get_missing_setting_keys(path="settings.yaml"):
    settings_string = load_raw_settings_string(path)
    parsed_yaml = load(settings_string).data or {}
    # Returb a list of required keys from the schema that aren't in settings.yaml
    return [
        key
        for key in schema._required_keys
        if key not in parsed_yaml and key not in os.environ
    ]


def load_settings():

    with open("settings.yaml") as fp:
        settings_string = fp.read()
        try:
            settings = load(settings_string, schema)
            for key in schema._required_keys:
                if key in os.environ:
                    print(
                        f"Overriding setting {key} with environ value: {os.getenv(key)}"  # noqa: E501
                    )
                    print(
                        (
                            "If overriding keeps happening & you can't "
                            "work out why- check your IDE (hello vscode) "
                            "isn't getting in the way. Try using a terminal instead."
                        )
                    )
                    settings[key] = os.getenv(key)
        except strictyaml.exceptions.YAMLValidationError as e:
            raise ValueError(
                "The app settings have a validation error."
                f" Check settings.yaml The error was: {e}"
            )
        return settings


# Load app settings via strictyaml & schema
if "SUBSCRIBIE_SKIP_SETTINGS_LOAD" in os.environ:
    settings = {}
else:
    settings = load_settings().data
