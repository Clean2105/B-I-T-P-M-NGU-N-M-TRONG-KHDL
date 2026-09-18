import os
import time
import numpy as np
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 1. Khởi tạo dữ liệu thử nghiệm
payload = b"HUTECH Data Security System - Confidential Payload" * 100
num_trials = 1000

time_128 = []
time_256 = []

# 2. Đo thời gian mã hóa AES-128 và AES-256
for _ in range(num_trials):
    # Tạo nonce 12 bytes chuẩn cho AES-GCM bằng os.urandom
    nonce = os.urandom(12)
    
    # AES-128
    key_128 = AESGCM.generate_key(bit_length=128)
    aesgcm_128 = AESGCM(key_128)
    start = time.perf_counter()
    aesgcm_128.encrypt(nonce, payload, None)
    time_128.append((time.perf_counter() - start) * 1e6)
    
    # AES-256
    key_256 = AESGCM.generate_key(bit_length=256)
    aesgcm_256 = AESGCM(key_256)
    start = time.perf_counter()
    aesgcm_256.encrypt(nonce, payload, None)
    time_256.append((time.perf_counter() - start) * 1e6)

# Xử lý thống kê với NumPy
arr_128 = np.array(time_128)
arr_256 = np.array(time_256)

mean_128, std_128 = np.mean(arr_128), np.std(arr_128)
mean_256, std_256 = np.mean(arr_256), np.std(arr_256)

print(f"AES-128: Trung bình = {mean_128:.2f} µs | Độ lệch chuẩn = {std_128:.2f} µs")
print(f"AES-256: Trung bình = {mean_256:.2f} µs | Độ lệch chuẩn = {std_256:.2f} µs")

# 3. Trực quan hóa với Matplotlib
labels = ['AES-128 Bit', 'AES-256 Bit (Khuyến nghị)']
means = [mean_128, mean_256]
stds = [std_128, std_256]

plt.figure(figsize=(8, 5))
bars = plt.bar(labels, means, yerr=stds, capsize=8, color=['#3498db', '#e74c3c'], alpha=0.85)

plt.ylabel('Thời gian xử lý (Microseconds µs)')
plt.title('So sánh Hiệu năng Mã hóa AES chống Hacker')
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval:.2f} µs', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.show()