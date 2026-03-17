import csv
import random

# Generate more training data based on simple positive/negative/neutral word groups.
positive_words = [
    "tốt", "xuất sắc", "hoàn hảo", "tuyệt vời", "hài lòng", "thích", "yêu thích", "đáng tiền", "ổn", "tuyệt", "amazing", "great", "excellent", "wonderful", "superb", "fantastic", "love", "happy", "satisfied", "brilliant"
]
negative_words = [
    "tệ", "kém", "thất vọng", "ghét", "tồi tệ", "không đáng", "broken", "poor", "bad", "disappointed", "hate", "worst", "terrible", "awful", "horrible", "regret"
]

neutral_words = [
    "ổn", "bình thường", "không tệ", "không quá tốt", "khá", "tạm", "trung tính", "chấp nhận được", "đủ", "bình ổn"
]

# Generate synthetic sentences

def generate_sentence(label, length=5):
    if label == "positive":
        words = positive_words
    elif label == "negative":
        words = negative_words
    else:
        words = neutral_words
    return " ".join(random.choice(words) for _ in range(length)).capitalize() + "."


def main():
    count = 2000
    data = []
    for _ in range(count):
        label = random.choice(["positive", "negative", "neutral"])
        text = generate_sentence(label, length=random.randint(4, 10))
        data.append({"text": text, "label": label})

    with open("data.csv", "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label"])
        writer.writerows(data)

    print(f"Added {count} synthetic records to data.csv")


if __name__ == "__main__":
    main()
