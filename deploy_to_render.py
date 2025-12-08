# deploy_to_render.py
import os
import subprocess
import time

def check_git_status():
    """Verificar estado de Git"""
    print("🔍 Checking Git status...")
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if "nothing to commit" in result.stdout:
            print("✅ Git: No changes to commit")
            return True
        else:
            print("⚠️ Git: There are uncommitted changes")
            print(result.stdout[:500])
            return False
    except Exception as e:
        print(f"❌ Git check failed: {e}")
        return False

def push_to_github():
    """Hacer push a GitHub"""
    print("🚀 Pushing to GitHub...")
    try:
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit
        commit_message = f"Deploy to Render - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Successfully pushed to GitHub")
        return True
    except Exception as e:
        print(f"❌ Git push failed: {e}")
        return False

def verify_files():
    """Verificar archivos necesarios para Render"""
    print("📁 Verifying required files...")
    
    required_files = [
        "Dockerfile.production",
        "requirements.txt", 
        "main.py",
        "run_production.py",
        "config/__init__.py",
        "models/__init__.py",
        "controllers/__init__.py"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (MISSING)")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("🚀 DEPLOY TO RENDER")
    print("=" * 60)
    
    # 1. Verificar archivos
    if not verify_files():
        print("❌ Missing required files. Aborting.")
        return
    
    # 2. Verificar Git
    if not check_git_status():
        response = input("⚠️ There are uncommitted changes. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # 3. Hacer push
    if push_to_github():
        print("\n" + "=" * 60)
        print("✅ Code pushed to GitHub successfully!")
        print("\n📋 Next steps:")
        print("1. Go to https://dashboard.render.com")
        print("2. Select your 'ecommerce-backend' service")
        print("3. Click 'Manual Deploy' → 'Deploy latest commit'")
        print("4. Wait 5-10 minutes for deployment")
        print("5. Check logs for any errors")
        print("=" * 60)
    else:
        print("❌ Failed to push to GitHub")

if __name__ == "__main__":
    main()