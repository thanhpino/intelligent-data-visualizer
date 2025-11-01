# 🚀 Dự án Trực quan hóa Dữ liệu Thông minh

Đây là một trang web cho phép người dùng upload và phân tích các bộ dữ liệu một cách nhanh chóng. Hệ thống sẽ tự động đưa ra các gợi ý phân tích, giúp người dùng khám phá thông tin ẩn sau những con số mà không cần kiến thức chuyên sâu.

## ✨ Tính năng chính

-   **Gợi ý phân tích tự động:** Dựa vào kiểu dữ liệu (số, chữ) để đưa ra các phân tích phù hợp.
-   **Trực quan hóa tức thì:** Hiển thị kết quả dưới dạng biểu đồ Cột hoặc Tròn ngay lập tức.
-   **Giao diện hiện đại:** Sử dụng Next.js và Tailwind CSS.

## ⚙️ Công nghệ sử dụng

-   **Backend:** Python, FastAPI, Pandas
-   **Frontend:** Next.js (React), Chart.js, Tailwind CSS

## 🏃 Cách chạy dự án tại local

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload