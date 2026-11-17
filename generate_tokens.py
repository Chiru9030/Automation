"""
Auth Token Generator for Headless Cloud Automation.
Run this script ONCE locally on your workstation to produce:
1. youtube_tokens.json
2. instagram_session.json
"""

import os
import sys

def generate_youtube_tokens():
    print("\n--- 1. Generating YouTube OAuth Tokens ---")
    client_secrets_file = "client_secrets.json"
    if not os.path.exists(client_secrets_file):
        print(f"Error: '{client_secrets_file}' not found.")
        print("Please download your OAuth 2.0 Client credentials JSON from Google Cloud Console,")
        print(f"rename it to '{client_secrets_file}', and place it in this directory.")
        return False

    try:
        import json
        from google_auth_oauthlib.flow import InstalledAppFlow

        with open(client_secrets_file) as f:
            secret_data = json.load(f)

        client_type = list(secret_data.keys())[0]
        port = 8080 if client_type == "web" else 0

        if client_type == "web":
            print("⚠️ Notice: Your client_secrets.json is configured as 'Web application'.")
            print(f"👉 Please make sure 'http://localhost:{port}/' is added in Google Cloud Console under:")
            print("   'Authorized redirect URIs' for this OAuth Client ID.\n")

        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_local_server(port=port)

        with open("youtube_tokens.json", "w") as token_file:
            token_file.write(credentials.to_json())

        print("✅ Successfully created 'youtube_tokens.json'!")
        return True
    except Exception as e:
        print(f"Failed to generate YouTube tokens: {e}")
        return False


def generate_instagram_session():
    print("\n--- 2. Generating Instagram Session ---")
    username = os.getenv("IG_USERNAME") or input("Enter Instagram Username: ").strip()
    password = os.getenv("IG_PASSWORD") or input("Enter Instagram Password: ").strip()

    if not username or not password:
        print("Username and password are required.")
        return False

    try:
        from instagrapi import Client

        cl = Client()
        cl.login(username, password)
        cl.dump_settings("instagram_session.json")
        print(" Successfully created 'instagram_session.json'!")
        return True
    except Exception as e:
        print(f"Failed to generate Instagram session: {e}")
        return False


if __name__ == "__main__":
    print("==================================================")
    print(" Local Auth Token Generator for Video Automation ")
    print("==================================================")

    choice = input("Generate (1) YouTube tokens, (2) Instagram session, (3) Both? [1/2/3]: ").strip()

    if choice in ["1", "3"]:
        generate_youtube_tokens()

    if choice in ["2", "3"]:
        generate_instagram_session()

    print("\nDone! Upload the generated JSON file(s) securely to your cloud environment.")

