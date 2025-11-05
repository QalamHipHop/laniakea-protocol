"""
Laniakea Protocol - Wallet System
سیستم کیف پول و مدیریت کلیدهای رمزنگاری
"""

import os
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature


class Wallet:
    """
    کیف پول برای مدیریت کلیدهای خصوصی و عمومی
    """

    def __init__(self, data_dir: str):
        """
        Args:
            data_dir: مسیر ذخیره‌سازی کیف پول
        """
        wallet_file = os.path.join(data_dir, "wallet.pem")
        os.makedirs(data_dir, exist_ok=True)

        # بارگذاری یا ایجاد کلید خصوصی
        if os.path.exists(wallet_file):
            try:
                with open(wallet_file, "rb") as f:
                    # تلاش برای بارگذاری با رمز عبور
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=b"Laniakea_Protocol_Secret_Key"
                    )
                print(f"🔓 Wallet loaded from {wallet_file} (Encrypted)")
            except ValueError:
                # اگر رمزگذاری نشده باشد، بدون رمز عبور بارگذاری کن
                with open(wallet_file, "rb") as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
                print(f"🔓 Wallet loaded from {wallet_file} (Unencrypted)")
            except TypeError:
                # اگر رمزگذاری نشده باشد، بدون رمز عبور بارگذاری کن
                with open(wallet_file, "rb") as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
                print(f"🔓 Wallet loaded from {wallet_file} (Unencrypted - Recovered)")
        else:
            # ایجاد کلید جدید
            self.private_key = ec.generate_private_key(ec.SECP256R1())

            # ذخیره کلید
            with open(wallet_file, "wb") as f:
                f.write(
                    self.private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.BestAvailableEncryption(b"Laniakea_Protocol_Secret_Key")
                    )
                )
            print(f"🔐 New wallet created at {wallet_file}")

        # استخراج کلید عمومی
        self.public_key = self.private_key.public_key()

        # تولید شناسه نود
        self.node_id = self._get_node_id()

        # تنظیم متغیر محیطی
        os.environ["MY_NODE_ID"] = self.node_id

        print(f"🔑 Wallet initialized. Node ID: {self.node_id[:12]}...")

    def _get_node_id(self) -> str:
        """
        تولید شناسه نود از کلید عمومی
        
        Returns:
            شناسه نود (hex)
        """
        pub_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint
        )
        return hashlib.sha256(pub_key_bytes).hexdigest()

    def sign(self, data: bytes) -> str:
        """
        امضای داده
        
        Args:
            data: داده برای امضا
        
        Returns:
            امضای hex
        """
        signature = self.private_key.sign(
            data,
            ec.ECDSA(hashes.SHA256())
        )
        return signature.hex()

    @staticmethod
    def verify(
        public_key: ec.EllipticCurvePublicKey,
        signature_hex: str,
        data: bytes
    ) -> bool:
        """
        اعتبارسنجی امضا
        
        Args:
            public_key: کلید عمومی
            signature_hex: امضای hex
            data: داده اصلی
        
        Returns:
            True اگر امضا معتبر باشد
        """
        try:
            public_key.verify(
                bytes.fromhex(signature_hex),
                data,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except (InvalidSignature, ValueError):
            return False

    def get_public_key_pem(self) -> str:
        """
        دریافت کلید عمومی به فرمت PEM
        
        Returns:
            کلید عمومی PEM
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def get_address(self) -> str:
        """
        دریافت آدرس کیف پول (همان node_id)
        
        Returns:
            آدرس
        """
        return self.node_id
