"""
Test client for the search management endpoints.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

# Add parent directory to path to import from sibling modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

async def test_search_management_api():
    """Test the search management API endpoints."""
    # Load environment variables
    load_dotenv()
    
    base_url = "http://localhost:8765"
    
    async with aiohttp.ClientSession() as session:
        # Test creating a document
        print("\n=== Creating a document ===")
        create_response = await session.post(
            f"{base_url}/api/documents",
            json={
                "fact": "Azure AI Search supports vector search for semantic retrieval.",
                "title": "Vector Search Capability"
            }
        )
        create_data = await create_response.json()
        print(f"Status: {create_response.status}")
        print(json.dumps(create_data, indent=2))
        
        if create_response.status != 201:
            print("Failed to create document. Exiting.")
            return
        
        document_id = create_data.get("id")
        
        # Test getting all documents
        print("\n=== Getting all documents ===")
        get_all_response = await session.get(f"{base_url}/api/documents")
        get_all_data = await get_all_response.json()
        print(f"Status: {get_all_response.status}")
        print(f"Found {len(get_all_data.get('documents', []))} documents")
        
        # Test getting a specific document
        if document_id:
            print(f"\n=== Getting document {document_id} ===")
            get_one_response = await session.get(f"{base_url}/api/documents/{document_id}")
            get_one_data = await get_one_response.json()
            print(f"Status: {get_one_response.status}")
            print(json.dumps(get_one_data, indent=2))
            
            # Test deleting a document
            print(f"\n=== Deleting document {document_id} ===")
            delete_response = await session.delete(f"{base_url}/api/documents/{document_id}")
            delete_data = await delete_response.json()
            print(f"Status: {delete_response.status}")
            print(json.dumps(delete_data, indent=2))

if __name__ == "__main__":
    asyncio.run(test_search_management_api()) 