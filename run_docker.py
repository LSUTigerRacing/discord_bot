#!/usr/bin/env python3
# this is completely vibe coded
# run chmod +x run_docker.py to give it perms
import os
import subprocess
import sys
from dotenv import load_dotenv

def run_docker():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get tokens from environment variables
    test_token = os.getenv('TEST_TOKEN')
    prod_token = os.getenv('PRODUCTION_TOKEN')
    
    if not test_token or not prod_token:
        print("Error: TEST_TOKEN and PRODUCTION_TOKEN must be set in .env file")
        sys.exit(1)
    
    # Ask for target environment
    target = input("Push to (P)roduction or (D)ev? ").upper()
    if target not in ['P', 'D']:
        print("Invalid input! Please enter P or D")
        sys.exit(1)
    
    if target == 'P':
        confirm = input("Are you sure? This cannot be undone. (Y)es or (N)o: ").upper()
        if confirm != 'Y':
            print("Deployment cancelled")
            sys.exit(0)
    
    # Build the Docker image
    print("Building Docker image...")
    build_result = subprocess.run([
        'docker', 'build', '-t', 'discord-bot', '.'
    ], capture_output=True, text=True)
    
    if build_result.returncode != 0:
        print(f"Error building Docker image: {build_result.stderr}")
        sys.exit(1)
    
    print("Docker image built successfully!")
    
    # Run the Docker container
    print("Starting Discord bot in Docker container...")
    run_command = [
        'docker', 'run', '--rm',
        '-e', f'TARGET={target}',
        '-e', f'TEST_TOKEN={test_token}',
        '-e', f'PRODUCTION_TOKEN={prod_token}',
        '-p', '8080:8080',
        'discord-bot'
    ]
    
    # Run the container in foreground
    subprocess.run(run_command)

if __name__ == '__main__':
    run_docker()