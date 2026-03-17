import pickle

with open('naive_bayes_model.pkl','rb') as f:
    model = pickle.load(f)
with open('vectorizer.pkl','rb') as f:
    vect = pickle.load(f)

for text in ['tiêu cực', 'tốt', 'bình thường', 'không tốt', 'không', 'xấu', 'rất tệ']:
    vec = vect.transform([text])
    pred = model.predict(vec)[0]
    proba = model.predict_proba(vec)[0]
    print(text, '->', pred, 'proba', {c: round(p, 3) for c, p in zip(model.classes_, proba)})
