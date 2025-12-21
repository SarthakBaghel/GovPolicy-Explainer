#!/usr/bin/env python3
"""
MongoDB Migration Script
Initializes documents array for all existing users
"""

import sys
sys.path.insert(0, '/Users/sarthakbaghel/Documents/Projects/govpolicy-explainer')

from backend.core.mongo_config import get_db

def migrate_users_documents_field():
    """Add documents array to all users that don't have it"""
    print("\n" + "="*70)
    print("🔄 MONGODB MIGRATION: Initialize documents field")
    print("="*70)
    
    db = get_db()
    users_collection = db["users"]
    
    print("\nBefore migration:")
    before_count = users_collection.count_documents({"documents": {"$exists": False}})
    print(f"  Users without documents field: {before_count}")
    
    # Update all users without documents field
    result = users_collection.update_many(
        {"documents": {"$exists": False}},
        {"$set": {"documents": []}}
    )
    
    print(f"\nMigration result:")
    print(f"  ✓ Updated {result.modified_count} users")
    print(f"  ✓ Total users now: {users_collection.count_documents({})}")
    
    # Verify all users have documents field
    print(f"\nVerification:")
    users_without_docs = users_collection.count_documents({"documents": {"$exists": False}})
    users_with_docs = users_collection.count_documents({"documents": {"$exists": True}})
    
    print(f"  ✓ Users with documents field: {users_with_docs}")
    print(f"  ✓ Users without documents field: {users_without_docs}")
    
    if users_without_docs == 0:
        print(f"\n✅ Migration completed successfully!")
    else:
        print(f"\n⚠️  Warning: Some users still missing documents field")
    
    # Show all users and their documents
    print(f"\nAll users status:")
    users = list(users_collection.find().sort("_id", -1))
    for i, user in enumerate(users, 1):
        docs_count = len(user.get('documents', []))
        print(f"  {i}. {user['email']}: {docs_count} documents")

if __name__ == "__main__":
    migrate_users_documents_field()
