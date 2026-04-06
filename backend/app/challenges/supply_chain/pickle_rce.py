"""
Challenge: Pickle RCE
Upload a malicious pickle file that executes code on deserialization.
"""

from app.flags import get_flag

import pickle
import base64
import io
import os

FLAG = get_flag("sc-pickle")

# Write flag to a file the exploit should read
FLAG_PATH = "/tmp/dvai_pickle_flag.txt"
os.makedirs(os.path.dirname(FLAG_PATH), exist_ok=True)
with open(FLAG_PATH, "w") as f:
    f.write(FLAG)


async def handle(user_input: str, difficulty: int = 1) -> dict:
    cmd = user_input.strip()

    if cmd.lower() == "help":
        return {
            "response": (
                "Model Loading Service v1.0\n"
                "─────────────────────────\n"
                "Upload a base64-encoded pickle file to load a model.\n\n"
                "Commands:\n"
                "  load <base64_pickle>  - Load a serialized model\n"
                "  help                  - Show this message\n\n"
                f"Difficulty {difficulty}:\n"
                + ("  No restrictions on pickle loading.\n" if difficulty == 1 else "")
                + ("  Basic class name filtering applied.\n" if difficulty == 2 else "")
                + ("  Restricted unpickler with allowlist.\n" if difficulty == 3 else "")
            ),
            "flag_found": False,
        }

    if not cmd.lower().startswith("load "):
        return {"response": "Unknown command. Type 'help' for usage.", "flag_found": False}

    b64_data = cmd[5:].strip()
    try:
        raw = base64.b64decode(b64_data)
    except Exception:
        return {"response": "Error: Invalid base64 encoding.", "flag_found": False}

    output = ""
    flag_found = False

    try:
        if difficulty == 1:
            # No restrictions - direct pickle.loads
            obj = pickle.loads(raw)
            output = f"Model loaded successfully: {repr(obj)}"
        elif difficulty == 2:
            # Basic filter: block 'os' and 'subprocess' in the raw bytes
            raw_str = raw.decode("latin-1")
            if "os" in raw_str.lower() and "system" in raw_str.lower():
                return {"response": "Blocked: detected os.system in pickle stream.", "flag_found": False}
            obj = pickle.loads(raw)
            output = f"Model loaded: {repr(obj)}"
        else:
            # Restricted unpickler
            class RestrictedUnpickler(pickle.Unpickler):
                ALLOWED = {"builtins.dict", "builtins.list", "builtins.tuple", "builtins.set"}
                def find_class(self, module, name):
                    full = f"{module}.{name}"
                    if full in self.ALLOWED:
                        return super().find_class(module, name)
                    raise pickle.UnpicklingError(f"Blocked: {full}")
            obj = RestrictedUnpickler(io.BytesIO(raw)).load()
            output = f"Model loaded: {repr(obj)}"

        # Check if the exploit read the flag file
        if os.path.exists("/tmp/dvai_pickle_output.txt"):
            exploit_output = open("/tmp/dvai_pickle_output.txt").read()
            output += f"\n\nExploit output:\n{exploit_output}"
            if FLAG in exploit_output:
                flag_found = True
            os.remove("/tmp/dvai_pickle_output.txt")

    except Exception as e:
        output = f"Error during deserialization: {e}"

    return {"response": output, "flag_found": flag_found, "flag": FLAG if flag_found else None}
