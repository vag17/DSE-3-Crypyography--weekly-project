# Week-3 — Blockchain-Based Decentralized Identity (DID) and Verifiable Credentials

A beginner-friendly, fully local, educational Python project for a
cybersecurity college course. It demonstrates the core ideas behind
Decentralized Identity (DID) and Verifiable Credentials (VC), backed by a
very simple simulated blockchain ledger.

> **Honesty note (please read):** This project is a local, offline
> **simulation** built for learning. It is **not** a real blockchain
> network, does **not** connect to Ethereum/Polygon/Solana/Hyperledger,
> requires **no wallet, no cryptocurrency, and no internet access**, and
> does **not** implement a real, production-grade W3C DID method. Every
> claim below is scoped to "this simulation," not to real-world systems.

---

## 1. Project Overview

This program plays out a small story with three characters:

- **University (Issuer)** — creates a digital identity and issues a signed
  digital certificate to a student.
- **Student (Holder)** — receives and holds the certificate.
- **Company (Verifier)** — checks whether the certificate is genuine and
  unmodified.

Everything happens on your own computer. Keys, identities, credentials, and
a simple "blockchain" ledger are all stored as local files.

## 2. Problem Statement

Traditional paper or PDF certificates have some well-known weaknesses:

- **Manual verification** — an employer often has to call the university
  or check a physical seal/signature by eye.
- **Fake certificates** — a certificate image or PDF can be edited fairly
  easily by anyone with basic tools.
- **Silent modification** — a value like a grade or course name can be
  changed after issuance without an easy way to detect it.
- **Centralized identity systems** — a single database or office is the
  only place identity/credential truth lives, which is a single point of
  failure or manipulation.

This project does **not** claim to solve identity fraud everywhere — it
shows, at a small and understandable scale, how public-key cryptography
and hash-linked records can make tampering detectable.

## 3. Project Objective

To demonstrate, using simple local Python code:

- How a Decentralized Identifier (DID) can be created from a public key.
- How a DID Document publishes a public key for others to use.
- How a Verifiable Credential is created and digitally signed.
- How a verifier checks a signature using only the public key.
- How a simple hash-chained ledger ("blockchain") can record events and
  reveal tampering.

## 4. What is Decentralized Identity?

In a **centralized** identity system, one organization (e.g. a college
database or a government ID office) is the only place that can confirm
"this identity is real." In a **decentralized identity (DID)** system, an
identity is instead tied to a cryptographic key pair that the identity
owner controls, and it can be checked by anyone who has the matching
public key — without calling a central office every time.

In this project, the "decentralization" being demonstrated is conceptual
and educational: the DID is derived directly from a public key using math
(a hash function), not from a central authority handing out ID numbers.

## 5. What is a DID?

A DID here looks like:

```
did:local:7a91c4...
```

- `did` — tells you it is a Decentralized Identifier.
- `local` — the "method" name. Real DIDs use methods like `did:web`,
  `did:key`, or `did:ethr`. `local` clearly marks this as our own
  **educational, non-production** method — it only means "generated for
  this local demo."
- `7a91c4...` — a SHA-256 hash of the owner's public key. Because it is a
  hash of the public key, two different keys will (for all practical
  purposes) never produce the same DID.

This is a simplified stand-in for real DID methods, built only to teach
the underlying idea.

## 6. What is a DID Document?

A DID Document is the "profile page" for a DID. Anyone who wants to verify
something signed by a DID looks up its DID Document to find the matching
public key. In this project, `data/did_document.json` plays that role:

```json
{
    "id": "did:local:7a91c4...",
    "public_key": "Base64-encoded-public-key",
    "authentication": true
}
```

The private key is **never** written into this file — only the public
key, which is safe to share with anyone.

## 7. What is a Verifiable Credential?

A Verifiable Credential (VC) is a digitally signed statement made by an
**issuer** about a **subject**. In this project:

```
University (Issuer)  →  Student (Holder)  →  Company (Verifier)
```

- The **University** issues the credential and signs it with its private
  key.
