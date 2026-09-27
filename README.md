# 🔐 Cybersecurity Weekly Projects

Welcome to my **Cybersecurity Weekly Projects Repository**.

This repository contains a series of hands-on cybersecurity projects developed as part of my weekly learning and practical work.

Each week focuses on a different cybersecurity concept, progressing from digital signatures to forensic log integrity and decentralized identity.

---

## 📚 Projects

| Week | Project | Main Concepts | Language |
|------|---------|---------------|----------|
| 🟢 Week 1 | Digital Signature Algorithm (Ed25519) Implementation and Verification | Digital Signatures, Authentication, Integrity | Python |
| 🟡 Week 2 | Cryptographic Hash-Chained Audit Logging System for Tamper-Proof Forensics | SHA-256, Hash Chaining, Audit Logs, Forensics | Python |
| 🔵 Week 3 | Blockchain-Based Decentralized Identity (DID) and Verifiable Credentials | DID, Verifiable Credentials, Digital Signatures, Blockchain | Python |

---

# 🟢 Week 1 — Digital Signature Algorithm (Ed25519)

### Digital Signature Algorithm (Ed25519) Implementation and Verification

This project demonstrates the use of **Ed25519 digital signatures** in Python. It generates a public/private key pair, signs a message using the private key, and verifies the signature using the public key.

The project also demonstrates how modifying a signed message causes signature verification to fail.

### 🔑 Concepts Covered

- Public Key Cryptography
- Public and Private Keys
- Ed25519
- Digital Signatures
- Message Integrity
- Signature Verification
- Tamper Detection

### 🔄 Basic Workflow

```text
Message
   ↓
Private Key
   ↓
Ed25519 Signature
   ↓
Public Key
   ↓
Verification
   ↓
VALID / INVALID
```

### 📂 Project Files

👉 [Open Week-1 Folder](./Week-1/)

👉 [Read Week-1 README](./Week-1/README.md)

---

# 🟡 Week 2 — Cryptographic Hash-Chained Audit Logging

### Cryptographic Hash-Chained Audit Logging System for Tamper-Proof Forensics

This project demonstrates how **cryptographic hash chaining** can be used to detect unauthorized modifications to audit logs.

Each log entry contains the hash of the previous entry. If an earlier entry is changed, the hash chain becomes invalid and the system can detect the modification.

### 🔑 Concepts Covered

- SHA-256
- Cryptographic Hashing
- Hash Chains
- Audit Logging
- Log Integrity
- Tamper Detection
- Digital Forensics
- Evidence Integrity

### 🔄 Basic Workflow

```text
Audit Entry 1
     ↓
   SHA-256
     ↓
   Hash 1
     ↓
Audit Entry 2 + Hash 1
     ↓
   SHA-256
     ↓
   Hash 2
     ↓
Audit Entry 3 + Hash 2
     ↓
   SHA-256
     ↓
   Hash 3
```

If an earlier entry is modified:

```text
Modified Entry
      ↓
Different Hash
      ↓
Broken Hash Chain
      ↓
⚠️ TAMPERING DETECTED
```

### 📂 Project Files

👉 [Open Week-2 Folder](./Week-2/)

👉 [Read Week-2 README](./Week-2/README.md)

---

# 🔵 Week 3 — Blockchain-Based Decentralized Identity

### Blockchain-Based Decentralized Identity (DID) and Verifiable Credentials

This project demonstrates the basic concepts behind **Decentralized Identity (DID)** and **Verifiable Credentials**.

The project simulates how an issuer can create a digitally signed credential, how a holder can receive it, and how a verifier can validate its authenticity.

A simple local blockchain simulation demonstrates how records can be linked using cryptographic hashes.

### 🔑 Concepts Covered

- Decentralized Identity
- DID
- DID Documents
- Verifiable Credentials
- Issuer / Holder / Verifier
- Ed25519 Digital Signatures
- SHA-256
- Blockchain Concepts
- Credential Verification
- Tamper Detection

### 🔄 Basic Workflow

