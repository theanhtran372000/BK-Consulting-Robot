# BK Consulting Robot Server
Source code cho **backend server** (*Khối quản trị*) trong hệ thống BKBot.

## 1. Thiết lập môi trường
- Tạo môi trường ảo
```
python -m venv venv
```
- Kích hoạt môi trường ảo
```
source venv/bin/activate # For linux
.\venv\Scripts\activate
```
- Cài đặt các thư viện cần thiết
```
pip install -r requirements.txt
```

## 2. Chạy chương trình
File `configs.yml` chứa những configs cần thiết để thiết lập server. Sau đó, chạy server bằng câu lệnh sau:
```
bash scripts/run.sh
```

Server đang được chạy tại [34.142.132.0:9000](34.142.132.0:9000).