- The **Student** holds the credential and can present it to others.
- The **Company** verifies the credential using the University's public
  key (found via the DID Document).

## 8. What is a Digital Signature?

A digital signature proves two things:

1. **Authenticity** — the credential really was signed by the holder of a
   specific private key.
2. **Integrity** — the signed data has not been changed since signing.

This project uses **Ed25519**, a modern, fast, and secure signature
algorithm:

```
Credential  →  Ed25519 sign (Issuer PRIVATE key)  →  Signature
Credential + Signature  →  Ed25519 verify (Issuer PUBLIC key)  →  VALID / INVALID
```

If even one character of the signed data changes, verification fails.

## 9. What is Blockchain?

At its core, a blockchain is a list of **blocks**, where each block stores
some data plus the hash of the previous block:

```
Block 0 (Genesis)        Block 1                    Block 2
previous_hash = "0"  →   previous_hash = Block0.hash → previous_hash = Block1.hash
hash = H(...)             hash = H(...)                hash = H(...)
```

Because each block's hash depends on the previous block's hash, changing
any old block breaks the chain — every hash after that point stops
matching, which is easy to detect.

## 10. How This Project Simulates Blockchain

**This project is NOT a real decentralized blockchain.** There is no
peer-to-peer network, no miners, no consensus algorithm, and no
distributed nodes. It is a **local simulation**, stored entirely in
`data/blockchain.json`, that demonstrates:

- Blocks
- SHA-256 hashes
- Previous-hash linking
- Append-only record keeping
- Tamper detection through hash mismatches

## 11. System Architecture

```
ISSUER (University)
   |
   | generates Ed25519 keys, creates DID
   v
DID DOCUMENT  (publishes public key)
   |
   | signs credential with private key
   v
VERIFIABLE CREDENTIAL  (student's certificate)
   |
   v
HOLDER (Student)
   |
   | presents credential
   v
VERIFIER (Company)
   |
   v
VERIFY SIGNATURE using issuer's public key (via DID Document)
   |
   v
VALID / INVALID
```

Alongside this flow, every important event (DID created, credential
issued) is also recorded as a block in the local simulated blockchain, so
the whole history can be checked for tampering at any time.

## 12. Project Structure

```
Week-3/
│
├── main.py                 # All program logic (see section 18 for functions)
├── requirements.txt         # Python dependencies (just "cryptography")
├── README.md                 # This file
├── .gitignore                # Ignores venv/, __pycache__, and private keys
│
├── data/
│   ├── did_document.json    # Issuer's DID + public key (auto-generated)
│   ├── credential.json       # Currently issued credential (auto-generated)
│   └── blockchain.json       # The simulated blockchain ledger (auto-generated)
│
├── keys/
│   └── .gitkeep               # Placeholder; issuer_*.pem files are generated here
│
└── output/
    └── .gitkeep               # Placeholder; credential_backup.json goes here
```

All folders and files inside `data/`, `keys/`, and `output/` are created
or overwritten automatically by the program — you never edit them by hand.

## 13. Requirements

- Python 3.8 or newer
- The `cryptography` Python package (used only for Ed25519 key generation
  and digital signatures)

Everything else (`json`, `hashlib`, `datetime`, `os`, `base64`) is part of
Python's standard library — nothing else needs to be installed.

## 14. Installation (Windows)

Open the project folder in **VS Code**, then open a terminal
(Command Prompt or PowerShell) and run:

```
python --version
```

```
python -m venv venv
```

```
venv\Scripts\activate
```

```
pip install -r requirements.txt
```

## 15. How to Run

```
python main.py
```

## 16. Recommended College Demonstration

1. Run `python main.py`.
2. Select option **8** (Run Complete Demonstration).
3. Point out the identity generation step (DID printed on screen).
4. Point out the DID Document that gets created and printed.
5. Point out the sample credential being issued for "Rahul Sharma".
6. Point out "Signature Verification: VALID" and "FINAL RESULT: CREDENTIAL VALID".
7. Point out "BLOCKCHAIN STATUS: VALID".
8. Point out the tampering demonstration (course changed from BCA to MCA).
9. Point out "Signature Verification: INVALID" and "TAMPERING DETECTED".
10. Explain that the original credential is then automatically restored
    from `output/credential_backup.json`, and re-verified as VALID again.

