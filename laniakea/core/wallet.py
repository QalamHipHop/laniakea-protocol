"""
Laniakea Protocol - Wallet System (Enhanced & Secure)
سیستم کیف پول و مدیریت کلیدهای رمزنگاری - نسخه امن

تغییرات نسخه v0.0.01:
- رفع مشکل hardcoded encryption key
- استفاده از متغیرهای محیطی
- بهبود امنیت و مدیریت خطا
"""

import os
import hashlib
import secrets
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature


class Wallet:
    """
    کیف پول امن برای مدیریت کلیدهای خصوصی و عمومی

    ویژگی‌های امنیتی:
    - استفاده از متغیر محیطی برای encryption key
    - تولید خودکار کلید امن در صورت عدم وجود
    - پشتیبانی از الگوریتم SECP256R1
    """

    DEFAULT_ENCRYPTION_KEY_ENV = "LANIAKEA_WALLET_KEY"

    def __init__(self, data_dir: str):
        """
        راه‌اندازی کیف پول

        Args:
            data_dir: مسیر ذخیره‌سازی کیف پول
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.wallet_file = self.data_dir / "wallet.pem"
        self.private_key: Optional[ec.EllipticCurvePrivateKey] = None
        self.public_key: Optional[ec.EllipticCurvePublicKey] = None
        self.node_id: str = ""

        # دریافت یا تولید کلید رمزنگاری
        self.encryption_key = self._get_encryption_key()

        # بارگذاری یا ایجاد کیف پول
        self._initialize_wallet()

        # تنظیم متغیر محیطی برای استفاده در سایر ماژول‌ها
        os.environ["MY_NODE_ID"] = self.node_id

        print(f"🔑 Wallet initialized. Node ID: {self.node_id[:16]}...")

    def _get_encryption_key(self) -> bytes:
        """
        دریافت کلید رمزنگاری از متغیر محیطی یا تولید جدید

        Returns:
            کلید رمزنگاری به صورت bytes
        """
        # تلاش برای خواندن از متغیر محیطی
        key_from_env = os.environ.get(self.DEFAULT_ENCRYPTION_KEY_ENV)

        if key_from_env:
            # استفاده از کلید موجود
            return key_from_env.encode("utf-8")

        # تولید کلید جدید و ذخیره در فایل محلی (برای development)
        key_file = self.data_dir / ".wallet_key"

        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()

        # تولید کلید امن جدید
        new_key = secrets.token_urlsafe(32).encode("utf-8")

        # ذخیره کلید (فقط برای development - در production باید از .env استفاده شود)
        with open(key_file, "wb") as f:
            f.write(new_key)

        # تنظیم دسترسی فقط برای owner
        os.chmod(key_file, 0o600)

        print(
            f"⚠️  کلید رمزنگاری جدید تولید شد. برای production از متغیر محیطی {self.DEFAULT_ENCRYPTION_KEY_ENV} استفاده کنید"
        )

        return new_key

    def _initialize_wallet(self):
        """راه‌اندازی و بارگذاری کیف پول"""
        if self.wallet_file.exists():
            self._load_existing_wallet()
        else:
            self._create_new_wallet()

        # استخراج کلید عمومی
        self.public_key = self.private_key.public_key()

        # تولید شناسه نود
        self.node_id = self._generate_node_id()

    def _load_existing_wallet(self):
        """بارگذاری کیف پول موجود"""
        try:
            with open(self.wallet_file, "rb") as f:
                # تلاش برای بارگذاری با رمزگذاری
                self.private_key = serialization.load_pem_private_key(
                    f.read(), password=self.encryption_key
                )
            print(f"🔓 Wallet loaded from {self.wallet_file} (Encrypted)")

        except (ValueError, TypeError) as e:
            # تلاش برای بارگذاری بدون رمزگذاری (برای سازگاری با نسخه‌های قدیمی)
            try:
                with open(self.wallet_file, "rb") as f:
                    self.private_key = serialization.load_pem_private_key(f.read(), password=None)
                print(f"🔓 Wallet loaded from {self.wallet_file} (Unencrypted - Legacy)")

                # ارتقا به نسخه رمزگذاری شده
                self._upgrade_wallet_encryption()

            except Exception as load_error:
                raise RuntimeError(f"Failed to load wallet: {load_error}")

    def _create_new_wallet(self):
        """ایجاد کیف پول جدید"""
        # تولید کلید خصوصی با الگوریتم SECP256R1
        self.private_key = ec.generate_private_key(ec.SECP256R1())

        # ذخیره کلید با رمزگذاری
        with open(self.wallet_file, "wb") as f:
            f.write(
                self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(self.encryption_key),
                )
            )

        # تنظیم دسترسی فقط برای owner
        os.chmod(self.wallet_file, 0o600)

        print(f"🔐 New encrypted wallet created at {self.wallet_file}")

    def _upgrade_wallet_encryption(self):
        """ارتقا کیف پول قدیمی به نسخه رمزگذاری شده"""
        print("🔄 Upgrading wallet to encrypted version...")

        # ایجاد backup
        backup_file = self.wallet_file.with_suffix(".pem.backup")
        import shutil

        shutil.copy2(self.wallet_file, backup_file)

        # ذخیره مجدد با رمزگذاری
        with open(self.wallet_file, "wb") as f:
            f.write(
                self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(self.encryption_key),
                )
            )

        print(f"✅ Wallet upgraded. Backup saved at {backup_file}")

    def _generate_node_id(self) -> str:
        """
        تولید شناسه یکتای نود از کلید عمومی

        Returns:
            شناسه نود (hex string)
        """
        pub_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.X962, format=serialization.PublicFormat.CompressedPoint
        )
        return hashlib.sha256(pub_key_bytes).hexdigest()

    def sign(self, data: bytes) -> str:
        """
        امضای دیجیتال داده

        Args:
            data: داده برای امضا

        Returns:
            امضای hex
        """
        if not self.private_key:
            raise RuntimeError("Wallet not initialized")

        signature = self.private_key.sign(data, ec.ECDSA(hashes.SHA256()))
        return signature.hex()

    @staticmethod
    def verify(public_key: ec.EllipticCurvePublicKey, signature_hex: str, data: bytes) -> bool:
        """
        اعتبارسنجی امضای دیجیتال

        Args:
            public_key: کلید عمومی امضاکننده
            signature_hex: امضای hex
            data: داده اصلی

        Returns:
            True اگر امضا معتبر باشد
        """
        try:
            public_key.verify(bytes.fromhex(signature_hex), data, ec.ECDSA(hashes.SHA256()))
            return True
        except (InvalidSignature, ValueError):
            return False

    def get_public_key_pem(self) -> str:
        """
        دریافت کلید عمومی به فرمت PEM

        Returns:
            کلید عمومی PEM
        """
        if not self.public_key:
            raise RuntimeError("Wallet not initialized")

        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def get_address(self) -> str:
        """
        دریافت آدرس کیف پول (همان node_id)

        Returns:
            آدرس کیف پول
        """
        return self.node_id

    def export_public_key(self, output_file: Optional[Path] = None) -> str:
        """
        صادرات کلید عمومی به فایل

        Args:
            output_file: مسیر فایل خروجی (اختیاری)

        Returns:
            کلید عمومی PEM
        """
        pem = self.get_public_key_pem()

        if output_file:
            with open(output_file, "w") as f:
                f.write(pem)
            print(f"✅ Public key exported to {output_file}")

        return pem

    def get_stats(self) -> dict:
        """
        دریافت آمار کیف پول

        Returns:
            دیکشنری حاوی آمار
        """
        return {
            "node_id": self.node_id,
            "address": self.get_address(),
            "wallet_file": str(self.wallet_file),
            "encrypted": True,
            "algorithm": "SECP256R1",
            "hash_algorithm": "SHA256",
        }
