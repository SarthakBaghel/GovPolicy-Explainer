#!/usr/bin/env python3
"""
Test with MongoDB field initialization
This will update existing users to have documents array, then run upload test
"""

import sys
sys.path.insert(0, '/Users/sarthakbaghel/Documents/Projects/govpolicy-explainer')

from backend.core.mongo_config import get_db
import requests
import json
from pathlib import Path
from uuid import uuid4

BASE_URL = "http://localhost:8000/api"

def initialize_users_documents_field():
    """Add documents array to existing users that don't have it"""
    print("\n" + "="*70)
    print("🔧 INITIALIZING USERS DOCUMENTS FIELD")
    print("="*70)
    
    db = get_db()
    users_collection = db["users"]
    
    # Update all users without documents field
    result = users_collection.update_many(
        {"documents": {"$exists": False}},
        {"$set": {"documents": []}}
    )
    
    print(f"✓ Updated {result.modified_count} users to have documents array")
    
    # Verify
    users = list(users_collection.find())
    for user in users:
        print(f"\n  User: {user['email']}")
        print(f"  - documents: {user.get('documents', [])}")

def test_upload_and_verify():
    """Test document upload with new user"""
    print("\n" + "="*70)
    print("📤 TESTING DOCUMENT UPLOAD")
    print("="*70)
    
    # Create new user
    test_email = f"verify-test-{uuid4().hex[:8]}@example.com"
    test_password = "TestPass123"
    
    print(f"\n1️⃣  Registering user: {test_email}")
    reg_response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": test_email,
        "password": test_password
    })
    print(f"   Status: {reg_response.status_code}")
    
    print(f"\n2️⃣  Logging in...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    token = login_response.json()["access_token"]
    print(f"   ✓ Got token")
    
    print(f"\n3️⃣  Uploading document...")
    pdf_path = Path("/Users/sarthakbaghel/Documents/Projects/govpolicy-explainer/backend/data/raw_pdfs/policy_on_adoption_of_oss.pdf")
    
    with open(pdf_path, 'rb') as f:
        upload_response = requests.post(
            f"{BASE_URL}/rag/upload",
            files={"file": ("policy.pdf", f, "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    if upload_response.status_code == 200:
        data = upload_response.json()
        doc_id = data["doc_id"]
        user_id = data["user_id"]
        print(f"   ✓ Upload successful")
        print(f"   - doc_id: {doc_id}")
        print(f"   - user_id: {user_id}")
        
        print(f"\n4️⃣  Checking MongoDB directly...")
        db = get_db()
        
        # Check user
        user = db.users.find_one({"id": user_id})
        if user:
            print(f"\n   ✓ User found in MongoDB:")
            print(f"     - email: {user['email']}")
            print(f"     - documents array: {user.get('documents', [])}")
            print(f"     - contains our doc? {doc_id in user.get('documents', [])}")
        else:
            print(f"   ✗ User NOT found")
        
        # Check document
        document = db.documents.find_one({"doc_id": doc_id})
        if document:
            print(f"\n   ✓ Document found in MongoDB:")
            print(f"     - doc_id: {document['doc_id']}")
            print(f"     - user_id: {document['user_id']}")
            print(f"     - filename: {document['filename']}")
            print(f"     - status: {document['status']}")
        else:
            print(f"   ✗ Document NOT found")
    else:
        print(f"   ✗ Upload failed: {upload_response.status_code}")
        print(f"   Response: {upload_response.json()}")

if __name__ == "__main__":
    initialize_users_documents_field()
    test_upload_and_verify()
