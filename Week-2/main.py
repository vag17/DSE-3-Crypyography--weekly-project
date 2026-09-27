"""
=====================================================================
 Week-2 : Cryptographic Hash-Chained Audit Logging System
 For Tamper-Proof Forensics (Educational Project)
=====================================================================

WHAT THIS PROGRAM DOES (in plain English):

Every time something happens (like a user logging in), we create an
"audit log entry" describing that event. We then calculate a SHA-256
hash of that entry's important details PLUS the hash of the previous
entry. This links every entry to the one before it, like links in a
chain.

If anyone secretly edits an old entry, the hash we recalculate for
that entry will no longer match the hash that was stored -- and every
entry that comes after it will also fail to match, because each entry
depends on the previous entry's hash. This lets us DETECT tampering.

This program is intentionally kept simple (only standard Python
libraries) so it is easy to read, run, and explain in a college
viva / demonstration.
=====================================================================
"""

import hashlib      # used to calculate SHA-256 hashes
import json         # used to read/write the log file and to create a
                     # consistent (deterministic) string before hashing
import os           # used to create folders and check if files exist
import shutil       # used to copy files (for backup/restore)
from datetime import datetime  # used to generate timestamps


# ---------------------------------------------------------------
# CONSTANTS -- file and folder locations used throughout the program
# ---------------------------------------------------------------
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "audit_log.json")

EVIDENCE_DIR = "evidence"
BACKUP_FILE = os.path.join(EVIDENCE_DIR, "audit_log_backup.json")

OUTPUT_DIR = "output"
REPORT_FILE = os.path.join(OUTPUT_DIR, "forensic_report.txt")


# ---------------------------------------------------------------
# ensure_directories()
# Makes sure logs/, evidence/, and output/ folders exist.
# This runs every time the program starts, so the project works
# even if these folders were deleted.
# ---------------------------------------------------------------
def ensure_directories():
    for folder in (LOG_DIR, EVIDENCE_DIR, OUTPUT_DIR):
        if not os.path.exists(folder):
            os.makedirs(folder)


# ---------------------------------------------------------------
# calculate_hash(entry)
#
# This is the heart of the whole project.
#
# It takes a log entry (a dictionary) and calculates its SHA-256
# hash using ONLY these five fields, in a fixed, predictable order:
#   id, timestamp, event, user, previous_hash
#
# IMPORTANT: We do NOT include the entry's own "hash" field when
# calculating the hash -- that would be circular. The hash is a
# fingerprint of everything EXCEPT itself.
#
# We use json.dumps(..., sort_keys=True) to turn the dictionary into
# a text string in a completely predictable (deterministic) way.
# The same input will always produce the same JSON string, and
# therefore always the same SHA-256 hash.
# ---------------------------------------------------------------
def calculate_hash(entry):
    data_for_hashing = {
        "id": entry["id"],
        "timestamp": entry["timestamp"],
        "event": entry["event"],
        "user": entry["user"],
        "previous_hash": entry["previous_hash"],
    }
    # sort_keys=True guarantees the same field order every time
    data_string = json.dumps(data_for_hashing, sort_keys=True)

    # Encode the string to bytes, then hash it with SHA-256
    return hashlib.sha256(data_string.encode()).hexdigest()


# ---------------------------------------------------------------
# create_genesis_entry()
#
# The very first entry in any hash chain is called the "Genesis
# Entry". It has no previous entry, so we use the special value
# "GENESIS" instead of a real hash. This clearly marks the start
# of the chain.
# ---------------------------------------------------------------
def create_genesis_entry():
    entry = {
        "id": 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": "Genesis Entry - Start of Audit Log",
        "user": "SYSTEM",
        "previous_hash": "GENESIS",
    }
    entry["hash"] = calculate_hash(entry)
    return entry


# ---------------------------------------------------------------
# create_log_entry(entry_id, event, user, previous_hash)
#
# Builds a normal (non-genesis) log entry and calculates its hash.
# ---------------------------------------------------------------
def create_log_entry(entry_id, event, user, previous_hash):
    entry = {
        "id": entry_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "user": user,
        "previous_hash": previous_hash,
    }
    entry["hash"] = calculate_hash(entry)
    return entry


