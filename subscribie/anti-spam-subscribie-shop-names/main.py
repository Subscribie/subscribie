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

# Load the data
data = pd.read_csv("shop-list-a.csv")

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    data["account_name"], data["label"], test_size=0.3, random_state=42
)

# Preprocess the data: character-level features
char_vectorizer = CountVectorizer(analyzer="char", ngram_range=(2, 5))
breakpoint()
X_train_char = char_vectorizer.fit_transform(X_train)
X_test_char = char_vectorizer.transform(X_test)

# Preprocess the data: word-level features
word_vectorizer = TfidfVectorizer()
X_train_word = word_vectorizer.fit_transform(X_train)
X_test_word = word_vectorizer.transform(X_test)

# Combine character-level and word-level features
X_train_combined = hstack([X_train_char, X_train_word])
X_test_combined = hstack([X_test_char, X_test_word])

# Train the model
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(X_train_combined, y_train)

# Evaluate the model
y_pred = classifier.predict(X_test_combined)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1-score:", f1_score(y_test, y_pred))

# Save the classifier and preprocessing steps
with open("classifier.pkl", "wb") as fp:
    pickle.dump((classifier, char_vectorizer, word_vectorizer), fp)
