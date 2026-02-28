import json
import time
from rmap.identity_manager import IdentityManager
from rmap.rmap import RMAP

# Initialize (same setup as usage_example.py)
im = IdentityManager(
    client_keys_dir="testassets/clients",
    server_public_key_path="testassets/server_pub.asc",
    server_private_key_path="testassets/server_priv.asc",
)
rmap = RMAP(im)

# Message 1: establish a pending session state on the server
msg1_plain = {"nonceClient": 12345678, "identity": "Jean"}
msg1 = {"payload": im.encrypt_for_server(msg1_plain)}
resp1 = rmap.handle_message1(msg1)

# Extract the freshly issued server nonce from server-side state (testing convenience)
nonce_client, nonce_server = rmap.nonces["Jean"]
msg2_plain = {"nonceServer": nonce_server}
msg2 = {"payload": im.encrypt_for_server(msg2_plain)}

# First submission of Message 2
r1 = rmap.handle_message2(msg2)
print("first:", json.dumps(r1, indent=2))

# Simulate a delayed, cross-request replay (no new Message 1)
print("\n--- waiting 5 seconds before replay ---\n")
time.sleep(5)

# Replay the exact same Message 2 payload
r2 = rmap.handle_message2(msg2)
print("replay:", json.dumps(r2, indent=2))

print("replay_same_response:", r1 == r2)