# ---------------------------------------------------------------
# load_logs(path=LOG_FILE)
#
# Reads the audit log JSON file and returns it as a Python list.
# Handles the case where the file doesn't exist yet, or is empty,
# or contains corrupted/invalid JSON -- instead of crashing, it
# tells the user clearly what went wrong.
# ---------------------------------------------------------------
def load_logs(path=LOG_FILE):
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if content == "":
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        print("\n[ERROR] The log file appears to be corrupted or is not valid JSON.")
        return None


# ---------------------------------------------------------------
# save_logs(logs, path=LOG_FILE)
#
# Writes the list of log entries back to the JSON file, nicely
# formatted (indent=4) so it is human-readable if opened directly.
# ---------------------------------------------------------------
def save_logs(logs, path=LOG_FILE):
    with open(path, "w") as f:
        json.dump(logs, f, indent=4)


# ---------------------------------------------------------------
# OPTION 1: create_new_audit_log()
#
# Creates (or resets) the audit log with a fresh Genesis entry.
# Asks for confirmation before overwriting an existing log so we
# never silently destroy audit data.
# ---------------------------------------------------------------
def create_new_audit_log():
    ensure_directories()

    if os.path.exists(LOG_FILE):
        existing = load_logs()
        if existing:  # file exists and has entries
            print("\n[WARNING] An audit log already exists with "
                  f"{len(existing)} entr{'y' if len(existing) == 1 else 'ies'}.")
            confirm = input("Type YES to reset it (this cannot be undone), "
                             "or anything else to cancel: ").strip()
            if confirm != "YES":
                print("Cancelled. Existing audit log was NOT changed.")
                return

    genesis = create_genesis_entry()
    logs = [genesis]
    save_logs(logs)

    print("\n=============================================")
    print(" NEW AUDIT LOG CREATED")
    print("=============================================")
    print(f"Genesis Entry Hash: {genesis['hash']}")
    print(f"Saved to: {LOG_FILE}")


# ---------------------------------------------------------------
# OPTION 2: add_log_entry()
#
# Asks the user for an event and username, then creates a new
# entry linked to the previous entry's hash, and saves it.
# ---------------------------------------------------------------
def add_log_entry():
    ensure_directories()
    logs = load_logs()

    if logs is None:
        print("Cannot add entry -- the log file is corrupted. "
              "Consider creating a new audit log (Option 1).")
        return

    if len(logs) == 0:
        print("\nNo audit log found yet. Please choose Option 1 "
              "(Create New Audit Log) first.")
        return

    user = input("Enter username: ").strip()
    event = input("Enter event: ").strip()

    if user == "" or event == "":
        print("Username and event cannot be empty. Entry not added.")
        return

    last_entry = logs[-1]
    new_entry = create_log_entry(
        entry_id=last_entry["id"] + 1,
        event=event,
        user=user,
        previous_hash=last_entry["hash"],
    )

    logs.append(new_entry)
    save_logs(logs)

    print("\n=============================================")
    print("AUDIT ENTRY CREATED")
    print("=============================================")
    print(f"Entry ID: {new_entry['id']}")
    print(f"User: {new_entry['user']}")
    print(f"Event: {new_entry['event']}")
    print(f"Previous Hash: {new_entry['previous_hash']}")
    print(f"Current Hash: {new_entry['hash']}")
    print("\nLog entry successfully added.")


# ---------------------------------------------------------------
# OPTION 3: display_logs()
#
# Prints every log entry in a clean, readable format.
# ---------------------------------------------------------------
def display_logs():
    logs = load_logs()

    if logs is None:
        print("Cannot display logs -- the log file is corrupted.")
        return

    if len(logs) == 0:
        print("\nNo audit log entries found. "
              "Use Option 1 to create a new audit log.")
        return

    print("\n=============================================")
    print("AUDIT LOG")
    print("=============================================")
    for i, entry in enumerate(logs):
        print(f"\nEntry ID: {entry['id']}")
        print(f"Timestamp: {entry['timestamp']}")
        print(f"User: {entry['user']}")
        print(f"Event: {entry['event']}")
        print(f"Previous Hash: {entry['previous_hash']}")
        print(f"Hash: {entry['hash']}")
        if i != len(logs) - 1:
            print("---------------------------------------------")


