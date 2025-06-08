import os
import subprocess


def run_command(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ 指令失敗：{cmd}")
        exit(1)


# 設定 remote URL 使用 Secret Token
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    print("❌ 請先在 Secrets 設定 GITHUB_TOKEN")
    exit(1)

repo_url = f"https://{github_token}@github.com/ykxzz83/line-ptt-bot.git"

print("🔧 設定 Git 遠端 URL...")
run_command(f"git remote set-url origin {repo_url}")

print("📦 新增所有變更檔案...")
run_command("git add .")

print("📝 建立 commit...")
run_command("git commit -m '📦 更新程式碼（自動推送）' || echo '⚠️ 無變更可提交'")

print("🚀 推送到 GitHub...")
run_command("git push origin main")

print("✅ 推送完成！")
