#!/usr/bin/env python3

"""
List all available BAML models/clients for use with melody_generator.py

This script parses the clients.baml file to extract all defined LLM clients
and displays them in a formatted way, so users can choose which model to use
for melody generation.

Usage:
    python list_models.py

This information can then be used with the melody_generator.py script:
    python main.py --model OpenAIGPT4o --theme "Create a jazzy waltz"
"""

import os
import re
import sys
from typing import List, Tuple

def extract_clients_from_baml(file_path: str) -> List[Tuple[str, str, str]]:
    """
    Extract client names, providers, and models from a BAML clients file.
    
    Returns:
        List of tuples containing (client_name, provider, model)
    """
    if not os.path.exists(file_path):
        print(f"Error: BAML clients file not found at {file_path}")
        return []
    
    clients = []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Use a simpler approach: find each client<llm> block
        for client_match in re.finditer(r'client<llm>\s+(\w+)', content):
            client_name = client_match.group(1)
            
            # Find the model used by this client
            model_pattern = fr'{client_name}\s*\{{.*?model\s+"([^"]+)"'
            model_match = re.search(model_pattern, content, re.DOTALL)
            model = model_match.group(1) if model_match else "unknown"
            
            # Find the provider used by this client
            provider_pattern = fr'{client_name}\s*\{{.*?provider\s+(\w+(?:-\w+)?)'
            provider_match = re.search(provider_pattern, content, re.DOTALL)
            provider = provider_match.group(1) if provider_match else "unknown"
            
            clients.append((client_name, provider, model))
            
    except Exception as e:
        print(f"Error parsing BAML file: {e}")
        import traceback
        traceback.print_exc()
        return []
        
    return clients

def main():
    baml_file = os.path.join("baml_src", "clients.baml")
    clients = extract_clients_from_baml(baml_file)
    
    if not clients:
        print("No clients found or error parsing the BAML file.")
        sys.exit(1)
    
    print("\n===== Available Models for Melody Generation =====\n")
    print(f"{'Client Name':<25} {'Provider':<20} {'Model':<30}")
    print("-" * 75)
    
    for client_name, provider, model in sorted(clients, key=lambda x: x[0]):
        print(f"{client_name:<25} {provider:<20} {model:<30}")
    
    print("\nUsage with melody_generator:")
    print("  python main.py --model <ClientName> --theme \"Your theme here\"")
    print("  Example: python main.py --model AnthropicSonnet37 --theme \"Create a jazzy waltz\"")
    print("\nOr directly with melody_generator.py:")
    print("  python melody_generator.py --model <ClientName> --theme \"Your theme here\"")

if __name__ == "__main__":
    main() 