## 17. Expected Output (example — your hashes/DID will differ)

```
Identity Generated Successfully

DID:
did:local:944c847135dcb0e5a2a27135582170ec9503b15273eb0ab45e3a4bdcefa93c45

...

=========================================
CREDENTIAL VERIFICATION
=========================================
Credential Type: StudentCredential
Holder: Rahul Sharma
Course: BCA Cybersecurity
University: Example University

Signature Verification: VALID
DID Verification: VALID
Credential Status: ACTIVE
-----------------------------------------
FINAL RESULT: CREDENTIAL VALID
-----------------------------------------
```

*(This is example/sample output — your actual DID string, timestamps, and
hash values will be different every time you generate new keys.)*

## 18. Complete Workflow

```
Key Generation
      ↓
DID Creation (SHA-256 hash of public key)
      ↓
DID Document (publishes public key)
      ↓
Credential Creation (student details entered)
      ↓
Digital Signature (Ed25519, using issuer private key)
      ↓
Blockchain Record (event appended as a new block)
      ↓
Credential Verification (checked with issuer public key)
      ↓
Tampering Detection (modified data fails signature check)
```

Core functions used throughout the program:

`generate_keys()`, `create_did()`, `create_did_document()`,
`load_private_key()`, `load_public_key()`, `create_credential()`,
`sign_credential()`, `verify_credential()`, `create_genesis_block()`,
`add_block()`, `calculate_block_hash()`, `verify_blockchain()`,
`display_blockchain()`, `demonstrate_tampering()`, `restore_backup()`,
`main()`.

## 19. Security Properties

- **Integrity** — Ed25519 signatures and SHA-256 block hashes both reveal
  if data has been changed after the fact.
- **Authentication** — only someone holding the issuer's private key
  could have produced a valid signature for a credential.
- **Credential authenticity** — a verifier can independently confirm a
  credential's origin using only public information (the DID Document).
- **Tamper detection** — modifying the credential JSON file or a
  blockchain block by hand will cause verification to fail.
- **Decentralized identity concepts** — the DID is derived mathematically
  from a public key rather than assigned by a central office, illustrating
  the key idea behind DIDs (even though this demo runs on one computer).

Private keys are never printed to the screen, never stored inside a
credential, and never stored inside a blockchain block.

## 20. Limitations

- This is a **local simulation only** — everything runs on a single
  machine, in single JSON files.
- There is **no real blockchain network**, no peer-to-peer nodes, and no
  consensus mechanism (no Proof of Work / Proof of Stake).
- There is **no production DID method** — `did:local` is not registered
  with or recognized by any real DID resolver.
- There is **no real identity provider** — nothing here is connected to
  a government ID, university database, or other authority.
- There is **no production credential revocation system** — the
  `credential_status` field is just a simple demonstration flag.
- Private keys are stored unencrypted on disk for simplicity, which would
  not be acceptable in a production system.

## 21. Future Improvements

- Real blockchain / distributed ledger technology (DLT) integration
- Real W3C DID methods (e.g. `did:web`, `did:key`)
- Full W3C Verifiable Credentials Data Model compliance
- QR-code based credential presentation
- A mobile "wallet" app for holders
- A proper credential revocation registry
- Zero-knowledge proofs for selective disclosure
- Smart-contract-based issuance/verification
- A web-based front end
- A real database instead of JSON files
- Multi-user / multi-issuer support

---

## How to Explain This Project in 30 Seconds

"This project shows how a university can create a digital identity, issue
a digitally signed certificate to a student using Ed25519 cryptography,
and let any employer verify that certificate using only the university's
public key. I also built a simple local blockchain — just SHA-256 linked
blocks — to record these events and prove that if anyone edits the data
afterward, the signature and hash checks immediately catch it. It's a
local, educational simulation, not a real production blockchain network."

