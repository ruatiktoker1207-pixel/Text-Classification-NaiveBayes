import csv

# Mẫu câu để tạo dữ liệu (positive/negative/neutral)
positive_templates = [
    "Ứng dụng này {adj}.",
    "Mình thấy app {adj}.",
    "Mô hình phân loại hoạt động {adj}.",
    "Dữ liệu training rất {adj}.",
    "Tôi rất {adj} với kết quả của app.",
    "Phần mềm này {adj}.",
    "Cảm ơn vì phân loại {adj}.",
    "App trả kết quả {adj}.",
]
negative_templates = [
    "Ứng dụng này {adj}.",
    "Mình thấy app {adj}.",
    "Mô hình phân loại quá {adj}.",
    "Dữ liệu training bị {adj}.",
    "Tôi rất {adj} với kết quả này.",
    "Phần mềm này {adj}.",
    "Đây là một trải nghiệm {adj}.",
    "App trả kết quả {adj}.",
]
neutral_templates = [
    "Ứng dụng này {adj}.",
    "Mình thấy app {adj}.",
    "Mô hình phân loại hoạt động {adj}.",
    "Dữ liệu training khá {adj}.",
    "Tôi cảm thấy {adj} về kết quả của app.",
    "Phần mềm này {adj}.",
    "App trả kết quả {adj}.",
]

positive_adjs = [
    "tốt", "tuyệt vời", "mượt mà", "chính xác", "đáng tin cậy", "ổn định", "hữu ích", "đầy đủ", "thông minh", "thích"
]
negative_adjs = [
    "tệ", "kém", "lỗi", "không chính xác", "đáng thất vọng", "chậm", "bị crash", "không ổn", "lộn xộn", "bối rối", "tiêu cực", "xấu", "đáng ghét"
]
neutral_adjs = [
    "bình thường", "ổn", "không tệ", "không quá tốt", "trung tính", "mơ hồ", "chấp nhận được", "bình ổn", "không nổi bật", "tạm được"
]

path = "data.csv"

# Read existing rows
existing = set()
with open(path, encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2:
            existing.add((row[0].strip(), row[1].strip()))

# Generate new data
new_rows = []
for tmpl in positive_templates:
    for adj in positive_adjs:
        text = tmpl.format(adj=adj)
        new_rows.append((text, "positive"))
for tmpl in negative_templates:
    for adj in negative_adjs:
        text = tmpl.format(adj=adj)
        new_rows.append((text, "negative"))

for tmpl in neutral_templates:
    for adj in neutral_adjs:
        text = tmpl.format(adj=adj)
        new_rows.append((text, "neutral"))

# Add to CSV if not exists
added = 0
with open(path, "a", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    for text, label in new_rows:
        if (text, label) not in existing:
            writer.writerow([text, label])
            added += 1

print(f"Added {added} new training examples")
