import joblib
import sys

model = joblib.load("naive_bayes_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

text = " ".join(sys.argv[1:])

vec = vectorizer.transform([text])

prediction = model.predict(vec)

print(prediction[0])