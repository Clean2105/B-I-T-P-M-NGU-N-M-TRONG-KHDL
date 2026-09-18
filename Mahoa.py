import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecureDataEngine:
    def __init__(self, secret_passphrase: str):
        """
        Khởi tạo động cơ mã hóa. Tự động chuyển đổi mật khẩu thành khóa 256-bit chuẩn AES bằng SHA-256.
        """
        self.key = hashlib.sha256(secret_passphrase.encode('utf-8')).digest()
        self.aesgcm = AESGCM(self.key)

    def encrypt_data(self, plaintext: bytes) -> tuple[bytes, bytes]:
        """
        Mã hóa dữ liệu thô sang dạng Ciphertext an toàn.
        Trả về (nonce, ciphertext).
        """
        # Tạo nonce ngẫu nhiên 12 bytes (96 bits) chuẩn AES-GCM
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        return nonce, ciphertext

    def decrypt_data(self, nonce: bytes, ciphertext: bytes) -> bytes:
        """
        Giải mã dữ liệu. Nếu bị hacker can thiệp biến đổi nội dung, hàm sẽ ném ra lỗi cryptography.exceptions.InvalidTag.
        """
        return self.aesgcm.decrypt(nonce, ciphertext, None)

    @staticmethod
    def calculate_checksum(data: bytes) -> str:
        """
        Tính toán mã băm SHA-256 kiểm tra toàn vẹn gói tin.
        """
        return hashlib.sha256(data).hexdigest()


# ==========================================
# THỬ NGHIỆM KỊCH BẢN BẢO MẬT & CHỐNG HACKER
# ==========================================
if __name__ == "__main__":
    print("=== HỆ THỐNG MÃ HÓA BẢO MẬT DỮ LIỆU AES-256-GCM ===")
    
    # 1. Định nghĩa dữ liệu cần bảo vệ & Khóa bảo mật
    secret_passphrase = "HUTECH_DataScience_SecretKey_2026"
    original_message = "CẢNH BÁO: Thông tin hệ thống mạng và hạ tầng dữ liệu nội bộ nghiêm cấm truy cập!"
    data_bytes = original_message.encode('utf-8')

    # Khởi tạo Engine
    crypto_engine = SecureDataEngine(secret_passphrase)

    # 2. Thực hiện mã hóa dữ liệu
    print(f"\n[1] Thông điệp gốc: {original_message}")
    original_hash = crypto_engine.calculate_checksum(data_bytes)
    print(f"    Mã băm SHA-256 (Gốc): {original_hash}")

    nonce, ciphertext = crypto_engine.encrypt_data(data_bytes)
    print(f"\n[2] Dữ liệu sau mã hóa (Hex): {ciphertext.hex()[:60]}...")
    print(f"    Mã Nonce ngẫu nhiên: {nonce.hex()}")

    # 3. Giả lập giải mã hợp lệ (Người dùng hợp pháp)
    try:
        decrypted_bytes = crypto_engine.decrypt_data(nonce, ciphertext)
        decrypted_message = decrypted_bytes.decode('utf-8')
        decrypted_hash = crypto_engine.calculate_checksum(decrypted_bytes)
        
        print(f"\n[3] Giải mã thành công!")
        print(f"    Nội dung khôi phục: {decrypted_message}")
        print(f"    Kiểm tra Integrity Hash: {'HOÀN HẢO' if original_hash == decrypted_hash else 'LỖI'}")
    except Exception as e:
        print(f"[!] Giải mã thất bại: {e}")

    # 4. Giả lập tấn công: Hacker cố tình sửa đổi 1 byte dữ liệu trên đường truyền
    print("\n[4] Mô phỏng tấn công: Hacker sửa đổi dữ liệu mã hóa...")
    tampered_ciphertext = bytearray(ciphertext)
    tampered_ciphertext[0] ^= 0xFF  # Bị chỉnh sửa dữ liệu

    try:
        crypto_engine.decrypt_data(nonce, bytes(tampered_ciphertext))
    except Exception:
        print("    --> PHÁT HIỆN TẤN CÔNG: Hệ thống phát hiện dữ liệu bị sửa đổi và TỰ ĐỘNG HỦY GÓI TIN!")