# ---------------------------------------------------------------
# OPTION 4: verify_hash_chain(logs=None, quiet=False)
#
# THE MOST IMPORTANT FUNCTION IN THIS PROJECT.
#
# For every entry:
#   1. Recalculate its SHA-256 hash from its own fields.
#   2. Compare the recalculated hash to the hash stored in the file.
#   3. Check that its "previous_hash" matches the actual hash of the
#      entry before it in the chain.
#
# If either check fails for an entry, that entry is marked INVALID.
#
# Returns a tuple: (overall_valid: bool, results: list of (id, bool))
# so this function can be reused by both the menu option and the
# forensic report / tampering demo, without duplicating logic.
# ---------------------------------------------------------------
def verify_hash_chain(logs=None, quiet=False):
    if logs is None:
        logs = load_logs()

    if logs is None:
        if not quiet:
            print("Cannot verify -- the log file is corrupted.")
        return False, []

    if len(logs) == 0:
        if not quiet:
            print("\nNo audit log entries to verify. "
                  "Use Option 1 to create a new audit log.")
        return False, []

    results = []
    overall_valid = True

    for i, entry in enumerate(logs):
        recalculated_hash = calculate_hash(entry)
        hash_matches = (recalculated_hash == entry["hash"])

        if i == 0:
            # The first entry should be the Genesis entry
            previous_ok = (entry["previous_hash"] == "GENESIS")
        else:
            previous_ok = (entry["previous_hash"] == logs[i - 1]["hash"])

        entry_valid = hash_matches and previous_ok
        results.append((entry["id"], entry_valid))

        if not entry_valid:
            overall_valid = False

    if not quiet:
        print("\n=============================================")
        print("HASH CHAIN VERIFICATION")
        print("=============================================")
        for entry_id, is_valid in results:
            status = "VALID" if is_valid else "INVALID"
            print(f"Entry {entry_id}: {status}")

        print("\n---------------------------------------------")
        if overall_valid:
            print("RESULT: HASH CHAIN VALID")
            print("No tampering detected.")
        else:
            print("RESULT: TAMPERING DETECTED")
            print("The audit log has been modified.")
        print("---------------------------------------------")

    return overall_valid, results


# ---------------------------------------------------------------
# OPTION 5: demonstrate_tampering()
#
# A safe, automatic, and REVERSIBLE demonstration of tamper
# detection:
#   1. Back up the current log to evidence/audit_log_backup.json
#   2. Make sure there are at least 3 entries (create sample ones
#      if needed).
#   3. Verify the chain is currently valid.
#   4. Secretly modify one old entry's "event" text.
#   5. Save the modified log and verify again.
#   6. Show that tampering is now detected.
#   7. Offer to restore the original log from the backup.
# ---------------------------------------------------------------
def demonstrate_tampering():
    ensure_directories()
    logs = load_logs()

    if logs is None:
        print("Cannot run demonstration -- the log file is corrupted.")
        return

    # Step 0: make sure we have a log to work with, creating sample
    # entries automatically if necessary.
    if len(logs) == 0:
        print("No audit log found. Creating one automatically for the demo...")
        logs = [create_genesis_entry()]

    while len(logs) < 3:
        last_entry = logs[-1]
        sample_events = [
            ("admin", "User logged into the system"),
            ("admin", "File accessed: report.docx"),
            ("admin", "User logged out"),
        ]
        user, event = sample_events[len(logs) - 1 % len(sample_events)]
        new_entry = create_log_entry(
            entry_id=last_entry["id"] + 1,
            event=event,
            user=user,
            previous_hash=last_entry["hash"],
        )
        logs.append(new_entry)

    save_logs(logs)

    # Step 1: back up the current (clean) log before touching it
    shutil.copyfile(LOG_FILE, BACKUP_FILE)

    print("\n=============================================")
    print("TAMPERING DEMONSTRATION")
    print("=============================================")

    print("\nStep 1: Checking original log...")
    is_valid, _ = verify_hash_chain(logs, quiet=True)
    print(f"Result: {'HASH CHAIN VALID' if is_valid else 'HASH CHAIN INVALID (unexpected!)'}")

    # Step 2: pick an entry to tamper with (not the genesis entry,
    # so the demo mirrors a realistic scenario: an attacker editing
    # a normal event).
    tamper_index = 1 if len(logs) > 1 else 0
    original_event = logs[tamper_index]["event"]
    fake_event = "Unauthorized login detected"

    print("\nStep 2: Simulating an attacker modifying an old event...")
    print(f"\nOriginal event:\n{original_event}")
    print(f"\nModified event:\n{fake_event}")

    # NOTE: We change the event text but deliberately do NOT
    # recalculate the hash -- this is exactly what a real attacker
    # would do: edit the visible data but have no way to produce a
    # matching valid hash without detection.
    tampered_logs = json.loads(json.dumps(logs))  # simple deep copy
    tampered_logs[tamper_index]["event"] = fake_event
    save_logs(tampered_logs)

    print("\nStep 3: Checking the modified log...")
    is_valid_after, _ = verify_hash_chain(load_logs(), quiet=False)

    if not is_valid_after:
        print("\nThe hash chain has been broken by the modification above.")
    else:
        print("\nUnexpected: tampering was not detected. Please check the code.")

    # Step 3: offer to restore the clean version from backup
    print("\n---------------------------------------------")
    restore = input("Restore the original, untampered audit log now? (yes/no): ").strip().lower()
    if restore == "yes":
        shutil.copyfile(BACKUP_FILE, LOG_FILE)
        print("Original audit log restored successfully.")
    else:
        print("Audit log left in the TAMPERED state for further inspection.")
        print(f"A clean backup is still safely stored at: {BACKUP_FILE}")


