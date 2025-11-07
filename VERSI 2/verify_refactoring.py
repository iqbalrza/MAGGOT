"""
Quick Verification Script
Verify all changes after refactoring to Tesseract OCR
"""

import os
import sys

def check_mark(condition):
    return "✅" if condition else "❌"

def verify_files():
    """Verify all required files exist"""
    print("\n" + "="*80)
    print("📁 VERIFYING FILES")
    print("="*80)
    
    files_to_check = [
        ("chatbot/utils/pdf_processor.py", "PDF Processor (modified)"),
        ("chatbot/chatbot_api.py", "Chatbot API (modified)"),
        ("chatbot/requirements_chatbot.txt", "Requirements (modified)"),
        ("chatbot/.env", "Environment config"),
        ("chatbot/.env.example", "Environment example (modified)"),
        ("chatbot/test_ocr.py", "OCR test script (new)"),
        ("chatbot/OCR_SETUP_GUIDE.md", "OCR setup guide (new)"),
        ("chatbot/README_OCR.md", "OCR README (new)"),
        ("chatbot/MIGRATION_GUIDE.md", "Migration guide (new)"),
        ("REFACTORING_SUMMARY.md", "Refactoring summary (new)"),
    ]
    
    all_exist = True
    for filepath, description in files_to_check:
        exists = os.path.exists(filepath)
        all_exist = all_exist and exists
        print(f"{check_mark(exists)} {description}")
        if exists:
            print(f"   → {filepath}")
    
    return all_exist

def verify_imports():
    """Verify Python imports work"""
    print("\n" + "="*80)
    print("🐍 VERIFYING IMPORTS")
    print("="*80)
    
    imports = {
        "pytesseract": "Tesseract OCR",
        "cv2": "OpenCV",
        "PIL": "Pillow",
        "pypdf": "PyPDF",
        "pdf2image": "PDF2Image",
    }
    
    all_ok = True
    for module, name in imports.items():
        try:
            __import__(module)
            print(f"✅ {name} ({module})")
        except ImportError:
            print(f"❌ {name} ({module}) - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_old_dependencies():
    """Check if old heavy dependencies are still installed"""
    print("\n" + "="*80)
    print("🗑️  CHECKING OLD DEPENDENCIES (should be removed)")
    print("="*80)
    
    old_deps = {
        "transformers": "Hugging Face Transformers",
        "torch": "PyTorch",
        "torchvision": "TorchVision",
    }
    
    clean = True
    for module, name in old_deps.items():
        try:
            __import__(module)
            print(f"⚠️  {name} - STILL INSTALLED (optional, can be removed)")
            clean = False
        except ImportError:
            print(f"✅ {name} - Not installed (good!)")
    
    return clean

def verify_env_config():
    """Verify .env has OCR configuration"""
    print("\n" + "="*80)
    print("⚙️  VERIFYING ENVIRONMENT CONFIG")
    print("="*80)
    
    env_path = "chatbot/.env"
    if not os.path.exists(env_path):
        print(f"❌ .env file not found at {env_path}")
        return False
    
    required_vars = [
        "TESSERACT_CMD",
        "OCR_LANG",
        "SKIP_OCR",
    ]
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    all_present = True
    for var in required_vars:
        present = var in content
        all_present = all_present and present
        print(f"{check_mark(present)} {var}")
    
    # Check old vars are removed/commented
    old_vars = ["CAPTION_MODEL", "SKIP_IMAGE_CAPTIONING"]
    for var in old_vars:
        present = var in content and not content[content.find(var):content.find(var)+50].startswith("#")
        if present:
            print(f"⚠️  {var} - Old variable still active (should remove/comment)")
        else:
            print(f"✅ {var} - Removed/commented (good!)")
    
    return all_present

def verify_code_changes():
    """Verify code has OCR instead of BLIP"""
    print("\n" + "="*80)
    print("💻 VERIFYING CODE CHANGES")
    print("="*80)
    
    # Check pdf_processor.py
    with open("chatbot/utils/pdf_processor.py", 'r') as f:
        pdf_processor = f.read()
    
    has_tesseract = "pytesseract" in pdf_processor
    has_ocr = "ocr_image" in pdf_processor or "OCR" in pdf_processor
    no_blip = "BlipProcessor" not in pdf_processor
    no_torch = "import torch" not in pdf_processor
    
    print(f"{check_mark(has_tesseract)} pdf_processor.py uses pytesseract")
    print(f"{check_mark(has_ocr)} pdf_processor.py has OCR methods")
    print(f"{check_mark(no_blip)} pdf_processor.py removed BLIP imports")
    print(f"{check_mark(no_torch)} pdf_processor.py removed torch imports")
    
    # Check chatbot_api.py
    with open("chatbot/chatbot_api.py", 'r') as f:
        api_code = f.read()
    
    uses_skip_ocr = "SKIP_OCR" in api_code or "skip_ocr" in api_code
    no_skip_images = "SKIP_IMAGE_CAPTIONING" not in api_code
    
    print(f"{check_mark(uses_skip_ocr)} chatbot_api.py uses SKIP_OCR")
    print(f"{check_mark(no_skip_images)} chatbot_api.py removed SKIP_IMAGE_CAPTIONING")
    
    return has_tesseract and has_ocr and no_blip and uses_skip_ocr

def verify_requirements():
    """Verify requirements.txt has correct dependencies"""
    print("\n" + "="*80)
    print("📦 VERIFYING REQUIREMENTS")
    print("="*80)
    
    with open("chatbot/requirements_chatbot.txt", 'r') as f:
        requirements = f.read()
    
    # Should have
    has_pytesseract = "pytesseract" in requirements
    has_opencv = "opencv-python" in requirements
    
    # Should NOT have
    no_transformers = "transformers" not in requirements
    no_torch = "torch" not in requirements
    no_torchvision = "torchvision" not in requirements
    
    print(f"{check_mark(has_pytesseract)} pytesseract in requirements")
    print(f"{check_mark(has_opencv)} opencv-python in requirements")
    print(f"{check_mark(no_transformers)} transformers removed from requirements")
    print(f"{check_mark(no_torch)} torch removed from requirements")
    print(f"{check_mark(no_torchvision)} torchvision removed from requirements")
    
    return has_pytesseract and has_opencv and no_transformers

def main():
    """Run all verification checks"""
    print("\n" + "="*80)
    print("🔍 REFACTORING VERIFICATION SCRIPT")
    print("="*80)
    print("Verifying migration from BLIP to Tesseract OCR...")
    
    checks = {
        "Files": verify_files(),
        "Imports": verify_imports(),
        "Old Dependencies": check_old_dependencies(),
        "Environment Config": verify_env_config(),
        "Code Changes": verify_code_changes(),
        "Requirements": verify_requirements(),
    }
    
    # Summary
    print("\n" + "="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)
    
    for check_name, result in checks.items():
        print(f"{check_mark(result)} {check_name}")
    
    all_passed = all(checks.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("="*80)
        print("\n✨ Refactoring complete and verified!")
        print("\n📋 Next steps:")
        print("   1. Install Tesseract OCR (see OCR_SETUP_GUIDE.md)")
        print("   2. Configure .env with Tesseract path")
        print("   3. Run: python chatbot/test_ocr.py")
        print("   4. Run: python chatbot/chatbot_api.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("="*80)
        print("\n❌ Please review the failed checks above")
        print("\n📚 Documentation:")
        print("   - chatbot/OCR_SETUP_GUIDE.md")
        print("   - chatbot/MIGRATION_GUIDE.md")
        print("   - chatbot/README_OCR.md")
    
    print("\n")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
