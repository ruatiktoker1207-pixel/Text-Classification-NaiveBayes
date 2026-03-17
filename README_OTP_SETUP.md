# Hướng dẫn cấu hình OTP và quên mật khẩu

## Các tính năng được thêm

1. **Đăng ký với Email và Số điện thoại**
   - Người dùng bây giờ phải nhập email và số điện thoại khi đăng ký
   - Email được lưu để sử dụng cho quên mật khẩu

2. **Quên mật khẩu với OTP**
   - Người dùng có thể yêu cầu mã OTP thông qua email
   - Mã OTP có hiệu lực trong 10 phút
   - Sau khi xác minh OTP, người dùng có thể đặt lại mật khẩu

## Hướng dẫn thiết lập Email

### Bước 1: Bật 2-Step Verification trên Google Account
1. Truy cập https://myaccount.google.com
2. Chọn "Security" (Bảo mặt)
3. Bật "2-Step Verification" (Xác minh 2 bước)

### Bước 2: Tạo App-Specific Password
1. Truy cập https://myaccount.google.com/apppasswords
2. Chọn "Mail" trong Application
3. Chọn "Windows Computer" (hoặc thiết bị của bạn) trong Select Device
4. Google sẽ hiển thị mật khẩu 16 ký tự (dạng: xxxx xxxx xxxx xxxx)
5. Copy mật khẩu này

### Bước 3: Cấu hình trong ứng dụng
1. Mở file `config_email.py`
2. Thay thế:
   - `your_email@gmail.com` bằng địa chỉ Gmail của bạn
   - `xxxx xxxx xxxx xxxx` bằng mật khẩu app-specific vừa nhận được
3. Lưu file

### Ví dụ:
```python
EMAIL_ADDRESS = "myemail@gmail.com"
EMAIL_PASSWORD = "abcd efgh ijkl mnop"
```

## Cơ sở dữ liệu

Đã thêm:
- Cột `email` và `phone` vào bảng `users`
- Bảng `otp_codes` để lưu mã OTP tạm thời

## Route mới

- GET/POST `/forgot_password` - Yêu cầu mã OTP
- GET/POST `/verify_otp` - Xác minh mã OTP
- GET/POST `/reset_password` - Đặt lại mật khẩu

## Lưu ý bảo mật

- Mật khẩu app-specific Google khác với mật khẩu Gmail thông thường
- Chỉ sử dụng mật khẩu app-specific trong ứng dụng
- Không chia sẻ `config_email.py` công khai
- OTP sẽ tự động xóa sau 10 phút hoặc khi được sử dụng
