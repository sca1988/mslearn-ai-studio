# add_to_store.py
import os
import glob
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

    try:
        # 1. Fetch names of files already inside the vector store
        print("Fetching existing files from the vector store...")
        existing_files = openai_client.vector_stores.files.list(vector_store_id=vector_store_id)
        
        # Build a set of filenames already in the cloud for O(1) lookups
        cloud_filenames = set()
        for file_info in existing_files.data:
            # We need to retrieve the actual file object to see its original filename
            file_details = openai_client.files.retrieve(file_id=file_info.id)
            if file_details.filename:
                cloud_filenames.add(file_details.filename)

        # 2. Find local files you want to add
        # This scans the entire brochures folder, but you can target specific files too
        local_file_paths = glob.glob("brochures/*.pdf")
        
        files_to_upload = []
        file_streams = []

        print("\nChecking for duplicates...")
        for path in local_file_paths:
            filename = os.path.basename(path)
            
            if filename in cloud_filenames:
                print(f" -> Skipping '{filename}' (Already exists in vector store)")
            else:
                print(f" -> Queued '{filename}' for upload")
                files_to_upload.append(path)
                file_streams.append(open(path, "rb"))

        # 3. Upload only the unique files
        if not file_streams:
            print("\nNo new or unique files found to upload. Everything is up to date!")
            return

        print(f"\nUploading and indexing {len(file_streams)} new file(s)...")
        file_batch = openai_client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=file_streams
        )
        
        print("\n--- UPDATE SUCCESSFUL ---")
        print(f"Batch Status: {file_batch.status}")
        print(f"New files appended: {file_batch.file_counts.completed}")

    except Exception as ex:
        print(f"\nAn error occurred: {ex}")
        
    finally:
        # Always clean up open file streams
        for f in file_streams:
            f.close()

if __name__ == '__main__':
    main()