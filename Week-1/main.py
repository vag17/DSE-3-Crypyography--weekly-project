"""
WEEK-1 — Digital Signature Algorithm (Ed25519) Implementation and Verification
--------------------------------------------------------------------------------
A beginner-friendly Python project that demonstrates how Ed25519 digital
signatures work using the `cryptography` library.

This program can:
1. Generate an Ed25519 public/private key pair.
2. Sign a message using the private key.
3. Verify a signature using the public key.
4. Show whether a signature is VALID or INVALID.
5. Demonstrate what happens when a signed message is tampered with.

Author: (your name here)
"""

import os

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


# ---------------------------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------------------------
# Using constants for paths makes the code easier to read and update.

KEYS_DIR = "keys"
SIGNATURES_DIR = "signatures"
MESSAGES_DIR = "messages"

PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "public_key.pem")
SIGNATURE_PATH = os.path.join(SIGNATURES_DIR, "signature.bin")
DEFAULT_MESSAGE_PATH = os.path.join(MESSAGES_DIR, "message.txt")


# ---------------------------------------------------------------------------
# KEY GENERATION
# ---------------------------------------------------------------------------

def generate_keys():
    """
    Generates a new Ed25519 private/public key pair and saves them
    as PEM files inside the 'keys' folder.

    The private key is NEVER printed or displayed — only saved to a file.
    """
    # Generate a new private key using the cryptography library.
    # Ed25519 key generation is cryptographically secure by default.
    private_key = Ed25519PrivateKey.generate()

    # Derive the matching public key from the private key.
    public_key = private_key.public_key()

    # Convert the private key into PEM format (a standard, readable format
    # for storing keys). We do NOT encrypt it with a password here to keep
    # things simple for this beginner project.
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Convert the public key into PEM format.
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Make sure the keys folder exists before saving files into it.
    os.makedirs(KEYS_DIR, exist_ok=True)

    # Save the private key to its own file.
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_pem)

    # Save the public key to its own file.
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_pem)

    print("\n[OK] Ed25519 key pair generated successfully!")
    print(f"     Private key saved to: {PRIVATE_KEY_PATH}  (keep this secret!)")
    print(f"     Public key saved to:  {PUBLIC_KEY_PATH}\n")


# ---------------------------------------------------------------------------
# LOADING KEYS FROM DISK
# ---------------------------------------------------------------------------

def load_private_key():
    """
    Loads the Ed25519 private key from the keys folder.
    Returns None if the key file does not exist.
    """
    if not os.path.exists(PRIVATE_KEY_PATH):
        return None

    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    return private_key


