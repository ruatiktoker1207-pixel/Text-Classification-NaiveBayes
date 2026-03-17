import csv
import os
import random
import re
import sqlite3
import string
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session, jsonify
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

app = Flask(__name__)
app.secret_key = "secret123"

# Email configuration for OTP sending (using Gmail)
# Try to load from config_email.py first
try:
    from config_email import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT, OTP_EXPIRY_MINUTES
except ImportError:
    EMAIL_ADDRESS = "your_email@gmail.com"  # Change this to your email
    EMAIL_PASSWORD = "your_app_password"     # Change this to your app-specific password from Google
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    OTP_EXPIRY_MINUTES = 10

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send OTP to user's email"""
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = email
        message["Subject"] = "Mã OTP để đặt lại mật khẩu"
        
        body = f"""
        Xin chào,
        
        Mã OTP của bạn là: {otp}
        
        Mã này sẽ hết hạn trong {OTP_EXPIRY_MINUTES} phút.
        
        Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
        
        Trân trọng,
        AI Text Classification Team
        """
        
        message.attach(MIMEText(body, "plain", "utf-8"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Load AI model (with fallback to in-memory training)
model = None
vectorizer = None
model_accuracy = 0.0

try:
    with open("naive_bayes_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
except Exception:
    # Will build the model later when data is available
    model = None
    vectorizer = None

# Chat knowledge base (triggers + responses) - giúp chat trở nên tự nhiên hơn
CHAT_KB = [
    {
        "triggers": ["naive bayes", "naive", "bayes", "mô hình"],
        "responses": [
            "Naive Bayes là thuật toán phân loại dựa trên xác suất và giả định các đặc trưng độc lập.\nTrong app này, nó dùng để dự đoán cảm xúc (positive/negative/neutral).",
            "Mình dùng Naive Bayes để phân loại cảm xúc từ văn bản.\nNó học từ dữ liệu 'text' + 'label', rồi dùng xác suất để dự đoán."
        ]
    },
    {
        "triggers": ["huấn luyện", "tái huấn luyện", "train", "dữ liệu", "dataset"],
        "responses": [
            "Bạn có thể thêm dữ liệu vào trang 'Dữ liệu', sau đó nhấn 'Tái huấn luyện' để làm model tốt hơn.",
            "Mình cứ dựa vào dữ liệu bạn thêm vào để học. Càng có nhiều mẫu, mô hình càng chính xác."
        ]
    },
    {
        "triggers": ["cách dùng", "hướng dẫn", "làm sao"],
        "responses": [
            "Chỉ cần nhập câu vào ô 'Văn bản để phân loại' rồi nhấn 'Dự đoán' (trên bảng điều khiển).",
            "Nhập một câu, nhấn nút dự đoán, mình sẽ báo cảm xúc của câu đó (positive/negative/neutral)."
        ]
    },
    {
        "triggers": ["độ chính xác", "accuracy", "độ tin cậy"],
        "responses": [
            "Model Naive Bayes dựa vào dữ liệu đào tạo. Nếu dữ liệu tốt, độ chính xác sẽ lên cao hơn. Bạn có thể kiểm tra bằng cách thêm dữ liệu chất lượng vào mục 'Dữ liệu'.",
            "Độ tin cậy phụ thuộc vào dữ liệu bạn cung cấp. Nhiều dữ liệu rõ ràng, ít lẫn lộn giúp mô hình chính xác hơn."
        ]
    },
    {
        "triggers": ["ok", "được", "đồng ý", "oke", "okie"],
        "responses": [
            "Ok nhé! Bạn muốn thử câu mới hay muốn mình giải thích thêm?",
            "Đã hiểu rồi. Bạn có thể gửi tiếp câu khác để mình dự đoán hoặc hỏi mình về Naive Bayes."
        ]
    }
]

# Các trả lời linh hoạt theo độ cảm xúc (để chat không lặp lại)
POSITIVE_REPLIES = [
    "Câu này có vẻ tích cực 😊. Bạn muốn mình phân tích thêm không?",
    "Mình thấy nó mang tâm trạng tích cực đấy. Muốn mình gợi ý cách làm cho nó tích cực hơn không?",
    "Rất tích cực! Nếu bạn cần phân tích cụ thể hơn thì cứ nói nhé."
]

NEGATIVE_REPLIES = [
    "Câu này hơi tiêu cực 😟. Bạn muốn mình gợi ý cách viết tích cực hơn không?",
    "Mình thấy ý câu không vui lắm. Muốn mình giúp đổi sang câu tích cực hơn không?",
    "Nó có vẻ tiêu cực. Mình có thể thử đề xuất cách viết tích cực hơn cho bạn."
]

NEUTRAL_REPLIES = [
    "Câu này có vẻ trung tính 🙂. Mình thấy nó không thiên về tích cực hay tiêu cực.",
    "Ý câu khá trung lập, không rõ ràng lắm. Bạn có muốn thử câu khác không?",
    "Nó hơi trung tính. Nếu bạn muốn, mình có thể gợi ý cách làm cho câu rõ ràng hơn."
]

UNKNOWN_REPLIES = [
    "Mình chưa hiểu lắm, bạn thử dùng câu khác nhé.",
    "Có thể mình chưa rõ ý. Bạn thử nhập câu ngắn gọn hơn được không?",
    "Chưa rõ lắm, bạn hãy thử loại câu khác hoặc rõ ràng hơn nhé."
]


def classify_text_with_neutral(text):
    """Classify text and return positive/negative/neutral.

    If the model only has two classes, we treat low-confidence / close predictions as neutral.
    """
    text_vector = vectorizer.transform([text])
    probs = model.predict_proba(text_vector)[0]
    classes = list(model.classes_)

    # Get highest-probability class
    max_idx = int(probs.argmax())
    max_label = classes[max_idx]
    max_prob = float(probs[max_idx])

    # If model is binary, treat low confidence / close probability as neutral
    if len(classes) == 2:
        other_prob = float(probs[1 - max_idx])
        if max_prob < 0.70 or abs(max_prob - other_prob) < 0.12:
            return "neutral", probs, classes

    return max_label, probs, classes


def ensure_database_structure():
    """Ensure the additional tables exist so users can add training samples."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS training_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        label TEXT
        )"""
    )
    conn.commit()
    conn.close()


ensure_database_structure()


def ensure_default_user():
    """Create a default user if no users exist (helps avoid being locked out)."""
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("admin", "admin"),
            )
            conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


ensure_default_user()


def retrain_model():
    global model, vectorizer

    texts = []
    labels = []

    # Load base dataset from CSV
    try:
        with open("data.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                texts.append(row.get("text", ""))
                labels.append(row.get("label", ""))
    except FileNotFoundError:
        pass

    # Load supplemental training data from the database
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT text, label FROM training_data")
        for text, label in cursor.fetchall():
            texts.append(text)
            labels.append(label)
        conn.close()
    except Exception:
        pass

    if not texts or not labels:
        return False

    # Balance classes by oversampling minority labels (helps model learn new labels better)
    try:
        import pandas as _pd
        df = _pd.DataFrame({"text": texts, "label": labels})
        counts = df["label"].value_counts()
        if len(counts) > 1:
            max_count = counts.max()
            extras = []
            for lbl, cnt in counts.items():
                if cnt < max_count:
                    extras.append(df[df["label"] == lbl].sample(max_count - cnt, replace=True, random_state=42))
            if extras:
                df = _pd.concat([df] + extras, ignore_index=True)
                texts = df["text"].tolist()
                labels = df["label"].tolist()
    except Exception:
        # If pandas not available or balancing fails, proceed without balancing
        pass

    vectorizer = CountVectorizer(ngram_range=(1, 2), lowercase=True)
    X = vectorizer.fit_transform(texts)

    model = MultinomialNB()
    model.fit(X, labels)

    # compute simple training accuracy for overview
    try:
        preds = model.predict(X)
        correct = sum(1 for p, t in zip(preds, labels) if p == t)
        global model_accuracy
        model_accuracy = round(correct / len(labels) * 100, 2) if labels else 0.0
    except Exception:
        model_accuracy = 0.0

    # Persist the updated model & vectorizer so the app keeps learning between restarts.
    try:
        with open("vectorizer.pkl", "wb") as f:
            pickle.dump(vectorizer, f)
        with open("naive_bayes_model.pkl", "wb") as f:
            pickle.dump(model, f)
    except Exception:
        pass

    return True


# Ensure we have a usable model when the app starts.
if model is None or vectorizer is None:
    retrain_model()


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()

        # Validation
        errors = []
        
        # Username validation
        if not username or len(username) < 3:
            errors.append("Username phải ít nhất 3 ký tự")
        if not re.match(r"^[a-zA-Z0-9_]{3,}$", username):
            errors.append("Username chỉ chứa chữ, số và gạch dưới")
        
        # Email validation
        if not email or not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            errors.append("Email không hợp lệ")
        
        # Phone validation
        if not phone or not re.match(r"^0\d{9,10}$", phone):
            errors.append("Số điện thoại phải bắt đầu từ 0, 10-11 chữ số")
        
        # Password validation
        if not password or len(password) < 6:
            errors.append("Mật khẩu phải ít nhất 6 ký tự")
        if not re.search(r"[a-zA-Z]", password) or not re.search(r"\d", password):
            errors.append("Mật khẩu phải gồm chữ cái và số")
        
        if errors:
            return render_template("register.html", error=" | ".join(errors))

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
                (username, email, phone, password)
            )
            conn.commit()

        except Exception as e:
            conn.close()
            if "username" in str(e).lower():
                error = "Username đã tồn tại!"
            elif "email" in str(e).lower() or "UNIQUE constraint failed: users.email" in str(e):
                error = "Email đã được đăng ký trước đó!"
            else:
                error = "Lỗi đăng ký. Vui lòng thử lại."
            return render_template("register.html", error=error)

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Allow login via username or email
        cursor.execute(
            "SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
            (username, username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/")
        else:
            error = "Sai tên đăng nhập hoặc mật khẩu."
            return render_template("login.html", error=error, username=username)

    return render_template("login.html")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# FORGOT PASSWORD
# =========================
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Handle forgot password request - send OTP to email"""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        
        if not email:
            return render_template("forgot_password.html", error="Vui lòng nhập email.")
        
        # Check if email exists
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return render_template("forgot_password.html", error="Email không tồn tại trong hệ thống.")
        
        # Generate OTP
        otp = generate_otp()
        
        # Save OTP to database
        expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM otp_codes WHERE email = ?",
            (email,)
        )
        cursor.execute(
            "INSERT INTO otp_codes (email, otp, expires_at) VALUES (?, ?, ?)",
            (email, otp, expires_at.strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        conn.close()
        
        # Send OTP via email
        if send_otp_email(email, otp):
            session["reset_email"] = email
            return redirect("/verify_otp")
        else:
            return render_template("forgot_password.html", 
                                 error="Lỗi gửi email. Vui lòng kiểm tra cấu hình email trong app.py")
    
    return render_template("forgot_password.html")


@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    """Verify OTP code from email"""
    if "reset_email" not in session:
        return redirect("/forgot_password")
    
    if request.method == "POST":
        otp_input = request.form.get("otp", "").strip()
        email = session.get("reset_email")
        
        if not otp_input:
            return render_template("verify_otp.html", error="Vui lòng nhập mã OTP.")
        
        # Verify OTP
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, expires_at FROM otp_codes WHERE email = ? AND otp = ?",
            (email, otp_input)
        )
        otp_record = cursor.fetchone()
        conn.close()
        
        if not otp_record:
            return render_template("verify_otp.html", error="Mã OTP không đúng.")
        
        # Check if OTP expired
        expires_at = datetime.strptime(otp_record[1], '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expires_at:
            return render_template("verify_otp.html", error="Mã OTP đã hết hạn. Vui lòng yêu cầu mã mới.")
        
        # OTP verified, proceed to reset password
        session["otp_verified"] = True
        return redirect("/reset_password")
    
    return render_template("verify_otp.html")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    """Reset password after OTP verification"""
    if "reset_email" not in session or not session.get("otp_verified"):
        return redirect("/forgot_password")
    
    if request.method == "POST":
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        email = session.get("reset_email")
        
        if not password or not confirm_password:
            return render_template("reset_password.html", error="Vui lòng điền đủ thông tin.")
        
        if password != confirm_password:
            return render_template("reset_password.html", error="Mật khẩu không khớp.")
        
        if len(password) < 6:
            return render_template("reset_password.html", error="Mật khẩu phải ít nhất 6 ký tự.")
        
        # Update password
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (password, email))
        conn.commit()
        
        # Clean up OTP
        cursor.execute("DELETE FROM otp_codes WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        
        # Clear session
        session.clear()
        
        return render_template("login.html", message="Mật khẩu đã được đặt lại thành công. Vui lòng đăng nhập.")
    
    return render_template("reset_password.html")


# =========================
# HISTORY
# =========================
@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    msg = None
    if request.args.get("cleared") == "1":
        msg = "Đã xóa lịch sử dự đoán."

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, text, result FROM predictions WHERE user_id=?",
        (session["user_id"],)
    )

    rows = cursor.fetchall()
    conn.close()

    return render_template("history.html", rows=rows, message=msg)


@app.route("/clear_history", methods=["POST"])
def clear_history():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE user_id=?", (session["user_id"],))
    conn.commit()
    conn.close()

    return redirect("/history?cleared=1")


@app.route("/delete_prediction/<int:pred_id>", methods=["POST"])
def delete_prediction(pred_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM predictions WHERE id=? AND user_id=?",
        (pred_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return redirect("/history?deleted=1")


@app.route("/export_history")
def export_history():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT text, result FROM predictions WHERE user_id=? ORDER BY id DESC",
        (session["user_id"],)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "Không có dữ liệu để xuất.", 400

    # Create CSV response
    import io
    output = io.StringIO()
    output.write("Văn bản,Kết quả\n")
    for text, result in rows:
        # Escape quotes and wrap text in quotes if it contains commas
        text_escaped = f'"{text.replace(chr(34), chr(34)+chr(34))}"' if "," in text or '"' in text else text
        result_escaped = f'"{result.replace(chr(34), chr(34)+chr(34))}"' if "," in result or '"' in result else result
        output.write(f'{text_escaped},{result_escaped}\n')

    output.seek(0)
    
    from flask import make_response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=prediction_history.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response


@app.route("/export_training_data")
def export_training_data():
    if "user_id" not in session:
        return redirect("/login")

    texts = []
    labels = []

    # Load base dataset from CSV
    try:
        with open("data.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                texts.append(row.get("text", ""))
                labels.append(row.get("label", ""))
    except FileNotFoundError:
        pass

    # Load from database
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT text, label FROM training_data")
        for text, label in cursor.fetchall():
            texts.append(text)
            labels.append(label)
        conn.close()
    except Exception:
        pass

    if not texts:
        return "Không có dữ liệu huấn luyện để xuất.", 400

    # Create CSV response
    import io
    output = io.StringIO()
    output.write("Văn bản,Nhãn\n")
    for text, label in zip(texts, labels):
        text_escaped = f'"{text.replace(chr(34), chr(34)+chr(34))}"' if "," in text or '"' in text else text
        label_escaped = f'"{label.replace(chr(34), chr(34)+chr(34))}"' if "," in label or '"' in label else label
        output.write(f'{text_escaped},{label_escaped}\n')

    output.seek(0)

    from flask import make_response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=training_data.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response


@app.route("/export_summary")
def export_summary():
    """Export summary statistics of predictions by sentiment."""
    if "user_id" not in session:
        return redirect("/login")

    user_id = session.get("user_id")
    
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # Get counts for current user
        cursor.execute("SELECT result, COUNT(*) as count FROM predictions WHERE user_id = ? GROUP BY result", (user_id,))
        stats = cursor.fetchall()
        conn.close()
        
        # Convert to dict
        counts = {"positive": 0, "negative": 0, "neutral": 0}
        total = 0
        for result, count in stats:
            if result in counts:
                counts[result] = count
                total += count
        
        # Calculate percentages
        percentages = {
            k: round(counts[k] / total * 100, 1) if total > 0 else 0 
            for k in counts
        }
        
        # Create CSV
        import io
        output = io.StringIO()
        output.write("Loại cảm xúc,Số lượng,Phần trăm\n")
        output.write(f"Tích cực (Positive),{counts['positive']},{percentages['positive']}%\n")
        output.write(f"Tiêu cực (Negative),{counts['negative']},{percentages['negative']}%\n")
        output.write(f"Trung tính (Neutral),{counts['neutral']},{percentages['neutral']}%\n")
        output.write(f"Tổng cộng,{total},100%\n")
        
        output.seek(0)
        
        from flask import make_response
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=sentiment_summary.csv"
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        
        return response
        
    except Exception as e:
        return f"Lỗi: {str(e)}", 500


# =========================
# USERS LIST
# =========================
@app.route("/users")
def users():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template("users.html", users=users)


# =========================
# PROFILE
# =========================
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("profile.html", username=session.get("username"))


# =========================
# DASHBOARD + AI
# =========================
@app.route("/", methods=["GET", "POST"])
def home():

    if "user_id" not in session:
        return redirect("/login")

    prediction = ""

    if request.method == "POST":

        text = request.form["text"]

        prediction, _, _ = classify_text_with_neutral(text)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO predictions (user_id, text, result) VALUES (?, ?, ?)",
            (session["user_id"], text, prediction)
        )

        conn.commit()
        conn.close()

    # Count predictions for chart
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT result, COUNT(*) FROM predictions WHERE user_id=? GROUP BY result",
        (session["user_id"],)
    )
    stats = dict(cursor.fetchall())
    conn.close()

    positive_count = stats.get("positive", 0)
    negative_count = stats.get("negative", 0)
    neutral_count = stats.get("neutral", 0)

    # Overall stats
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    # Recent training samples (latest 6)
    cursor.execute("SELECT text, label FROM training_data ORDER BY id DESC LIMIT 6")
    recent_samples = cursor.fetchall()
    conn.close()

    # Dataset size: training data + base csv
    dataset_size = 0
    try:
        with open("data.csv", encoding="utf-8") as f:
            dataset_size += sum(1 for _ in f) - 1
    except Exception:
        pass
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM training_data")
        dataset_size += cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass

    from datetime import datetime
    trained_at = datetime.now().strftime("%d/%m/%Y")

    return render_template(
        "dashboard.html",
        prediction=prediction,
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count,
        dataset_size=dataset_size,
        model_accuracy=model_accuracy,
        total_users=total_users,
        total_predictions=total_predictions,
        recent_samples=recent_samples,
        trained_at=trained_at,
    )


@app.route("/dataset", methods=["GET", "POST"])
def dataset():

    if "user_id" not in session:
        return redirect("/login")

    msg = None

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        label = request.form.get("label", "").strip()
        if text and label:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO training_data (text, label) VALUES (?, ?)",
                (text, label)
            )
            conn.commit()
            conn.close()

        # Tự động tái huấn luyện ngay khi thêm dữ liệu mới
        retrain_model()

        msg = "Đã thêm dữ liệu và tái huấn luyện mô hình thành công."

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT text, label FROM training_data ORDER BY id DESC LIMIT 150")
    samples = cursor.fetchall()
    conn.close()

    return render_template("dataset.html", samples=samples, message=msg)


@app.route("/retrain", methods=["POST"])
def retrain():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Vui lòng đăng nhập."}), 401

    ok = retrain_model()
    if ok:
        return jsonify({"success": True, "message": "Đã tái huấn luyện mô hình."})
    return jsonify({"success": False, "message": "Không có dữ liệu để tái huấn luyện."})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"reply": "Vui lòng gửi tin nhắn trước."})

    msg_lower = message.lower()

    # Trả lời theo knowledge base (cho cảm giác giống chat GPT hơn)
    for item in CHAT_KB:
        if any(trigger in msg_lower for trigger in item["triggers"]):
            return jsonify({"reply": random.choice(item["responses"])})

    # Nếu user muốn phân tích thêm dựa trên dự đoán gần nhất
    if any(k in msg_lower for k in ["phân tích", "phan tich", "giải thích", "analysis", "analyze"]):
        last = session.get("last_sentiment")
        if last == "positive":
            return jsonify({
                "reply": (
                    "Mình dự đoán câu này tích cực bởi nó chứa các từ như 'tốt', 'tuyệt', 'hài lòng', 'đẹp', 'thích'...\n"
                    "Nếu bạn muốn mình gợi ý cách viết tích cực hơn, hãy gửi một câu khác nhé."
                )
            })
        if last == "negative":
            return jsonify({
                "reply": (
                    "Mình thấy câu này hơi tiêu cực vì có các từ như 'tệ', 'thất vọng', 'không', 'bực'.\n"
                    "Bạn có thể gửi câu khác để mình gợi ý cách viết tích cực hơn."
                )
            })
        if last == "neutral":
            return jsonify({
                "reply": (
                    "Mình nghĩ câu này ở mức trung tính, không rõ ràng tích cực hay tiêu cực.\n"
                    "Bạn có thể thử viết lại để làm rõ cảm xúc hơn, hoặc gửi thêm câu khác."
                )
            })
        return jsonify({"reply": "Bạn hãy gửi một câu để mình phân tích cảm xúc cho bạn nhé!"})

    # Default: trả về dự đoán cảm xúc như một chatbot (mang tính gợi ý)
    try:
        prediction, _, _ = classify_text_with_neutral(message)
        session["last_sentiment"] = prediction

        if prediction == "positive":
            reply = random.choice(POSITIVE_REPLIES)
        elif prediction == "negative":
            reply = random.choice(NEGATIVE_REPLIES)
        elif prediction == "neutral":
            reply = random.choice(NEUTRAL_REPLIES)
        else:
            reply = f"Mình đoán đây là: {prediction}. Bạn có thể nhập thêm câu khác để mình thử nhé."
    except Exception:
        reply = random.choice(UNKNOWN_REPLIES)

    return jsonify({"reply": reply})


@app.route("/test_model", methods=["GET", "POST"])
def test_model():
    if "user_id" not in session:
        return redirect("/login")

    result = None
    input_text = ""

    if request.method == "POST":
        input_text = request.form.get("text", "").strip()
        if input_text:
            try:
                prediction, probabilities, classes = classify_text_with_neutral(input_text)
                confidence = max(probabilities)
                result = {
                    "prediction": prediction,
                    "confidence": round(confidence * 100, 2),
                    "probabilities": {cls: round(prob, 4) for cls, prob in zip(classes, probabilities)}
                }
            except Exception as e:
                result = {"error": str(e)}

    examples = []
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT text, label FROM training_data ORDER BY id DESC LIMIT 6")
        examples = cursor.fetchall()
        conn.close()
    except Exception:
        pass

    return render_template("test_model.html", result=result, input_text=input_text, examples=examples)


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)