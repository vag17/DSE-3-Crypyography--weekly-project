"""
Week-3 - Blockchain-Based Decentralized Identity (DID) and Verifiable Credentials
-----------------------------------------------------------------------------
A BEGINNER-FRIENDLY, FULLY LOCAL, EDUCATIONAL demo project.

This program simulates (it does NOT implement a real production system):
    - A Decentralized Identifier (DID) for an issuer (a "University")
    - A DID Document that publishes the issuer's public key
    - A Verifiable Credential (a "degree/course certificate") signed with Ed25519
    - A very simple local "blockchain" (a chain of SHA-256 linked JSON blocks)
      used only to record that certain events happened (DID created,
      credential issued) and to demonstrate tamper detection.

IMPORTANT / HONESTY NOTE:
    This is NOT a real decentralized blockchain network. There is no peer to
    peer network, no consensus algorithm (Proof of Work / Proof of Stake),
    and no real W3C DID method. Everything runs on your own computer, in a
    single JSON file, so you can SEE and EXPLAIN how blocks/hashes work.

No private key is ever printed to the screen or saved inside a credential
or block. Only public information is shared with the "verifier".
"""

import os
import json
import base64
import hashlib
import datetime

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


# ---------------------------------------------------------------------------
# FOLDER / FILE PATHS
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
KEYS_DIR = os.path.join(BASE_DIR, "keys")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "issuer_private_key.pem")
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "issuer_public_key.pem")

DID_DOCUMENT_PATH = os.path.join(DATA_DIR, "did_document.json")
CREDENTIAL_PATH = os.path.join(DATA_DIR, "credential.json")
BLOCKCHAIN_PATH = os.path.join(DATA_DIR, "blockchain.json")
CREDENTIAL_BACKUP_PATH = os.path.join(OUTPUT_DIR, "credential_backup.json")


def ensure_folders():
    """Create the required folders automatically if they do not exist."""
    for folder in (DATA_DIR, KEYS_DIR, OUTPUT_DIR):
        os.makedirs(folder, exist_ok=True)


# ---------------------------------------------------------------------------
# STEP 1: KEY GENERATION
#
#   Private Key  -> used to SIGN credentials (must stay secret, never shown)
#   Public Key   -> used to VERIFY credentials (safe to share with everyone)
# ---------------------------------------------------------------------------

def generate_keys():
    """Generate an Ed25519 key pair for the issuer and save them as PEM files."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_pem)
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_pem)

    # NOTE: the private key is written to a file only. It is never printed.
    return private_key, public_key


def load_private_key():
    """Load the issuer's private key from disk (used only for signing)."""
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key():
    """Load the issuer's public key from disk (used for verification)."""
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def public_key_to_b64(public_key: Ed25519PublicKey) -> str:
    """Encode a public key's raw bytes as Base64 text (readable/storable)."""
    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode("utf-8")


def public_key_from_b64(b64_string: str) -> Ed25519PublicKey:
    """Rebuild a public key object from its Base64 raw representation."""
    raw = base64.b64decode(b64_string)
    return Ed25519PublicKey.from_public_bytes(raw)


# ---------------------------------------------------------------------------
# STEP 2: DID CREATION
#
#   A DID here is simply:  did:local:<sha256 hash of the public key>
#   This is an EDUCATIONAL SIMULATION, not a real W3C-registered DID method.
# ---------------------------------------------------------------------------

def create_did(public_key: Ed25519PublicKey) -> str:
    """Create a simple local DID from the SHA-256 hash of the public key."""
    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    digest = hashlib.sha256(raw).hexdigest()
    return f"did:local:{digest}"


# ---------------------------------------------------------------------------
# STEP 3: DID DOCUMENT
#
#   The DID Document is what a verifier looks up to find the public key
#   that belongs to a given DID. In a real system this might live on a
#   blockchain or distributed registry; here it is simply a JSON file.
# ---------------------------------------------------------------------------

def create_did_document(did: str, public_key: Ed25519PublicKey) -> dict:
    """Build and save the DID Document (never contains the private key)."""
    did_document = {
        "id": did,
        "public_key": public_key_to_b64(public_key),
        "authentication": True,
        "note": "Educational local DID simulation (not a production W3C DID).",
    }
    with open(DID_DOCUMENT_PATH, "w") as f:
        json.dump(did_document, f, indent=4)
    return did_document


