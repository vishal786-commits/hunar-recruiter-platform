import os
from openai import OpenAI

# 1. Initialize the client (it automatically looks for the OPENAI_API_KEY environment variable)
client = OpenAI()

try:
    # 2. Fetch the list of models
    models = client.models.list()
    
    # 3. Print the model IDs
    print("Available Models:")
    for model in models.data:
        print(f"- {model.id}")
        
except Exception as e:
    print(f"An error occurred: {e}")
