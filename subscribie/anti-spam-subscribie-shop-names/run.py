import pickle
from scipy.sparse import hstack

# Load the classifier and preprocessing steps
with open("classifier.pkl", "rb") as file:
    (
        loaded_classifier,
        loaded_char_vectorizer,
        loaded_word_vectorizer,
    ) = pickle.load(  # noqa: E501
        file
    )

# Example new data
new_data = [
    "new_account.subscriby.shop",
    "another_account.subscriby.shop",
    "iniongfgfgfdgdfgjjjuiikloadconfirmdocumentcookie.subscriby.shop",
    "njfebifjwjdwufuihwiufwiodjwhdfeiujwoidwhtiueofadkxasjdfiuheijiejfoeuwhfiuwsjjhwuifojwdwdhiehfjiwkdoajdfjbgvhioqdjwjfhweihwiodjwahfewhguoeidoaksfkhguwhiowjijfiowehgoifajjfshguwehiwesubscribiecouk.subscriby.shop",
    "ynmpjutrau.subscriby.shop",
    "jfwlehbtvyppyn.subscriby.shop",
]

# Preprocess the new data
new_data_char = loaded_char_vectorizer.transform(new_data)
new_data_word = loaded_word_vectorizer.transform(new_data)
new_data_combined = hstack([new_data_char, new_data_word])

# Make predictions on the new data
predictions = loaded_classifier.predict(new_data_combined)

# Print the predictions
for accounts_name, prediction in zip(new_data, predictions):
    label = "spam" if prediction == 1 else "not spam"
    print(f"{accounts_name}: {label}")
