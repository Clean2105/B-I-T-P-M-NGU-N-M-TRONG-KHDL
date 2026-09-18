import os
import time
import numpy as np
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 1. Khởi tạo dữ liệu kiểm thử
# Tải giả lập gói tin dữ liệu nhạy cảm (10 KB)
payload = os.urandom(1024 * 10)  
num_trials = 500  # Số lần mã hóa để lấy mẫu thống kê

times_aes128 = []
times_aes256 = []

# 2. Đo thời gian mã hóa AES-128 vs AES-256
for _ in range(num_trials):
    nonce = os.urandom(12)  # Nonce 96-bit tiêu chuẩn cho AES-GCM
    
    # --- AES-128 Bit ---
    key_128 = AESGCM.generate_key(bit_length=128)
    cipher_128 = AESGCM(key_128)
    t0 = time.perf_counter()
    cipher_128.encrypt(nonce, payload, None)
    times_aes128.append((time.perf_counter() - t0) * 1e6)  # Đổi sang Microseconds (µs)

    # --- AES-256 Bit (Khuyến nghị chống Hacker) ---
    key_256 = AESGCM.generate_key(bit_length=256)
    cipher_256 = AESGCM(key_256)
    t0 = time.perf_counter()
    cipher_256.encrypt(nonce, payload, None)
    times_aes256.append((time.perf_counter() - t0) * 1e6)

# 3. Tính toán chỉ số thống kê bằng NumPy
arr_128 = np.array(times_aes128)
arr_256 = np.array(times_aes256)

mean_128, std_128 = np.mean(arr_128), np.std(arr_128)
mean_256, std_256 = np.mean(arr_256), np.std(arr_256)

# 4. Vẽ biểu đồ phân tích bằng Matplotlib
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Biểu đồ 1: Cột so sánh thời gian trung bình (Bar Chart)
algorithms = ['AES-128 Bit', 'AES-256 Bit\n(An toàn cao)']
means = [mean_128, mean_256]
stds = [std_128, std_256]
colors = ['#2ecc71', '#e74c3c']

bars = ax1.bar(algorithms, means, yerr=stds, capsize=8, color=colors, alpha=0.85, edgecolor='black')
ax1.set_ylabel('Thời gian thực thi trung bình (µs)', fontsize=11)
ax1.set_title('Hiệu năng Mã hóa Gói tin (Độ trễ trung bình)', fontsize=12, fontweight='bold')

for bar in bars:
    height = bar.get_height()
    ax1.annotate(f'{height:.2f} µs',
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 5), textcoords="offset points",
                 ha='center', va='bottom', fontweight='bold')

# Biểu đồ 2: Phân phối thời gian mã hóa qua 500 lần chạy (Line Chart)
ax2.plot(arr_128, label='AES-128', color='#2ecc71', alpha=0.6, linewidth=1)
ax2.plot(arr_256, label='AES-256', color='#e74c3c', alpha=0.6, linewidth=1)
ax2.set_xlabel('Lần thử nghiệm (Trial)', fontsize=11)
ax2.set_ylabel('Thời gian xử lý (µs)', fontsize=11)
ax2.set_title('Biến động thời gian mã hóa (500 Mẫu)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper right')

plt.suptitle('ĐÁNH GIÁ HIỆU NĂNG MÃ HÓA AES CHỐNG XÂM NHẬP', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()

# Lưu biểu đồ thành file ảnh và hiển thị
plt.savefig('D:/Projects/bieudo_mahoa.png', dpi=300, bbox_inches='tight')
plt.show()