#!/usr/bin/env python3
"""
MongoDB Inspection Script
Checks the state of users and documents collections
"""

import sys
sys.path.insert(0, '/Users/sarthakbaghel/Documents/Projects/govpolicy-explainer')

from backend.core.mongo_config import get_db
import json

def inspect_mongodb():
    """Inspect MongoDB collections"""
    print("\n" + "="*70)
    print("📊 MONGODB INSPECTION")
    print("="*70)
    
    try:
        db = get_db()
        print("\n✓ Connected to MongoDB")
        
        # Check users collection
        print("\n" + "-"*70)
        print("USERS Collection")
        print("-"*70)
        users_collection = db["users"]
        users = list(users_collection.find().limit(10))
        
        if users:
            print(f"Total users: {users_collection.count_documents({})}")
            for i, user in enumerate(users, 1):
                print(f"\n{i}. User:")
                print(f"   _id: {user.get('_id')}")
                print(f"   id (user_id): {user.get('id')}")
                print(f"   email: {user.get('email')}")
                print(f"   documents array: {user.get('documents', [])}")
                print(f"   documents count: {len(user.get('documents', []))}")
        else:
            print("⚠️  No users found in collection")
        
        # Check documents collection
        print("\n" + "-"*70)
        print("DOCUMENTS Collection")
        print("-"*70)
        documents_collection = db["documents"]
        documents = list(documents_collection.find().limit(10))
        
        if documents:
            print(f"Total documents: {documents_collection.count_documents({})}")
            for i, doc in enumerate(documents, 1):
                print(f"\n{i}. Document:")
                print(f"   _id: {doc.get('_id')}")
                print(f"   doc_id: {doc.get('doc_id')}")
                print(f"   user_id: {doc.get('user_id')}")
                print(f"   filename: {doc.get('filename')}")
                print(f"   file_size: {doc.get('file_size')}")
                print(f"   status: {doc.get('status')}")
                print(f"   created_at: {doc.get('created_at')}")
        else:
            print("⚠️  No documents found in collection")
        
        # Cross-check: verify user_id in documents matches users in collection
        print("\n" + "-"*70)
        print("CROSS-CHECK: Document-User Consistency")
        print("-"*70)
        
        if documents and users:
            user_ids_in_users_collection = {u['id'] for u in users}
            user_ids_in_documents = {d['user_id'] for d in documents}
            
            print(f"User IDs in users collection: {user_ids_in_users_collection}")
            print(f"User IDs in documents: {user_ids_in_documents}")
            
            orphaned_docs = user_ids_in_documents - user_ids_in_users_collection
            if orphaned_docs:
                print(f"\n⚠️  Orphaned documents (user not in users collection): {orphaned_docs}")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_mongodb()