def load_public_key():
    """
    Loads the Ed25519 public key from the keys folder.
    Returns None if the key file does not exist.
    """
    if not os.path.exists(PUBLIC_KEY_PATH):
        return None

    with open(PUBLIC_KEY_PATH, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    return public_key


# ---------------------------------------------------------------------------
# MESSAGE INPUT
# ---------------------------------------------------------------------------

def get_message():
    """
    Asks the user whether they want to type a message manually or use the
    default message stored in messages/message.txt.

    Returns the chosen message as a string, or None if something went wrong.
    """
    print("\nChoose message input method:")
    print("  1. Type a message manually")
    print("  2. Use the default message from messages/message.txt")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        message = input("Type your message: ").strip()
        if not message:
            print("[ERROR] Message cannot be empty.")
            return None
        return message

    elif choice == "2":
        if not os.path.exists(DEFAULT_MESSAGE_PATH):
            print(f"[ERROR] Default message file not found at {DEFAULT_MESSAGE_PATH}")
            return None
        with open(DEFAULT_MESSAGE_PATH, "r", encoding="utf-8") as f:
            message = f.read().strip()
        if not message:
            print("[ERROR] Default message file is empty.")
            return None
        return message

    else:
        print("[ERROR] Invalid choice.")
        return None


# ---------------------------------------------------------------------------
# SIGNING
# ---------------------------------------------------------------------------

def sign_message(message: str):
    """
    Signs the given message using the private key and saves the signature
    to signatures/signature.bin.
    """
    private_key = load_private_key()
    if private_key is None:
        print("[ERROR] Private key not found. Please generate keys first (Option 1).")
        return

    # Ed25519 signs raw bytes, so we encode the message string as UTF-8 bytes.
    message_bytes = message.encode("utf-8")

    # The sign() method produces a 64-byte digital signature.
    signature = private_key.sign(message_bytes)

    # Make sure the signatures folder exists.
    os.makedirs(SIGNATURES_DIR, exist_ok=True)

    # Save the raw signature bytes to a file.
    with open(SIGNATURE_PATH, "wb") as f:
        f.write(signature)

    print("\n[OK] Message signed successfully!")
    print(f"     Message: {message}")
    print(f"     Signature (hex): {signature.hex()}")
    print(f"     Signature saved to: {SIGNATURE_PATH}\n")


# ---------------------------------------------------------------------------
# VERIFICATION
# ---------------------------------------------------------------------------

def verify_signature(message: str, signature: bytes = None, label: str = "Message"):
    """
    Verifies a signature against a given message using the public key.

    If 'signature' is not provided, it is loaded from signatures/signature.bin.
    'label' is just used to make the printed output clearer (e.g. "Original"
    vs "Tampered").

    Returns True if the signature is valid, False otherwise.
    """
    public_key = load_public_key()
    if public_key is None:
        print("[ERROR] Public key not found. Please generate keys first (Option 1).")
        return False

    if signature is None:
        if not os.path.exists(SIGNATURE_PATH):
            print("[ERROR] Signature file not found. Please sign a message first (Option 2).")
            return False
        with open(SIGNATURE_PATH, "rb") as f:
            signature = f.read()

    message_bytes = message.encode("utf-8")

    print("=" * 40)
    print("SIGNATURE VERIFICATION")
    print("=" * 40)
    print(f"{label}: {message}")

    try:
        # verify() raises InvalidSignature if the signature does not match.
        # It returns None (no exception) if the signature IS valid.
        public_key.verify(signature, message_bytes)
        print("Status: VALID")
        print("The message has not been modified.")
        print("=" * 40 + "\n")
        return True

    except InvalidSignature:
        print("Status: INVALID")
        print("The message or signature may have been modified.")
        print("=" * 40 + "\n")
        return False


# ---------------------------------------------------------------------------
# TAMPERING DEMONSTRATION
# ---------------------------------------------------------------------------

def demonstrate_tampering():
    """
    Demonstrates Ed25519's tamper-detection property:
    1. Signs an original message.
    2. Verifies the original message (should be VALID).
    3. Slightly changes the message.
    4. Verifies the tampered message against the ORIGINAL signature
       (should be INVALID).
    """
    if load_private_key() is None or load_public_key() is None:
        print("[ERROR] Keys not found. Please generate keys first (Option 1).")
        return

    original_message = "Hello, this is my first Ed25519 digital signature."
    tampered_message = "Hello, this is my modified Ed25519 digital signature."

    print("\n--- TAMPERING DEMONSTRATION ---")
    print(f"Original message: {original_message}")
    print(f"Tampered message: {tampered_message}\n")

    # Step 1: Sign the ORIGINAL message.
    private_key = load_private_key()
    signature = private_key.sign(original_message.encode("utf-8"))
    print(f"Signature generated for the original message (hex): {signature.hex()}\n")

    # Step 2: Verify the original message against this signature.
    verify_signature(original_message, signature, label="Original Message")

    # Step 3 & 4: Verify the TAMPERED message using the SAME signature.
    verify_signature(tampered_message, signature, label="Tampered Message")

    print("Explanation:")
    print("Ed25519 signatures are mathematically tied to the EXACT bytes of")
    print("the message that was signed. Even a single changed character")
    print("produces a completely different message, so the original")
    print("signature no longer matches it. This is why the tampered message")
    print("fails verification — this is how digital signatures detect")
    print("tampering and protect message integrity.\n")


# ---------------------------------------------------------------------------
# FULL DEMONSTRATION (for presentations)
# ---------------------------------------------------------------------------

def run_full_demo():
    """
    Runs the entire demonstration automatically, in order:
    1. Generate keys
    2. Sign the default message
    3. Verify the original message
    4. Demonstrate tampering
    Useful for live college presentations.
    """
    print("\n########################################")
    print(" RUNNING COMPLETE DEMONSTRATION")
    print("########################################\n")

    print("STEP 1: Generating keys...")
    generate_keys()

    print("STEP 2: Signing the default message...")
    if not os.path.exists(DEFAULT_MESSAGE_PATH):
        print(f"[ERROR] Default message file not found at {DEFAULT_MESSAGE_PATH}")
        return
    with open(DEFAULT_MESSAGE_PATH, "r", encoding="utf-8") as f:
        message = f.read().strip()
    sign_message(message)

    print("STEP 3: Verifying the original message...")
    verify_signature(message, label="Original Message")

    print("STEP 4: Demonstrating tampering...")
    demonstrate_tampering()

    print("########################################")
    print(" DEMONSTRATION COMPLETE")
    print("########################################\n")


# ---------------------------------------------------------------------------
# MENU / MAIN PROGRAM
# ---------------------------------------------------------------------------

def print_menu():
    print("=" * 40)
    print(" ED25519 DIGITAL SIGNATURE DEMO")
    print("=" * 40)
    print("1. Generate Keys")
    print("2. Sign Message")
    print("3. Verify Signature")
    print("4. Demonstrate Tampering")
    print("5. Run Complete Demonstration")
    print("6. Exit")
    print()


def main():
    """
    Main program loop. Displays the menu and calls the appropriate
    function based on the user's choice.
    """
    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            generate_keys()

        elif choice == "2":
            message = get_message()
            if message is not None:
                sign_message(message)

        elif choice == "3":
            message = get_message()
            if message is not None:
                verify_signature(message)

        elif choice == "4":
            demonstrate_tampering()

        elif choice == "5":
            run_full_demo()

        elif choice == "6":
            print("Exiting program. Goodbye!")
            break

        else:
            print("[ERROR] Invalid menu choice. Please enter a number from 1 to 6.\n")


if __name__ == "__main__":
    main()