def load_did_document() -> dict:
    with open(DID_DOCUMENT_PATH, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# STEP 4: VERIFIABLE CREDENTIAL + DIGITAL SIGNATURE
#
#   Credential  ->  Ed25519 signature  ->  signed with Issuer PRIVATE key
#   Credential + Signature -> checked with Issuer PUBLIC key -> VALID/INVALID
# ---------------------------------------------------------------------------

def canonical_bytes(credential_without_proof: dict) -> bytes:
    """
    Turn a credential (without its 'proof' field) into a deterministic byte
    string so that signing and verifying always hash the same input.
    Uses sorted keys and no extra whitespace.
    """
    return json.dumps(
        credential_without_proof, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def create_credential(name, student_id, course, university, issuer_did) -> dict:
    """Build the (unsigned) Verifiable Credential dictionary."""
    credential = {
        "type": "StudentCredential",
        "issuer": issuer_did,
        "subject": {
            "name": name,
            "student_id": student_id,
            "course": course,
            "university": university,
        },
        "issued_at": datetime.date.today().isoformat(),
        "credential_status": "active",
    }
    return credential


def sign_credential(credential: dict, private_key: Ed25519PrivateKey) -> dict:
    """Sign the credential and attach the signature under 'proof'."""
    # IMPORTANT: sign the credential BEFORE the proof field is added.
    data_to_sign = canonical_bytes(credential)
    signature = private_key.sign(data_to_sign)
    signed_credential = dict(credential)  # shallow copy
    signed_credential["proof"] = {
        "type": "Ed25519Signature",
        "signature": base64.b64encode(signature).decode("utf-8"),
    }
    return signed_credential


def verify_credential_signature(credential: dict, public_key: Ed25519PublicKey) -> bool:
    """Verify a credential's Ed25519 signature. Returns True/False."""
    if "proof" not in credential or "signature" not in credential["proof"]:
        return False

    signature_b64 = credential["proof"]["signature"]
    signature = base64.b64decode(signature_b64)

    # Recreate exactly what was originally signed: the credential WITHOUT proof.
    credential_copy = dict(credential)
    credential_copy.pop("proof")
    data_that_was_signed = canonical_bytes(credential_copy)

    try:
        public_key.verify(signature, data_that_was_signed)
        return True
    except InvalidSignature:
        return False


# ---------------------------------------------------------------------------
# STEP 5: SIMPLE SIMULATED BLOCKCHAIN
#
#   block_hash = SHA256(index + timestamp + data + previous_hash)
#   Each block "points" to the previous block via previous_hash, forming a
#   tamper-evident chain. This is a teaching simulation, not a real network.
# ---------------------------------------------------------------------------

def calculate_block_hash(index, timestamp, data, previous_hash) -> str:
    block_string = f"{index}{timestamp}{data}{previous_hash}"
    return hashlib.sha256(block_string.encode("utf-8")).hexdigest()


def load_blockchain() -> list:
    if not os.path.exists(BLOCKCHAIN_PATH) or os.path.getsize(BLOCKCHAIN_PATH) == 0:
        return []
    with open(BLOCKCHAIN_PATH, "r") as f:
        return json.load(f)


def save_blockchain(chain: list):
    with open(BLOCKCHAIN_PATH, "w") as f:
        json.dump(chain, f, indent=4)


def create_genesis_block() -> dict:
    timestamp = datetime.datetime.now().isoformat()
    index = 0
    data = "Genesis Block"
    previous_hash = "0"
    block_hash = calculate_block_hash(index, timestamp, data, previous_hash)
    return {
        "index": index,
        "timestamp": timestamp,
        "data": data,
        "previous_hash": previous_hash,
        "hash": block_hash,
    }


def add_block(data: str) -> dict:
    """Append a new block describing `data` to the local blockchain file."""
    chain = load_blockchain()

    if len(chain) == 0:
        genesis = create_genesis_block()
        chain.append(genesis)

    previous_block = chain[-1]
    index = previous_block["index"] + 1
    timestamp = datetime.datetime.now().isoformat()
    previous_hash = previous_block["hash"]
    block_hash = calculate_block_hash(index, timestamp, data, previous_hash)

    new_block = {
        "index": index,
        "timestamp": timestamp,
        "data": data,
        "previous_hash": previous_hash,
        "hash": block_hash,
    }
    chain.append(new_block)
    save_blockchain(chain)
    return new_block


def verify_blockchain() -> bool:
    """Recalculate every block's hash and check the chain of previous_hash links."""
    chain = load_blockchain()

    print("=" * 41)
    print("BLOCKCHAIN VERIFICATION")
    print("=" * 41)

    if not chain:
        print("Blockchain is empty. Nothing to verify.")
        return False

    overall_valid = True

    for i, block in enumerate(chain):
        recalculated_hash = calculate_block_hash(
            block["index"], block["timestamp"], block["data"], block["previous_hash"]
        )

        hash_ok = recalculated_hash == block["hash"]

        if i == 0:
            link_ok = block["previous_hash"] == "0"
        else:
            link_ok = block["previous_hash"] == chain[i - 1]["hash"]

        block_valid = hash_ok and link_ok
        if not block_valid:
            overall_valid = False

        status = "VALID" if block_valid else "INVALID"
        print(f"Block {block['index']}: {status}")

    print("-" * 41)
    if overall_valid:
        print("BLOCKCHAIN STATUS: VALID")
        print("No tampering detected.")
    else:
        print("BLOCKCHAIN STATUS: INVALID")
        print("Tampering detected.")
    print("-" * 41)

    return overall_valid


def display_blockchain():
    chain = load_blockchain()

    print("=" * 41)
    print("BLOCKCHAIN")
    print("=" * 41)

    if not chain:
        print("Blockchain is empty. Nothing has been recorded yet.")
        return

    for block in chain:
        print()
        print(f"Block {block['index']}")
        print(f"Previous Hash: {block['previous_hash']}")
        print(f"Hash: {block['hash']}")
        print()
        print("Data:")
        print(block["data"])
        print("-" * 41)


# ---------------------------------------------------------------------------
# STEP 6: HIGH-LEVEL CREDENTIAL VERIFICATION (uses DID Document + Blockchain)
# ---------------------------------------------------------------------------

def load_credential() -> dict:
    with open(CREDENTIAL_PATH, "r") as f:
        return json.load(f)


def save_credential(credential: dict, path=CREDENTIAL_PATH):
    with open(path, "w") as f:
        json.dump(credential, f, indent=4)


def verify_credential():
    """Full credential verification workflow used by menu option 4."""
    print("=" * 41)
    print("CREDENTIAL VERIFICATION")
    print("=" * 41)

    if not os.path.exists(CREDENTIAL_PATH):
        print("No credential found. Please issue a credential first (option 3).")
        return False

    credential = load_credential()

    print(f"Credential Type: {credential.get('type')}")
    print(f"Holder: {credential.get('subject', {}).get('name')}")
    print(f"Course: {credential.get('subject', {}).get('course')}")
    print(f"University: {credential.get('subject', {}).get('university')}")
    print()

    # DID verification: does the issuer DID in the credential match the DID
    # Document we have on file (i.e. can we resolve the issuer's public key)?
    did_valid = False
    signature_valid = False

    if os.path.exists(DID_DOCUMENT_PATH):
        did_document = load_did_document()
        did_valid = did_document.get("id") == credential.get("issuer")

        if did_valid:
            issuer_public_key = public_key_from_b64(did_document["public_key"])
            signature_valid = verify_credential_signature(credential, issuer_public_key)
    else:
        print("No DID Document found. Cannot resolve issuer public key.")

    print(f"Signature Verification: {'VALID' if signature_valid else 'INVALID'}")
    print(f"DID Verification: {'VALID' if did_valid else 'INVALID'}")
    print(f"Credential Status: {credential.get('credential_status', 'unknown').upper()}")
    print("-" * 41)

    final_valid = did_valid and signature_valid and credential.get("credential_status") == "active"
    if final_valid:
        print("FINAL RESULT: CREDENTIAL VALID")
    else:
        print("FINAL RESULT: CREDENTIAL INVALID")
    print("-" * 41)

    return final_valid


# ---------------------------------------------------------------------------
# STEP 7: TAMPERING DEMONSTRATION
# ---------------------------------------------------------------------------

def demonstrate_tampering():
    print("=" * 41)
    print("TAMPERING DEMONSTRATION")
    print("=" * 41)

    if not os.path.exists(CREDENTIAL_PATH):
        print("No credential found. Please issue a credential first (option 3).")
        return

    credential = load_credential()

    # 1. Back up the original, untouched credential first.
    save_credential(credential, CREDENTIAL_BACKUP_PATH)

    original_course = credential["subject"]["course"]
    print("Original Credential:")
    print(f"Course = {original_course}")
    print()

    # 2. Simulate an unauthorized modification.
    print("Simulating unauthorized modification...")
    tampered_credential = json.loads(json.dumps(credential))  # deep copy
    tampered_credential["subject"]["course"] = "MCA Cybersecurity"

    print()
    print("Modified Credential:")
    print(f"Course = {tampered_credential['subject']['course']}")
    print()

    # 3. Save the tampered version as the "current" credential and verify it.
    save_credential(tampered_credential, CREDENTIAL_PATH)

    print("Verifying modified credential...")
    did_document = load_did_document()
    issuer_public_key = public_key_from_b64(did_document["public_key"])
    signature_valid = verify_credential_signature(tampered_credential, issuer_public_key)

    print()
    print(f"Signature Verification: {'VALID' if signature_valid else 'INVALID'}")
    print("-" * 41)
    if not signature_valid:
        print("TAMPERING DETECTED")
        print("The credential has been modified after signing.")
    else:
        print("Tampering was NOT detected (this should not normally happen).")
    print("-" * 41)


def restore_backup():
    """Restore the original credential from output/credential_backup.json."""
    if not os.path.exists(CREDENTIAL_BACKUP_PATH):
        print("No backup found. Nothing to restore.")
        return False

    with open(CREDENTIAL_BACKUP_PATH, "r") as f:
        original_credential = json.load(f)

    save_credential(original_credential, CREDENTIAL_PATH)
    print("Original credential restored successfully.")
    return True


# ---------------------------------------------------------------------------
# MENU OPTION HANDLERS
# ---------------------------------------------------------------------------

def option_generate_identity():
    print("Generating issuer identity (Ed25519 key pair)...")
    private_key, public_key = generate_keys()
    did = create_did(public_key)

    print()
    print("Identity Generated Successfully")
    print()
    print("DID:")
    print(did)
    print()
    print("(The private key was saved to keys/issuer_private_key.pem")
    print(" and is never shown on screen.)")

    add_block(f"DID Created: {did}")
    return did


def option_create_did_document():
    if not os.path.exists(PUBLIC_KEY_PATH):
        print("No keys found. Please generate an identity first (option 1).")
        return

    public_key = load_public_key()
    did = create_did(public_key)
    did_document = create_did_document(did, public_key)

    print("DID Document created and saved to data/did_document.json")
    print()
    print(json.dumps(did_document, indent=4))


def _prompt_credential_fields():
    print("Enter the student's details for the credential:")
    name = input("Student Name: ").strip()
    student_id = input("Student ID: ").strip()
    course = input("Course: ").strip()
    university = input("University: ").strip()
    return name, student_id, course, university


def issue_credential(name, student_id, course, university):
    if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(DID_DOCUMENT_PATH):
        print("Please generate an identity (option 1) and a DID Document (option 2) first.")
        return None

    did_document = load_did_document()
    issuer_did = did_document["id"]

    private_key = load_private_key()
    credential = create_credential(name, student_id, course, university, issuer_did)
    signed_credential = sign_credential(credential, private_key)

    save_credential(signed_credential, CREDENTIAL_PATH)
    add_block(f"Credential Issued: {name} ({student_id})")

    print()
    print("Credential issued successfully.")
    print(f"Saved to: data/credential.json")
    return signed_credential


def option_issue_credential():
    name, student_id, course, university = _prompt_credential_fields()
    issue_credential(name, student_id, course, university)


def option_run_complete_demo():
    print("#" * 55)
    print("RUNNING COMPLETE DEMONSTRATION (using sample data)")
    print("#" * 55)
    print()

    print("[1/10] Generating identity...")
    option_generate_identity()
    print()

    print("[2/10] Creating DID Document...")
    option_create_did_document()
    print()

    print("[3/10] Issuing a SAMPLE credential (demonstration data only)...")
    print("       Name: Rahul Sharma | ID: BCA001 | Course: BCA Cybersecurity")
    print("       University: Example University")
    issue_credential("Rahul Sharma", "BCA001", "BCA Cybersecurity", "Example University")
    print()

    print("[4/10] Verifying the credential...")
    verify_credential()
    print()

    print("[5/10] Verifying the blockchain...")
    verify_blockchain()
    print()

    print("[6/10] Demonstrating credential tampering...")
    demonstrate_tampering()
    print()

    print("[7/10] Verifying the TAMPERED credential (should be INVALID)...")
    verify_credential()
    print()

    print("[8/10] Restoring the original credential from backup...")
    restore_backup()
    print()

    print("[9/10] Verifying the RESTORED (original) credential (should be VALID)...")
    verify_credential()
    print()

    print("[10/10] Complete demonstration finished.")
    print("#" * 55)


# ---------------------------------------------------------------------------
# MAIN MENU
# ---------------------------------------------------------------------------

MENU_TEXT = """
==================================================
 BLOCKCHAIN-BASED DECENTRALIZED IDENTITY DEMO
==================================================

1. Generate Identity
2. Create DID Document
3. Issue Verifiable Credential
4. Verify Credential
5. View Blockchain
6. Verify Blockchain
7. Demonstrate Credential Tampering
8. Run Complete Demonstration
9. Exit

Enter your choice: """


def main():
    ensure_folders()

    while True:
        choice = input(MENU_TEXT).strip()

        if choice == "1":
            option_generate_identity()
        elif choice == "2":
            option_create_did_document()
        elif choice == "3":
            option_issue_credential()
        elif choice == "4":
            verify_credential()
        elif choice == "5":
            display_blockchain()
        elif choice == "6":
            verify_blockchain()
        elif choice == "7":
            demonstrate_tampering()
        elif choice == "8":
            option_run_complete_demo()
        elif choice == "9":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
