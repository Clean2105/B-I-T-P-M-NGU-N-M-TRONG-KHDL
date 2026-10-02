import asyncio
import re  # Đã đưa import re lên đầu file để tránh lỗi NameError
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from playwright.async_api import async_playwright

async def scrape_dhcnhn_journal():
    # SỬA LỖI: Đường dẫn URL mục tiêu chính xác của Tạp chí ĐH Công nghiệp Hà Nội
    url = "https://vjol.info.vn/dhcnhn/en/"
    print(f"Đang kết nối và cào dữ liệu mục tiêu từ: {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, timeout=60000)
            
            # Chờ một trong các thẻ chứa bài viết tải xong
            await page.wait_for_selector("h4.title a, .obj_article_summary, .articles", timeout=45000)
            
            articles_data = []
            
            # Định vị tất cả các thẻ liên kết tiêu đề bài viết đang hiển thị
            article_links = page.locator("h4.title a")
            titles_count = await article_links.count()
            
            print(f"Hệ thống tìm thấy {titles_count} bài viết thực tế.")
            
            for i in range(titles_count):
                link_elem = article_links.nth(i)
                
                # 1. Thu thập Tiêu đề
                title = await link_elem.inner_text()
                title = title.strip()
                
                # 2. Thu thập URL thực tế và chuẩn hóa link tuyệt đối
                href = await link_elem.get_attribute("href")
                article_url = href if href.startswith("http") else f"https://vjol.info.vn{href}"
                
                # 3. Thu thập Tác giả và dải trang từ khối bao bọc bài viết (.obj_article_summary)
                parent_block = page.locator(".obj_article_summary").nth(i)
                
                authors_elem = parent_block.locator(".authors")
                authors = await authors_elem.inner_text() if await authors_elem.count() > 0 else "N/A"
                authors = authors.strip()
                
                pages_elem = parent_block.locator(".pages")
                pages_text = await pages_elem.inner_text() if await pages_elem.count() > 0 else "0"
                pages_text = pages_text.strip()
                
                # Trích xuất số trang bắt đầu bằng Regex cơ bản
                digits = [int(s) for s in re.findall(r'\d+', pages_text)]
                start_page = digits[0] if digits else 0
                
                articles_data.append({
                    "Tiêu Đề Bài Viết": title,
                    "Tác Giả": authors,
                    "Trang Bắt Đầu": start_page,
                    "Đường Link Bài Viết": article_url
                })
                
            return articles_data
            
        except Exception as e:
            print(f"Lỗi phân tích DOM hoặc đường truyền mạng: {e}")
            return []
        finally:
            await browser.close()

def process_data_and_plot(data_list, filename="vjol_dhcnhn_numpy_data.xlsx"):
    if not data_list:
        print("Không có dữ liệu đầu vào. Vui lòng kiểm tra lại kết nối mạng hoặc URL.")
        return
        
    # --- XỬ LÝ MẢNG DỮ LIỆU BẰNG NUMPY ---
    pages_array = np.array([item["Trang Bắt Đầu"] for item in data_list])
    
    # Nếu dải trang cào về bị trống (bằng 0), tự động điền vị trí tịnh tiến bằng np.arange
    if np.all(pages_array == 0):
        pages_array = np.arange(3, 3 + len(data_list) * 8, 8)
        for i, page_num in enumerate(pages_array):
            data_list[i]["Trang Bắt Đầu"] = int(page_num)
            
    # Tạo ngẫu nhiên số lượt xem bằng phân phối chuẩn khoa học (Mean=320, Std=90) thông qua NumPy
    np.random.seed(50)
    views_array = np.random.normal(loc=320, scale=90, size=len(data_list)).astype(int)
    views_array = np.clip(views_array, 30, 650) # Giới hạn dải từ 30 đến 650 lượt xem
    
    # Tính độ dài chuỗi tiêu đề bằng NumPy array
    title_lengths = np.array([len(item["Tiêu Đề Bài Viết"]) for item in data_list])
    
    # Cập nhật số liệu tính từ NumPy vào danh sách xuất Excel
    for i in range(len(data_list)):
        data_list[i]["STT"] = i + 1
        data_list[i]["Số Ký Tự Tiêu Đề"] = int(title_lengths[i])
        data_list[i]["Lượt Xem (NumPy)"] = int(views_array[i])
        
    # --- XUẤT TỆP EXCEL (.XLSX) ---
    df = pd.DataFrame(data_list)
    layout = ["STT", "Tiêu Đề Bài Viết", "Tác Giả", "Trang Bắt Đầu", "Số Ký Tự Tiêu Đề", "Lượt Xem (NumPy)", "Đường Link Bài Viết"]
    df = df[layout]
    
    df.to_excel(filename, index=False, sheet_name="VJOL HaUI Analytics")
    print(f" Xuất file Excel thành công, đã nhúng link thật tại: '{filename}'")
    
    # --- VẼ BIỂU ĐỒ PHÂN TÁN BONG BÓNG ---
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.figure(figsize=(11, 6))
    
    # Biểu đồ phân tán có kích thước chấm (s) thay đổi dựa trên độ dài tiêu đề bài viết
    plt.scatter(
        pages_array, 
        views_array, 
        color="royalblue", 
        s=title_lengths * 2.5, 
        alpha=0.7, 
        edgecolors="black",
        label="Bài báo khoa học"
    )
    
    # Đánh nhãn số thứ tự bài báo sát bên cạnh chấm điểm tọa độ
    for i in range(len(data_list)):
        plt.text(pages_array[i] + 1.2, views_array[i] + 2, f"Bài {i+1}", fontsize=9, weight='bold')
        
    plt.title("Biểu đồ phân tán: Phân bổ Vị trí trang & Lượt truy cập (HaUI Journal)", fontsize=12, fontweight='bold')
    plt.xlabel("Vị trí trang bắt đầu (Page Start)", fontsize=11)
    plt.ylabel("Lượt xem bài viết (Views)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper right")
    
    plt.tight_layout()
    print("Đang hiển thị biểu đồ phân tán dạng bong bóng dữ liệu...")
    plt.show()

async def main():
    records = await scrape_dhcnhn_journal()
    process_data_and_plot(records)

if __name__ == "__main__":
    asyncio.run(main())