from cryptography.fernet import Fernet
import os.path

# Function to generate and save the key to a file
def save_key_to_file(file_path="secret.key"):
    key = Fernet.generate_key()  # Generate a new key
    with open(file_path, "wb") as key_file:
        key_file.write(key)
    print(f"Key saved to {file_path}")

def load_key_from_file(file_path="secret.key"):
    if os.path.exists(file_path):
        with open(file_path, "rb") as key_file:
            key = key_file.read()
        print(f"Key loaded from {file_path}")
        return key
    else:
        print(f"Key file not found at {file_path}. Generating a new key...")
        save_key_to_file(file_path)
        return load_key_from_file(file_path)

#save_key_to_file()