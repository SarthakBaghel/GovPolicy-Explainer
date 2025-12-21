#!/usr/bin/env python3
"""
Test script for document management flow
Tests: Auth -> Upload -> List Documents -> Delete Documents
"""

import requests
import json
from pathlib import Path
import tempfile

BASE_URL = "http://localhost:8000/api"

class TestDocumentFlow:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.test_email = "doctest@example.com"
        self.test_password = "TestPassword123"
        self.uploaded_doc_ids = []
    
    def test_registration(self):
        """Register a test user"""
        print("\n" + "="*60)
        print("STEP 1: Register User")
        print("="*60)
        
        payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_login(self):
        """Login and get JWT token"""
        print("\n" + "="*60)
        print("STEP 2: Login & Get JWT Token")
        print("="*60)
        
        payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                self.token = data.get("access_token")
                print(f"\n✓ Got JWT Token: {self.token[:50]}...")
                return True
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_upload_document(self, filename="policy_on_adoption_of_oss.pdf"):
        """Upload a test PDF document"""
        print("\n" + "="*60)
        print("STEP 3: Upload Document")
        print("="*60)
        
        # Use existing PDF file
        pdf_path = Path("/Users/sarthakbaghel/Documents/Projects/govpolicy-explainer/backend/data/raw_pdfs/policy_on_adoption_of_oss.pdf")
        
        if not pdf_path.exists():
            print(f"Error: PDF file not found at {pdf_path}")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            with open(pdf_path, 'rb') as f:
                files = {"file": (filename, f, "application/pdf")}
                response = requests.post(
                    f"{BASE_URL}/rag/upload",
                    files=files,
                    headers=headers
                )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                doc_id = data.get("doc_id")
                self.uploaded_doc_ids.append(doc_id)
                print(f"\n✓ Document uploaded with ID: {doc_id}")
                return True
            else:
                try:
                    error_data = response.json()
                    print(f"Error Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error Response (raw): {response.text}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_list_documents(self):
        """List all documents for the user"""
        print("\n" + "="*60)
        print("STEP 4: List User Documents")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(
                f"{BASE_URL}/documents/documents",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                doc_count = data.get("count", 0)
                print(f"\n✓ Found {doc_count} document(s) for user")
                return True
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_get_document_info(self):
        """Get info about a specific document"""
        if not self.uploaded_doc_ids:
            print("\nNo documents to retrieve info for")
            return False
        
        print("\n" + "="*60)
        print("STEP 5: Get Document Info")
        print("="*60)
        
        doc_id = self.uploaded_doc_ids[0]
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(
                f"{BASE_URL}/documents/documents/{doc_id}",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                print(f"\n✓ Retrieved info for document: {doc_id}")
                return True
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_delete_document(self):
        """Delete a document"""
        if not self.uploaded_doc_ids:
            print("\nNo documents to delete")
            return False
        
        print("\n" + "="*60)
        print("STEP 6: Delete Document")
        print("="*60)
        
        doc_id = self.uploaded_doc_ids[0]
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.delete(
                f"{BASE_URL}/documents/documents/{doc_id}",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                print(f"\n✓ Deleted document: {doc_id}")
                return True
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run the complete flow"""
        print("\n" + "🧪 Document Management Flow Test Suite 🧪".center(60))
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000")
            print(f"\n✓ Server is running at http://localhost:8000")
        except:
            print("\n✗ Server is NOT running!")
            return False
        
        results = {}
        
        # Run tests
        results["Registration"] = self.test_registration()
        if not results["Registration"]:
            # Try login if registration fails (user may already exist)
            print("\nAttempting login with existing user...")
            results["Login"] = self.test_login()
        else:
            results["Login"] = self.test_login()
        
        if not results["Login"]:
            print("\nCannot proceed without login")
            return False
        
        results["Upload Document"] = self.test_upload_document()
        results["List Documents"] = self.test_list_documents()
        results["Get Document Info"] = self.test_get_document_info()
        results["Delete Document"] = self.test_delete_document()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:8} - {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return False

if __name__ == "__main__":
    test = TestDocumentFlow()
    test.run_all_tests()
