import asyncio
import random
import pandas as pd
import matplotlib.pyplot as plt
from playwright.async_api import async_playwright

async def scrape_kali_website():
    url = "https://kali.org"
    print(f"Đang kết nối và cào dữ liệu từ Kali Linux: {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Giả lập User-Agent để tránh bị chặn hoặc timeout
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("domcontentloaded")
            
            articles_data = []
            # Định vị các tiêu đề bài viết (thường nằm trong thẻ h4 ở mục Blog)
            blog_section_titles = page.locator("h4") 
            titles_count = await blog_section_titles.count()
            
            for i in range(titles_count):
                title = await blog_section_titles.nth(i).inner_text()
                title = title.strip()
                
                # Lọc các tiêu đề bài viết thực tế dựa trên từ khóa xuất hiện trên trang chủ
                if title and len(title) > 10 and ("Kali" in title or "LLM" in title or "Release" in title): 
                    # Thu thập độ dài tiêu đề và giả lập số lượt xem (Views) để phục vụ vẽ biểu đồ
                    doc_dai = len(title)
                    views_gia_lap = random.randint(500, 5000)
                    
                    articles_data.append({
                        "STT": len(articles_data) + 1,
                        "Tiêu Đề Bài Viết": title,
                        "Độ Dài Tiêu Đề (Ký tự)": doc_dai,
                        "Lượt Xem (Giả lập)": views_gia_lap
                    })
            
            print(f" Thu thập thành công {len(articles_data)} bài viết từ Kali Linux.")
            return articles_data
        except Exception as e:
            print(f"Có lỗi xảy ra trong quá trình quét dữ liệu: {e}")
            return []
        finally:
            await context.close()
            await browser.close()

def export_and_draw_charts(data_list, filename="kali_news_data.xlsx"):
    if not data_list:
        print("Không có dữ liệu để xuất file và vẽ biểu đồ.")
        return
        
    # 1. XUẤT FILE EXCEL (.xlsx)
    df = pd.DataFrame(data_list)
    df.to_excel(filename, index=False, sheet_name="Kali Blog")
    print(f" Đã xuất danh sách thành công vào file Excel: '{filename}'")
    
    # Cấu hình font hiển thị tiếng Việt cho đồ thị
    plt.rcParams["font.family"] = "DejaVu Sans"
    
    # Khởi tạo khung chứa 2 biểu đồ (1 hàng, 2 cột)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Tạo nhãn rút gọn cho các bài viết để biểu đồ không bị đè chữ (Ví dụ: Bài 1, Bài 2...)
    labels = [f"Bài {row['STT']}" for _, row in df.iterrows()]
    
    # 2. VẼ BIỂU ĐỒ CỘT (Độ dài tiêu đề)
    ax1.bar(labels, df["Độ Dài Tiêu Đề (Ký tự)"], color="royalblue", edgecolor="black", alpha=0.8)
    ax1.set_title("Biểu đồ cột: Độ dài tiêu đề bài viết", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Bài viết", fontsize=10)
    ax1.set_ylabel("Số lượng ký tự", fontsize=10)
    ax1.grid(True, linestyle="--", alpha=0.5, axis='y')
    
    # Thêm số liệu cụ thể lên trên đầu mỗi cột
    for i, val in enumerate(df["Độ Dài Tiêu Đề (Ký tự)"]):
        ax1.text(i, val + 1, str(val), ha='center', fontsize=9)

    # 3. VẼ BIỂU ĐỒ PHÂN TÁN (Mối tương quan Độ dài tiêu đề vs Lượt xem)
    ax2.scatter(df["Độ Dài Tiêu Đề (Ký tự)"], df["Lượt Xem (Giả lập)"], color="crimson", s=150, edgecolor="black", alpha=0.8)
    ax2.set_title("Biểu đồ phân tán: Độ dài tiêu đề vs Lượt xem", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Độ dài tiêu đề (Ký tự)", fontsize=10)
    ax2.set_ylabel("Số lượt xem (Giả lập)", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    # Đính kèm nhãn mã số bài viết kế bên mỗi điểm chấm tọa độ
    for _, row in df.iterrows():
        ax2.text(row["Độ Dài Tiêu Đề (Ký tự)"] + 1, row["Lượt Xem (Giả lập)"] + 50, f"Bài {row['STT']}", fontsize=9)
        
    plt.tight_layout()
    print(" Đang hiển thị các biểu đồ...")
    plt.show()

async def main():
    data = await scrape_kali_website()
    export_and_draw_charts(data)

if __name__ == "__main__":
    asyncio.run(main())
