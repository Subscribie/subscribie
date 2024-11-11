from strictyaml import load, Map, Email, Str, Url, Int, Bool, Regex, CommaSeparated, Seq
import os

# Load application settings according to schema

# Schema for Subscribie application settings
# See also https://hitchdev.com/strictyaml/
schema = Map(
    {
        "FLASK_ENV": Str(),
        "SENTRY_SDK_DSN": Str(),
        "SENTRY_SDK_SESSION_REPLAY_ID": Str(),
        "SAAS_URL": Url(),
        "SAAS_API_KEY": Str(),
        "SAAS_ACTIVATE_ACCOUNT_PATH": Str(),
        "SUBSCRIBIE_REPO_DIRECTORY": Str(),
        "SQLALCHEMY_TRACK_MODIFICATIONS": Bool(),
        "SQLALCHEMY_DATABASE_URI": Regex("sqlite:////.*"),
        "SECRET_KEY": Str(),
        "DB_FULL_PATH": Str(),
        "MODULES_PATH": Str(),
        "TEMPLATE_BASE_DIR": Str(),
        "THEME_NAME": Str(),
        "CUSTOM_PAGES_PATH": Str(),
        "UPLOADED_IMAGES_DEST": Str(),
        "UPLOADED_FILES_DEST": Str(),
        "MAX_CONTENT_LENGTH": Str(),
        "SUCCESS_REDIRECT_URL": Str(),
        "THANKYOU_URL": Str(),
        "EMAIL_LOGIN_FROM": Str(),
        "EMAIL_QUEUE_FOLDER": Str(),
        "SERVER_NAME": Str(),
        "PERMANENT_SESSION_LIFETIME": Int(),
        "MAIL_DEFAULT_SENDER": Email(),
        "STRIPE_LIVE_PUBLISHABLE_KEY": Regex("pk_live_..*"),
        "STRIPE_LIVE_SECRET_KEY": Regex("sk_live_..*"),
        "STRIPE_TEST_PUBLISHABLE_KEY": Regex("pk_test_..*"),
        "STRIPE_TEST_SECRET_KEY": Regex("sk_test_..*"),
        "STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST": Url(),
        "PYTHON_LOG_LEVEL": Str(),
        "PLAYWRIGHT_HOST": Url(),
        "PLAYWRIGHT_HEADLESS": Bool(),
        "PATH_TO_SITES": Str(),
        "PATH_TO_RENAME_SCRIPT": Str(),
        "SUBSCRIBIE_DOMAIN": Str(),
        "PRIVATE_KEY": Str(),
        "PUBLIC_KEY": Str(),
        "SUPPORTED_CURRENCIES": CommaSeparated(Str()),
        "ANTI_SPAM_SHOP_NAMES_MODEL_FULL_PATH": Str(),
        "SUSPECTED_SPAM_EMAIL_DOMAINS": Seq(Str()),
        "TELEGRAM_TOKEN": Str(),
        "TELEGRAM_CHAT_ID": Str(),
        "TELEGRAM_PYTHON_LOG_LEVEL": Str(),
        "TEST_SHOP_OWNER_EMAIL_ISSUE_704": Email(),
        "TEST_SHOP_OWNER_LOGIN_URL": Url(),
    }
)


def load_settings():
    with open("settings.yaml") as fp:
        settings_string = fp.read()
        settings = load(settings_string, schema)
        for key in schema._required_keys:
            if key in os.environ:
                print(f"Overriding setting {key} with environ value: {os.getenv(key)}")
                settings[key] = os.getenv(key)
        return settings


# Load app setttings via strictyaml & schema
settings = load_settings().data
