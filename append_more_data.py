import csv

new_rows = [
    # Positive sentiments (app/model/dataset)
    ("Ứng dụng này chạy rất mượt, positive"),
    ("Mình rất hài lòng với kết quả phân loại, positive"),
    ("Model Naive Bayes cho kết quả chính xác, positive"),
    ("Dữ liệu huấn luyện đủ tốt giúp kết quả chính xác, positive"),
    ("Ứng dụng này dễ dùng và rất tiện, positive"),
    ("Tôi thích cách app hiển thị kết quả, positive"),
    ("Phân loại cảm xúc chính xác, positive"),
    ("Phần mềm này giúp tôi hiểu cảm xúc, positive"),
    ("Mô hình nghe có vẻ thông minh, positive"),
    ("Dữ liệu được lưu trữ tốt, positive"),

    # Negative sentiments
    ("Ứng dụng này thường xuyên lỗi, negative"),
    ("Model dự đoán sai nhiều, negative"),
    ("Dữ liệu huấn luyện không đủ tốt, negative"),
    ("Giao diện khó dùng, negative"),
    ("Phân loại sai nhiều, negative"),
    ("App chạy rất chậm, negative"),
    ("Mình không hiểu kết quả trả về, negative"),
    ("Kết quả không chính xác, negative"),
    ("Thiếu dữ liệu nên phân loại mơ hồ, negative"),
    ("App này gây khó chịu, negative"),

    # Sentences about training / improvement
    ("Tôi muốn thêm dữ liệu để model tốt hơn, positive"),
    ("Cần nhiều mẫu hơn để Naive Bayes chính xác, positive"),
    ("Mình đang test thuật toán phân loại, positive"),
    ("Dữ liệu chưa đủ nên kết quả chưa chính xác, negative"),
    ("Kết quả hiện tại khá trung tính, neutral"),
    ("Câu này rất tiêu cực, negative"),
    ("Nó làm mình cảm thấy tiêu cực, negative"),
    ("Không thích chút nào, negative"),
    ("Ngôn ngữ này nghe tiêu cực, negative"),
    ("Cứ bình thường thôi, neutral"),
    ("Không tốt không xấu, neutral"),

    # More general sentences
    ("Ứng dụng này giúp học Naive Bayes, positive"),
    ("Cần thêm tính năng gợi ý, positive"),
    ("Nó học từ dữ liệu mới, positive"),
    ("Cần cải thiện phần phân tích, negative"),
    ("Model bị quá khớp, negative"),
    ("Phân loại sai do dữ liệu lẫn lộn, negative"),
    ("Tôi thích app có giao diện đẹp, positive"),
    ("App bị crash khi tải dữ liệu, negative"),
    ("Cần thêm phần hướng dẫn, negative"),
    ("Mình muốn cho nó học tiếng Việt tốt hơn, positive"),
    ("Mình chưa rõ cảm xúc của câu này, neutral"),
]

# Append new rows to data.csv if they're not already present
path = "data.csv"
existing = set()
with open(path, encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2:
            existing.add((row[0].strip(), row[1].strip()))

with open(path, "a", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    added = 0
    for r in new_rows:
        text, label = r[0].strip(), r[1].strip() if isinstance(r, tuple) else r.strip().rsplit(' ', 1)
        # if r is plain string separated by last space
        if isinstance(r, str):
            parts = r.rsplit(' ', 1)
            if len(parts) == 2 and parts[1] in ("positive", "negative", "neutral"):
                text, label = parts[0], parts[1]
            else:
                continue
        if (text, label) not in existing:
            writer.writerow([text, label])
            added += 1

print(f"Added {added} new rows to data.csv")
