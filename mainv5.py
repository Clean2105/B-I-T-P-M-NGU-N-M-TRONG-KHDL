import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def scrape_kali_website():
    url = "https://www.kali.org/"
    print(f"Đang kết nối và cào dữ liệu từ Kali Linux: {url}...")
    
    async with async_playwright() as p:
        # Cấu hình Chromium chạy ở chế độ ẩn danh và thêm các tham số giảm tải chặn bot
        browser = await p.chromium.launch(headless=True)
        
        # Thêm User-Agent giả lập trình duyệt Chrome thông thường trên Windows
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Truy cập trang web Kali Linux
            await page.goto(url, timeout=60000)
            
            # Thay vì đợi một selector cụ thể dễ bị kẹt, ta đợi cấu trúc DOM của trang tải xong hoàn toàn
            await page.wait_for_load_state("domcontentloaded")
            
            articles_data = []
            
            # Định vị khu vực tin tức (Blog) sử dụng lớp hoặc thẻ có cấu trúc phân cấp ổn định hơn
            # Các bài viết của Kali nằm trong các thẻ h4 thuộc phần tin tức bài viết
            blog_section_titles = page.locator("h4") 
            titles_count = await blog_section_titles.count()
            
            print(f"Tìm thấy {titles_count} thẻ tiêu đề h4 trên trang chủ Kali.")
            
            for i in range(titles_count):
                title = await blog_section_titles.nth(i).inner_text()
                title = title.strip()
                
                # Chỉ lọc lấy các tiêu đề bài viết thực tế (thường chứa chữ 'Kali' hoặc có độ dài ký tự hợp lý)
                if title and len(title) > 10 and ("Kali" in title or "LLM" in title or "Release" in title): 
                    articles_data.append({
                        "STT": len(articles_data) + 1,
                        "Tiêu Đề Bài Viết": title
                    })
            
            return articles_data
        except Exception as e:
            print(f"Có lỗi xảy ra trong quá trình quét dữ liệu: {e}")
            return []
        finally:
            await context.close()
            await browser.close()

def export_to_excel(data_list, filename="kali_data.xlsx"):
    if not data_list:
        print("Không thu thập được dữ liệu để xử lý.")
        return
    df = pd.DataFrame(data_list)
    df.to_excel(filename, index=False, sheet_name="Kali Info")
    print(f"Đã xuất danh sách thành công vào file Excel: '{filename}'")

async def main():
    data = await scrape_kali_website()
    export_to_excel(data)

if __name__ == "__main__":
    asyncio.run(main())
