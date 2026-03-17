import random
import csv

# English word banks
positive_adj_en = [
"great","amazing","fantastic","excellent","wonderful","perfect","awesome",
"nice","beautiful","incredible","superb","outstanding","brilliant"
]

negative_adj_en = [
"bad","terrible","awful","horrible","worst","poor","disappointing",
"useless","annoying","broken","cheap","ugly"
]

products_en = [
"product","phone","laptop","movie","service","app","game","item","device","restaurant"
]

positive_templates_en = [
"I love this {product}",
"This {product} is {adj}",
"I really like this {product}",
"This is a {adj} {product}",
"The {product} works {adj}",
"This {product} is absolutely {adj}",
"I am very happy with this {product}"
]

negative_templates_en = [
"I hate this {product}",
"This {product} is {adj}",
"I regret buying this {product}",
"This is a very {adj} {product}",
"The {product} works very {adj}",
"This {product} is absolutely {adj}",
"I am very disappointed with this {product}"
]

neutral_adj_en = [
"okay","fine","acceptable","average","so-so","mediocre","decent","fair","not bad","neutral"
]

neutral_templates_en = [
"This {product} is {adj}",
"The {product} works {adj}",
"I feel the {product} is {adj}",
"This {product} is kinda {adj}",
"It is a {adj} {product}",
"The {product} seems {adj}"
]

# Vietnamese word banks
positive_adj_vi = [
"tốt","tuyệt vời","xuất sắc","hoàn hảo","rất ổn","đáng tiền","chất lượng cao"
]

negative_adj_vi = [
"tệ","rất tệ","kém","rất kém","thất vọng","không đáng tiền","tồi tệ"
]

products_vi = [
"sản phẩm","điện thoại","máy tính","dịch vụ","ứng dụng","trò chơi","thiết bị"
]

positive_templates_vi = [
"Tôi rất thích {product} này",
"{product} này rất {adj}",
"Tôi rất hài lòng với {product}",
"Đây là một {product} {adj}",
"{product} này thật sự {adj}",
"Trải nghiệm với {product} rất {adj}"
]

negative_templates_vi = [
"Tôi ghét {product} này",
"{product} này rất {adj}",
"Tôi rất thất vọng với {product}",
"Đây là một {product} {adj}",
"Trải nghiệm với {product} rất {adj}",
"{product} này thật sự {adj}"
]

neutral_adj_vi = [
"ổn", "bình thường", "không tệ", "không quá tốt", "trung tính", "chấp nhận được", "tạm được", "bình ổn"
]

neutral_templates_vi = [
"{product} này {adj}",
"Mình thấy {product} này {adj}",
"Trải nghiệm với {product} khá {adj}",
"{product} này hơi {adj}",
"Đây là một {product} {adj}"
]

rows = []

# generate English positive
for i in range(5000):
    template = random.choice(positive_templates_en)
    sentence = template.format(
        product=random.choice(products_en),
        adj=random.choice(positive_adj_en)
    )
    rows.append([sentence,"positive"])

# generate English negative
for i in range(5000):
    template = random.choice(negative_templates_en)
    sentence = template.format(
        product=random.choice(products_en),
        adj=random.choice(negative_adj_en)
    )
    rows.append([sentence,"negative"])

# generate Vietnamese positive
for i in range(5000):
    template = random.choice(positive_templates_vi)
    sentence = template.format(
        product=random.choice(products_vi),
        adj=random.choice(positive_adj_vi)
    )
    rows.append([sentence,"positive"])

# generate Vietnamese negative
for i in range(5000):
    template = random.choice(negative_templates_vi)
    sentence = template.format(
        product=random.choice(products_vi),
        adj=random.choice(negative_adj_vi)
    )
    rows.append([sentence,"negative"])

# generate English neutral
for i in range(3000):
    template = random.choice(neutral_templates_en)
    sentence = template.format(
        product=random.choice(products_en),
        adj=random.choice(neutral_adj_en)
    )
    rows.append([sentence,"neutral"])

# generate Vietnamese neutral
for i in range(3000):
    template = random.choice(neutral_templates_vi)
    sentence = template.format(
        product=random.choice(products_vi),
        adj=random.choice(neutral_adj_vi)
    )
    rows.append([sentence,"neutral"])

random.shuffle(rows)

with open("data.csv","w",newline="",encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["text","label"])
    writer.writerows(rows)

print("Dataset created! (includes positive/negative/neutral samples)")