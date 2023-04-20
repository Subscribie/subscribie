import pickle
from scipy.sparse import hstack
from flask import Flask
import os

ANTI_SPAM_SHOP_NAMES_MODEL_FULL_PATH = os.getenv(
    "ANTI_SPAM_SHOP_NAMES_MODEL_FULL_PATH", "./classifier.pkl"
)

# Load the classifier and preprocessing steps
with open(ANTI_SPAM_SHOP_NAMES_MODEL_FULL_PATH, "rb") as file:
    (
        loaded_classifier,
        loaded_char_vectorizer,
        loaded_word_vectorizer,
    ) = pickle.load(  # noqa: E501
        file
    )


def detect_spam_shop_name(account_name: str) -> bool:

    new_data = [account_name]
    # Preprocess the new data
    new_data_char = loaded_char_vectorizer.transform(new_data)
    new_data_word = loaded_word_vectorizer.transform(new_data)
    new_data_combined = hstack([new_data_char, new_data_word])

    # Make predictions on the new data
    predictions = loaded_classifier.predict(new_data_combined)

    # Print the predictions
    for account_name, prediction in zip(new_data, predictions):
        label = "spam" if prediction == 1 else "not spam"
        print(f"{account_name}: {label}")
        spam_detected = 0
        if prediction == 1:
            spam_detected = 1
        return spam_detected


app = Flask(__name__)


@app.route("/spamcheck/<string:account_name>")
def check_spam(account_name):
    return str(detect_spam_shop_name(account_name))
