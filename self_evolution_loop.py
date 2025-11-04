"""
Laniakea Protocol - Self-Evolution Loop
اسکریپت اصلی برای اجرای چرخه توسعه درونی دائمی و همگام‌سازی با GitHub
"""

import asyncio
import os
import subprocess
import time
from datetime import datetime
from src.intelligence.self_evolution import run_evolution

# --- تنظیمات ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
EVOLUTION_INTERVAL_SECONDS = 3600  # هر 1 ساعت یک بار
AUTO_APPLY_IMPROVEMENTS = True
GITHUB_BRANCH = "main"
GITHUB_REMOTE = "origin"
COMMIT_MESSAGE_PREFIX = "auto-evolve: "

def git_commit_and_push(commit_message: str) -> bool:
    """
    کامیت کردن تغییرات و ارسال به GitHub
    """
    try:
        print("\n--- Git Sync Started ---")
        
        # 1. افزودن تمام تغییرات
        subprocess.run(["git", "add", "."], check=True, cwd=PROJECT_ROOT)
        
        # 2. بررسی وجود تغییرات برای کامیت
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_ROOT)
        if result.returncode == 0:
            print("No changes to commit. Working tree clean.")
            return True

        # 3. کامیت کردن
        full_message = f"{COMMIT_MESSAGE_PREFIX}{commit_message}"
        subprocess.run(["git", "commit", "-m", full_message], check=True, cwd=PROJECT_ROOT)
        print(f"Changes committed: {full_message}")
        
        # 4. پول کردن قبل از پوش (برای جلوگیری از تداخل)
        subprocess.run(["git", "pull", GITHUB_REMOTE, GITHUB_BRANCH], check=True, cwd=PROJECT_ROOT)

        # 5. پوش کردن
        subprocess.run(["git", "push", GITHUB_REMOTE, GITHUB_BRANCH], check=True, cwd=PROJECT_ROOT)
        print("Changes successfully pushed to GitHub.")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        print("Attempting to reset and continue...")
        # در صورت خطا، تغییرات را reset می‌کنیم تا در چرخه بعدی دوباره امتحان شود
        subprocess.run(["git", "reset", "--hard"], cwd=PROJECT_ROOT)
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during Git sync: {e}")
        return False

async def evolution_loop():
    """
    حلقه اصلی توسعه درونی دائمی
    """
    print("=" * 60)
    print("🌌 Laniakea Self-Evolution Loop Activated")
    print(f"Interval: {EVOLUTION_INTERVAL_SECONDS / 3600} hours | Auto-Apply: {AUTO_APPLY_IMPROVEMENTS}")
    print("=" * 60)

    while True:
        start_time = time.time()
        
        try:
            # 1. اجرای چرخه تکامل
            print(f"\n--- Starting Evolution Cycle at {datetime.now().isoformat()} ---")
            report = await run_evolution(project_root=PROJECT_ROOT, auto_apply=AUTO_APPLY_IMPROVEMENTS)
            print("--- Evolution Cycle Finished ---")

            # 2. بررسی وجود بهبودهای اعمال شده
            applied_count = len(report.get('applied_improvements', []))
            
            if applied_count > 0:
                commit_msg = f"Applied {applied_count} high-priority improvements. Avg Complexity: {report['project_stats']['avg_complexity']:.2f}"
                git_commit_and_push(commit_msg)
            else:
                print("No high-priority improvements applied. Skipping Git commit.")

        except Exception as e:
            print(f"❌ Critical error in evolution loop: {e}")
            # در صورت خطای بحرانی، زمان انتظار طولانی‌تر می‌شود
            await asyncio.sleep(EVOLUTION_INTERVAL_SECONDS * 2)
            continue

        end_time = time.time()
        elapsed = end_time - start_time
        
        # 3. انتظار برای چرخه بعدی
        wait_time = EVOLUTION_INTERVAL_SECONDS - elapsed
        if wait_time > 0:
            print(f"\nCycle took {elapsed:.2f}s. Waiting for {wait_time:.2f}s until next evolution.")
            await asyncio.sleep(wait_time)
        else:
            print(f"\nCycle took {elapsed:.2f}s. Starting next cycle immediately.")

if __name__ == "__main__":
    # تنظیم نام کاربری و ایمیل گیت برای کامیت‌های خودکار
    subprocess.run(["git", "config", "--global", "user.name", "Laniakea Self-Evolution Engine"], cwd=PROJECT_ROOT)
    subprocess.run(["git", "config", "--global", "user.email", "evolution@laniakea.protocol"], cwd=PROJECT_ROOT)
    
    try:
        asyncio.run(evolution_loop())
    except KeyboardInterrupt:
        print("\nEvolution Loop stopped by user.")
