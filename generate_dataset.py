import random
import csv

positive_en = [
"I love this product",
"This is amazing",
"This phone is great",
"I really like this",
"This movie is wonderful",
"This service is excellent",
"The quality is very good",
"I am very satisfied",
"This item works perfectly",
"I highly recommend this"
]

negative_en = [
"I hate this product",
"This is terrible",
"This phone is very bad",
"I regret buying this",
"This movie is awful",
"The service is horrible",
"Very bad experience",
"This item is useless",
"I am disappointed",
"This is the worst product"
]

positive_vi = [
"Tôi rất thích sản phẩm này",
"Sản phẩm này rất tốt",
"Chất lượng rất tuyệt vời",
"Tôi rất hài lòng",
"Dịch vụ rất tốt",
"Tôi khuyên bạn nên mua",
"Sản phẩm hoạt động rất tốt",
"Trải nghiệm rất tuyệt",
"Đây là sản phẩm tuyệt vời",
"Tôi rất thích nó"
]

negative_vi = [
"Tôi ghét sản phẩm này",
"Sản phẩm rất tệ",
"Chất lượng rất kém",
"Tôi rất thất vọng",
"Dịch vụ rất tệ",
"Tôi sẽ không mua lại",
"Trải nghiệm rất tệ",
"Sản phẩm không đáng tiền",
"Đây là sản phẩm tệ",
"Tôi không hài lòng"
]

rows = []

for i in range(1000):
    rows.append([random.choice(positive_en), "positive"])
    rows.append([random.choice(positive_vi), "positive"])

for i in range(1000):
    rows.append([random.choice(negative_en), "negative"])
    rows.append([random.choice(negative_vi), "negative"])

random.shuffle(rows)

with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["text", "label"])
    writer.writerows(rows)

print("Dataset created: data.csv")