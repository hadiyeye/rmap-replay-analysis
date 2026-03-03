import time
from rmap.identity_manager import IdentityManager
from rmap.rmap import RMAP


def setup_rmap():
    im = IdentityManager(
        client_keys_dir="testassets/clients",
        server_public_key_path="testassets/server_pub.asc",
        server_private_key_path="testassets/server_priv.asc",
    )
    return im, RMAP(im)


def create_message2(im, rmap):
    msg1 = {"payload": im.encrypt_for_server({
        "nonceClient": 12345678,
        "identity": "Jean"
    })}
    rmap.handle_message1(msg1)

    _, nonce_server = rmap.nonces["Jean"]

    return {"payload": im.encrypt_for_server({
        "nonceServer": nonce_server
    })}


# Test 1: immediate replay
def test_pure_replay_same_session():
    im, rmap = setup_rmap()
    msg2 = create_message2(im, rmap)

    r1 = rmap.handle_message2(msg2)
    r2 = rmap.handle_message2(msg2)

    assert "result" in r1
    assert "error" in r2


# Test 2: delayed replay
def test_cross_request_replay():
    im, rmap = setup_rmap()
    msg2 = create_message2(im, rmap)

    r1 = rmap.handle_message2(msg2)
    time.sleep(2)
    r2 = rmap.handle_message2(msg2)

    assert "result" in r1
    assert "error" in r2
