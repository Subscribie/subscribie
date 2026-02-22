import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)  # noqa: E501
from scipy.sparse import hstack
import pickle

def load_data(csv_file_path=None):
    # Load the data
    if csv_file_path:
        csv_data = pd.read_csv(csv_file_path)
    else:
        csv_data = pd.read_csv("/home/chris/Documents/programming/python/subscribie/subscribie/anti_spam_subscribie_shop_names/shop-names-random-order.csv")
    return csv_data

def split_data(data):
    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        data["account_name"], data["label"], test_size=0.3, random_state=42
    )

    return X_train, X_test, y_train, y_test

def preprocess_data(X_train, X_test = None):
    # Preprocess the data: character-level features
    char_vectorizer = CountVectorizer(analyzer="char", ngram_range=(2, 5))
    X_train_char = char_vectorizer.fit_transform(X_train)
    if X_test is not None:
        X_test_char = char_vectorizer.transform(X_test)

    # Preprocess the data: word-level features
    word_vectorizer = TfidfVectorizer()
    X_train_word = word_vectorizer.fit_transform(X_train)
    if X_test is not None:
        X_test_word = word_vectorizer.transform(X_test)

    # Combine character-level and word-level features
    X_train_combined = hstack([X_train_char, X_train_word])
    if X_test is not None:
        X_test_combined = hstack([X_test_char, X_test_word])

    if X_test is not None:
        return X_train_combined, X_test_combined, char_vectorizer, word_vectorizer
    else:
        return X_train_combined, char_vectorizer, word_vectorizer


def train_model(X_train_combined, y_train):
    # Train the model
    classifier = RandomForestClassifier(n_estimators=100, random_state=42, warm_start=True)
    classifier.fit(X_train_combined, y_train)
    return classifier

def evaluate_model(classifier, X_test_combined, y_test):
    # Evaluate the model
    y_pred = classifier.predict(X_test_combined)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred))
    print("Recall:", recall_score(y_test, y_pred))
    print("F1-score:", f1_score(y_test, y_pred))


def get_more_training_samples():
    """
    get_more_training_samples
    Open 'new-data.csv'
    If len > 0
    Create new X_train_combined, y_train data points
    """
    pd = load_data('/home/chris/Documents/programming/python/csv-writing/new-data.csv')
    X_train = pd['account_name']
    X_train_combined, char_vectorizer, word_vectorizer = preprocess_data(X_train, X_test=None)

    y_train = pd['label']
    return X_train_combined, y_train


def save_updated_model_file(classifier, char_vectorizer, word_vectorizer):
    """
    Save (pickle) the latest model to disk
    """
    # Save the classifier and preprocessing steps
    with open("classifier.pkl", "wb") as fp:
        pickle.dump((classifier, char_vectorizer, word_vectorizer), fp)

def main(incremental_learning=False):
    pd = load_data()
    X_train, X_test, y_train, y_test = split_data(pd)
    X_train_combined, X_test_combined, char_vectorizer, word_vectorizer = preprocess_data(X_train, X_test)
    classifier = train_model(X_train_combined, y_train)
    if incremental_learning:
        # Keep learning until stopped
        while True:
            from time import sleep;
            sleep(0.5)
            print("sleeping")
            X_train_combined, y_train = get_more_training_samples()
            classifier.fit(X_train_combined, y_train)
            save_updated_model_file(classifier, char_vectorizer, word_vectorizer)
            #evaluate_model(classifier, X_test_combined, y_test)

    evaluate_model(classifier, X_test_combined, y_test)
    save_updated_model_file(classifier, char_vectorizer, word_vectorizer)


if __name__ == "__main__":
    main(incremental_learning=True)



# Goal: incremental learning
# see https://stackoverflow.com/questions/55123534/incrementally-fitting-sklearn-randomforestclassifier