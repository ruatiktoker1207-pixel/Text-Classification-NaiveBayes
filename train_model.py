import csv
import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# đọc dataset
# Data may contain commas in the text column, so we parse robustly using csv.reader.
rows = []
with open("data.csv", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader, None)
    for row in reader:
        if not row:
            continue
        # Assume last column is label, the rest is text
        label = row[-1].strip()
        text = ",".join(row[:-1]).strip()
        if text and label:
            rows.append((label, text))

data = pd.DataFrame(rows, columns=["label", "text"])

X = data["text"]
y = data["label"]

# chia train test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# vector hóa text
vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# dự đoán
y_pred = model.predict(X_test_vec)

accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy)

# lưu model
pickle.dump(model, open("naive_bayes_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model saved!")