## Simple Architecture Diagram

```
   University                Student                 Company
  (Issuer, has              (Holder, gets            (Verifier, checks
   private key)              credential)              signature)
        │                        │                         │
        │──── issues signed ────>│                         │
        │      credential        │                         │
        │                        │──── presents ──────────>│
        │                        │      credential          │
        │                        │                         │
        │<─────────── public key looked up via DID Document ────
        │                        │                         │
        │                        │                    VALID / INVALID
```

## Troubleshooting

**"'python' is not recognized as an internal or external command"**
Python is not installed or not added to PATH. Reinstall Python from
python.org and make sure to check "Add Python to PATH" during setup.

**"'pip' is not recognized as an internal or external command"**
Try `python -m pip install -r requirements.txt` instead of `pip install ...`.

**Error while installing the `cryptography` package**
Make sure you are using a reasonably recent Python 3 version (3.8+) and
have an active internet connection for the one-time install. Try
upgrading pip first: `python -m pip install --upgrade pip`.

**Virtual environment won't activate (PowerShell)**
If you see a script-execution error, run PowerShell as Administrator and
execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`,
then try `venv\Scripts\activate` again.

**`FileNotFoundError`**
Make sure you are running `python main.py` from inside the `Week-3`
folder. The program also auto-creates the `data/`, `keys/`, and `output/`
folders on startup, so this usually only happens if a file was deleted
mid-run.

**"Signature Verification: INVALID" when you didn't expect it**
This is expected right after running option 7 (tampering demo) — it means
detection worked. If you see it unexpectedly elsewhere, make sure you
haven't manually edited `data/credential.json` or `data/did_document.json`.

**JSON errors when reading a data file**
This usually means a `.json` file was manually edited and is no longer
valid JSON. Delete the affected file in `data/` and re-run option 1, 2,
or 3 to regenerate it.

**Permission errors when writing files**
Make sure the `Week-3` folder is not open as read-only and that you have
write permission to the folder (avoid running from inside a `.zip` file
without extracting it first).

---

## 10 Likely Viva Questions (with simple answers)

1. **What is a DID?**
   A Decentralized Identifier — an ID derived from a cryptographic key
   pair instead of being assigned by a central authority.

2. **What is a DID Document?**
   A small document that publishes the public key associated with a DID,
   so others can verify signatures made by that DID's owner.

3. **What is a Verifiable Credential?**
   A digitally signed statement (like a certificate) made by an issuer
   about a subject, that anyone can cryptographically verify.

4. **Who is the issuer?**
   The University — it creates the DID and signs the credential.

5. **Who is the holder?**
   The Student — they receive the credential and can present it to others.

6. **Who is the verifier?**
   The Company/Employer — they check the credential's signature to decide
   whether to trust it.

7. **Why are digital signatures used?**
   To prove the credential really came from the issuer and has not been
   changed since it was signed.

8. **Why is Ed25519 used?**
   It is a modern, fast, and secure public-key signature algorithm that is
   simple to use correctly compared to older alternatives.

9. **What is blockchain hashing?**
   Turning block data (index, timestamp, data, previous hash) into a
   fixed-size fingerprint using SHA-256, so any change to the data
   produces a completely different hash.

10. **What happens if someone modifies the credential?**
    The signature no longer matches the modified data, so verification
    returns INVALID — this is how tampering is detected.

**Bonus questions:**

- **Is this a real blockchain?** No — it is a local, single-file
  simulation with no network or consensus mechanism, built purely to
  teach the concepts of blocks, hashes, and tamper detection.
- **What is the difference between a DID and a traditional username?**
  A username is usually assigned and controlled by a central service
  (e.g. a college login system). A DID is derived from a key pair that
  the owner controls, so it does not depend on one central authority.
- **What is the role of the public key?** It lets anyone verify a
  signature made by the matching private key, without being able to
  create new signatures themselves.
- **What is the role of the private key?** It is kept secret by the
  issuer and used to create signatures that only that issuer could have
  produced.
