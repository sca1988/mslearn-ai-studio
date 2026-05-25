import os
from dotenv import load_dotenv
import glob

# Import namespaces
# import namespaces
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider



def main(): 
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get configuration settings 
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")
        vector_store_id = os.getenv("VECTOR_STORE_ID")

        # Initialize the OpenAI client
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://ai.azure.com/.default"
        )
            
        openai_client = OpenAI(
            base_url=azure_openai_endpoint,
            api_key=token_provider
        )



              # Track conversation state
        last_response_id = None

        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a question (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a question.")
                continue

            # Get a response using tools
            response = openai_client.responses.create(
                model=model_deployment,
                instructions="""
                You are a travel assistant that provides information on travel services available from Margie's Travel.
                Answer questions about services offered by Margie's Travel using the provided travel brochures.
                Search the web for general information about destinations or current travel advice.
                """,
                input=input_text,
                previous_response_id=last_response_id,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [vector_store_id]
                    },
                    {
                        "type": "web_search"
                    }
                ]
            )
            print(response.output_text)
            last_response_id = response.id
            



    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()
