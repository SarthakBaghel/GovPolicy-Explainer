#!/usr/bin/env python3
"""Test script for PDF upload functionality"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_upload():
    """Test the upload endpoint"""
    
    print("🧪 Testing GovPolicy Explainer Upload API\n")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("\n1️⃣  Registering test user...")
    test_email = "testuser@example.com"
    test_password = "TestPassword123!"
    
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": test_email, "password": test_password}
    )
    
    if register_response.status_code == 400 and "already registered" in register_response.text:
        print("✓ User already exists (that's fine)")
    elif register_response.status_code == 200:
        print(f"✓ Registration successful: {register_response.json()}")
    else:
        print(f"✗ Registration failed: {register_response.status_code}")
        print(f"  Response: {register_response.text}")
        return False
    
    # Step 2: Login to get access token
    print("\n2️⃣  Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": test_email, "password": test_password}
    )
    
    if login_response.status_code != 200:
        print(f"✗ Login failed: {login_response.status_code}")
        print(f"  Response: {login_response.text}")
        return False
    
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    print(f"✓ Login successful")
    print(f"  Token: {access_token[:20]}...")
    
    # Step 3: Create a test PDF or use existing one
    print("\n3️⃣  Checking for test PDF...")
    test_pdf_path = Path("backend/data/raw_pdfs/test_document.pdf")
    
    # Check if we have any existing PDFs to use for testing
    pdfs = list(Path("backend/data/raw_pdfs").glob("*.pdf"))
    if pdfs:
        test_pdf_path = pdfs[0]
        print(f"✓ Using existing PDF: {test_pdf_path.name}")
    else:
        print(f"⚠️  No PDF files found in backend/data/raw_pdfs/")
        print("   Creating a minimal test PDF...")
        
        # Create a minimal PDF for testing
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            test_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            c = canvas.Canvas(str(test_pdf_path), pagesize=letter)
            c.drawString(100, 750, "Test Document")
            c.drawString(100, 730, "This is a test PDF for upload functionality.")
            c.save()
            print(f"✓ Created test PDF: {test_pdf_path}")
        except ImportError:
            print("✗ reportlab not installed. Cannot create test PDF.")
            print("   Please create a test PDF manually in backend/data/raw_pdfs/")
            return False
    
    # Step 4: Upload the PDF
    print("\n4️⃣  Uploading PDF...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    with open(test_pdf_path, "rb") as f:
        files = {"file": (test_pdf_path.name, f, "application/pdf")}
        upload_response = requests.post(
            f"{BASE_URL}/api/rag/upload",
            files=files,
            headers=headers
        )
    
    if upload_response.status_code != 200:
        print(f"✗ Upload failed: {upload_response.status_code}")
        print(f"  Response: {upload_response.text}")
        return False
    
    upload_data = upload_response.json()
    print(f"✓ Upload successful!")
    print(f"  Message: {upload_data.get('message')}")
    print(f"  Doc Name: {upload_data.get('doc_name')}")
    print(f"  Output Dir: {upload_data.get('outputs')}")
    print(f"  Chunks File: {upload_data.get('chunks_file')}")
    print(f"  Index Dir: {upload_data.get('index_dir')}")
    
    # Step 5: Verify output files exist
    print("\n5️⃣  Verifying output files...")
    output_dir = Path(upload_data.get('outputs', ''))
    chunks_file = Path(upload_data.get('chunks_file', ''))
    index_dir = Path(upload_data.get('index_dir', ''))
    
    checks = [
        (output_dir.exists(), f"Output directory: {output_dir}"),
        (chunks_file.exists(), f"Chunks file: {chunks_file}"),
        ((index_dir / "index.faiss").exists(), f"FAISS index: {index_dir / 'index.faiss'}"),
        ((index_dir / "meta.jsonl").exists(), f"Index metadata: {index_dir / 'meta.jsonl'}"),
    ]
    
    all_ok = True
    for exists, description in checks:
        status = "✓" if exists else "✗"
        print(f"  {status} {description}")
        if not exists:
            all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("\n✅ All tests passed! Upload functionality is working correctly.")
        return True
    else:
        print("\n⚠️  Some files are missing. Check the service implementations.")
        return False

if __name__ == "__main__":
    try:
        success = test_upload()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the backend server")
        print(f"   Make sure the server is running at {BASE_URL}")
        print("   Run: uvicorn backend.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
