# setup_store.py
import os
import glob
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

def main():
    load_dotenv()
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )
        
    openai_client = OpenAI(
        base_url=azure_openai_endpoint,
        api_key=token_provider
    )

    print("Creating persistent vector store and uploading files...")
    vector_store = openai_client.vector_stores.create(name="travel-brochures")
    
    file_streams = [open(f, "rb") for f in glob.glob("brochures/*.pdf")]
    if not file_streams:
        print("No PDF files found in the brochures folder!")
        return
        
    file_batch = openai_client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams
    )
    
    for f in file_streams:
        f.close()
        
    print("\n--- SETUP COMPLETE ---")
    print(f"Vector store created with {file_batch.file_counts.completed} files.")
    print(f"YOUR_VECTOR_STORE_ID = {vector_store.id}")
    print("Copy this ID and put it in your .env file as VECTOR_STORE_ID")

if __name__ == '__main__': 
    main()