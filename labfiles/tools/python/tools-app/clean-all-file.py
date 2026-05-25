# wipe_all.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

def main():
    load_dotenv()
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    vector_store_id = os.getenv("VECTOR_STORE_ID")

    if not vector_store_id:
        print("Error: No VECTOR_STORE_ID found in your .env file.")
        return

    # Initialize client
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )
    openai_client = OpenAI(
        base_url=azure_openai_endpoint,
        api_key=token_provider
    )

    # Double-check confirmation
    print(f"WARNING: This will permanently delete vector store '{vector_store_id}' AND all files indexed inside it.")
    confirm = input("Are you absolutely sure you want to proceed? (type 'DELETE' to confirm): ")
    if confirm != 'DELETE':
        print("Wipe cancelled.")
        return

    try:
        # 1. Fetch and delete all individual files tied to this vector store
        print("\nStep 1: Fetching files inside the vector store...")
        store_files = openai_client.vector_stores.files.list(vector_store_id=vector_store_id)
        
        file_ids = [f.id for f in store_files.data]
        
        if file_ids:
            print(f"Found {len(file_ids)} file(s). Starting deletion...")
            for file_id in file_ids:
                try:
                    openai_client.files.delete(file_id=file_id)
                    print(f" -> Deleted file: {file_id}")
                except Exception as file_ex:
                    print(f" -> Failed to delete file {file_id}: {file_ex} (It may have already been deleted)")
        else:
            print("No files found remaining in this vector store.")

        # 2. Delete the vector store container itself
        print("\nStep 2: Deleting the vector store container...")
        deleted_store = openai_client.vector_stores.delete(vector_store_id=vector_store_id)
        
        if deleted_store.deleted:
            print("\n--- SYSTEM WIPED CLEAN ---")
            print(f"Successfully removed vector store: {deleted_store.id}")
            print("Your Azure OpenAI storage quota for these files has been freed.")
            print("Remember to clear out the VECTOR_STORE_ID from your .env file!")
        else:
            print(f"Could not delete the vector store container. Response: {deleted_store}")

    except Exception as ex:
        print(f"\nAn error occurred during the wipe process: {ex}")

if __name__ == '__main__':
    main()