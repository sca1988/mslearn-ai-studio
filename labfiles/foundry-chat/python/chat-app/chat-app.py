import os
from urllib import response
from dotenv import load_dotenv

# import namespaces
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def main():
    # Clear the console
    os.system("cls" if os.name == "nt" else "clear")

    try:
        # Get configuration settings
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Initialize the OpenAI client
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://ai.azure.com/.default"
        )

        openai_client = OpenAI(base_url=azure_openai_endpoint, api_key=token_provider)

        last_response_id = None
        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Get a response
            response = openai_client.responses.create(
                model=model_deployment,
                instructions="You are a helpful AI assistant that answers questions and provides information.",
                input=input_text,
                max_output_tokens=100,
                previous_response_id = last_response_id,
            )
            last_response_id = response.id
            print(response.output_text)
            print(f"Output tokens used: {response.usage.output_tokens}")

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
