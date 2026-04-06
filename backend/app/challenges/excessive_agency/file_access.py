"""
Challenge: Unrestricted File Access
Exploit the AI's file access to escape the sandbox.
"""

from app.flags import get_flag

import os

FLAG = get_flag("ea-file-access")

# Set up files
os.makedirs("/tmp/dvai_sandbox/allowed", exist_ok=True)
os.makedirs("/tmp/dvai_sandbox/secret", exist_ok=True)
with open("/tmp/dvai_sandbox/allowed/readme.txt", "w") as f:
    f.write("Welcome to the sandbox. You can read files here.")
with open("/tmp/dvai_sandbox/secret/flag.txt", "w") as f:
    f.write(FLAG)
with open("/tmp/dvai_sandbox/allowed/notes.txt", "w") as f:
    f.write("These are some notes. Nothing secret here.")


def read_file(path: str, difficulty: int) -> str:
    if difficulty == 1:
        # No restrictions
        try:
            return open(path).read()
        except Exception as e:
            return f"Error: {e}"
    elif difficulty == 2:
        # String-based path check (bypassable with traversal)
        if not path.startswith("/tmp/dvai_sandbox/allowed"):
            return "Access denied: path must start with /tmp/dvai_sandbox/allowed"
        try:
            return open(path).read()
        except Exception as e:
            return f"Error: {e}"
    else:
        # Resolved path check
        resolved = os.path.realpath(path)
        if not resolved.startswith("/tmp/dvai_sandbox/allowed"):
            return f"Access denied: resolved path {resolved} is outside sandbox"
        try:
            return open(resolved).read()
        except Exception as e:
            return f"Error: {e}"


def write_file(path: str, content: str, difficulty: int) -> str:
    if difficulty >= 2:
        return "Write access disabled at this difficulty level."
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Written to {path}"
    except Exception as e:
        return f"Error: {e}"


def list_dir(path: str, difficulty: int) -> str:
    if difficulty >= 3:
        resolved = os.path.realpath(path)
        if not resolved.startswith("/tmp/dvai_sandbox/allowed"):
            return "Access denied"
    try:
        entries = os.listdir(path)
        return "\n".join(entries)
    except Exception as e:
        return f"Error: {e}"


async def handle(user_input: str, difficulty: int = 1) -> dict:
    cmd = user_input.strip()

    if cmd.lower().startswith("read "):
        path = cmd[5:].strip()
        result = read_file(path, difficulty)
        flag_found = FLAG in result
        return {"response": result, "flag_found": flag_found, "flag": FLAG if flag_found else None}

    elif cmd.lower().startswith("write "):
        parts = cmd[6:].strip().split(" ", 1)
        if len(parts) < 2:
            return {"response": "Usage: write <path> <content>", "flag_found": False}
        result = write_file(parts[0], parts[1], difficulty)
        return {"response": result, "flag_found": False}

    elif cmd.lower().startswith("ls "):
        path = cmd[3:].strip()
        result = list_dir(path, difficulty)
        return {"response": result, "flag_found": False}

    else:
        return {
            "response": (
                "File System Sandbox\n"
                "────────────────────\n"
                "You have access to a sandboxed file system.\n"
                "Allowed directory: /tmp/dvai_sandbox/allowed/\n"
                "Flag is somewhere outside the sandbox.\n\n"
                "Commands:\n"
                "  read <path>           - Read a file\n"
                "  write <path> <data>   - Write to a file\n"
                "  ls <path>             - List directory\n"
            ),
            "flag_found": False,
        }