# ---------------------------------------------------------------
# OPTION 6: export_forensic_report()
#
# Writes a simple, human-readable text report summarizing the
# state of the audit log to output/forensic_report.txt
# ---------------------------------------------------------------
def export_forensic_report():
    ensure_directories()
    logs = load_logs()

    if logs is None:
        print("Cannot export report -- the log file is corrupted.")
        return

    if len(logs) == 0:
        print("\nNo audit log entries found. "
              "Use Option 1 to create a new audit log first.")
        return

    is_valid, results = verify_hash_chain(logs, quiet=True)
    invalid_entries = [entry_id for entry_id, valid in results if not valid]

    report_lines = []
    report_lines.append("=============================================")
    report_lines.append("FORENSIC AUDIT REPORT")
    report_lines.append("=============================================")
    report_lines.append("")
    report_lines.append("Hash Algorithm: SHA-256")
    report_lines.append("")
    report_lines.append(f"Total Entries: {len(logs)}")
    report_lines.append("")
    report_lines.append("Verification Status:")
    report_lines.append("VALID" if is_valid else "INVALID")
    report_lines.append("")
    report_lines.append("Tampering Detected:")
    report_lines.append("NO" if is_valid else "YES")
    report_lines.append("")

    if invalid_entries:
        report_lines.append("Invalid Entry IDs:")
        report_lines.append(", ".join(str(e) for e in invalid_entries))
        report_lines.append("")

    report_lines.append("Generated:")
    report_lines.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report_lines.append("=============================================")

    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(report_lines))

    print("\n=============================================")
    print("FORENSIC REPORT EXPORTED")
    print("=============================================")
    print(f"Saved to: {REPORT_FILE}")
    print(f"Verification Status: {'VALID' if is_valid else 'INVALID'}")


# ---------------------------------------------------------------
# main()
#
# Displays the menu in a loop and calls the correct function based
# on the user's choice.
# ---------------------------------------------------------------
def main():
    ensure_directories()

    while True:
        print("\n=============================================")
        print(" CRYPTOGRAPHIC HASH-CHAINED AUDIT LOGGING")
        print("=============================================")
        print("1. Create New Audit Log")
        print("2. Add Audit Log Entry")
        print("3. View Audit Logs")
        print("4. Verify Hash Chain")
        print("5. Demonstrate Tampering")
        print("6. Export Forensic Report")
        print("7. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            create_new_audit_log()
        elif choice == "2":
            add_log_entry()
        elif choice == "3":
            display_logs()
        elif choice == "4":
            verify_hash_chain()
        elif choice == "5":
            demonstrate_tampering()
        elif choice == "6":
            export_forensic_report()
        elif choice == "7":
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