```text
             ISSUER
                │
                ▼
          Create DID
                │
                ▼
       DID Document
                │
                ▼
     Create Credential
                │
                ▼
      Digital Signature
                │
                ▼
             HOLDER
                │
                ▼
            VERIFIER
                │
                ▼
       Verify Credential
                │
          ┌─────┴─────┐
          ▼           ▼
        VALID       INVALID
```

### ⛓️ Blockchain Simulation

```text
Genesis Block
      ↓
DID Created
      ↓
Credential Issued
      ↓
Hash Verification
      ↓
Tamper Detection
```

> **Note:** The blockchain used in this educational project is a local simulation designed to demonstrate blockchain concepts. It is not a production decentralized blockchain network.

### 📂 Project Files

👉 [Open Week-3 Folder](./Week-3/)

👉 [Read Week-3 README](./Week-3/README.md)

---

# 📈 Learning Progression

The three projects are designed to build on related cybersecurity concepts:

```text
                 CYBERSECURITY
                      │
                      ▼
        ┌──────────────────────────┐
        │         WEEK 1           │
        │   Digital Signatures     │
        │         Ed25519          │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │         WEEK 2           │
        │    Cryptographic Hash    │
        │      Hash Chaining       │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │         WEEK 3           │
        │   DID & Verifiable       │
        │      Credentials         │
        └──────────────────────────┘
```

---

# 🛠️ Technologies Used

### Programming

- Python 3

### Cryptography

- Ed25519
- SHA-256
- Digital Signatures
- Cryptographic Hashing

### Cybersecurity Concepts

- Authentication
- Data Integrity
- Tamper Detection
- Digital Forensics
- Audit Logging
- Decentralized Identity
- Verifiable Credentials
- Blockchain Concepts

---

# 🎯 Learning Objectives

Through these projects, this repository demonstrates practical understanding of:

- Cryptographic primitives
- Digital signatures
- Public-key cryptography
- Data integrity
- Authentication
- Cryptographic hashing
- Hash chaining
- Audit logging
- Digital forensics
- Decentralized identity
- Verifiable credentials
- Blockchain concepts
- Tamper detection

---

# 💻 How to Run

Each weekly project is independent and contains its own detailed `README.md`.

General workflow:

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd Cybersecurity-Projects
```

Then enter the required project:

```bash
cd Week-1
```

or:

```bash
cd Week-2
```

or:

```bash
cd Week-3
```

Follow the installation and execution instructions in that week's README.

---

# 📁 Repository Structure

```text
Cybersecurity-Projects/
│
├── README.md
│
├── Week-1/
│   ├── README.md
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── Week-2/
│   ├── README.md
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
└── Week-3/
    ├── README.md
    ├── main.py
    ├── requirements.txt
    └── ...
```

---

# 📖 Weekly Documentation

### 🟢 Week 1

[📄 Open Week-1 README](./Week-1/README.md)

Digital signatures using Ed25519, including signing, verification, and tamper detection.

### 🟡 Week 2

[📄 Open Week-2 README](./Week-2/README.md)

SHA-256 hash-chained audit logging for detecting modifications to forensic/audit records.

### 🔵 Week 3

[📄 Open Week-3 README](./Week-3/README.md)

A local educational simulation of decentralized identity, verifiable credentials, digital signatures, and blockchain-style records.

---

# 🚀 Future Projects

Future weekly projects may explore:

- 🔑 Advanced Cryptography
- 🌐 Network Security
- 🕵️ Digital Forensics
- 🤖 AI Security
- 🔐 Application Security
- 🧑‍💻 Ethical Hacking
- 🪪 Digital Identity
- ⛓️ Blockchain Security
- 🛡️ Cloud Security

---

# 👩‍💻 Author

**Vageesha Vats**

BCA Cybersecurity Student

### Areas of Interest

- Cybersecurity
- Ethical Hacking
- Digital Forensics
- Cryptography
- Application Security
- Emerging Security Technologies

---

## ⭐ Repository Note

Each weekly folder contains its own project files and detailed documentation.

Start with **Week-1** and progress through **Week-2** and **Week-3** to follow the project series.
