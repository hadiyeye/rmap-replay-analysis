from rmap.identity_manager import IdentityManager
from rmap.rmap import RMAP


def setup_rmap():
    im = IdentityManager(
        client_keys_dir="testassets/clients",
        server_public_key_path="testassets/server_pub.asc",
        server_private_key_path="testassets/server_priv.asc",
    )
    return im, RMAP(im)


def _make_msg1(im, identity: str, nonce_client: int):
    return {"payload": im.encrypt_for_server({"nonceClient": nonce_client, "identity": identity})}


def _make_msg2(im, nonce_server: int):
    return {"payload": im.encrypt_for_server({"nonceServer": nonce_server})}


def test_session_collision_overwrites_state_for_same_identity():
    """
    Vulnerability demo / design limitation test:
    The server stores pending session state as self.nonces[identity].
    A second Message1 using the same identity overwrites the previous nonceServer,
    causing the old Message2 (bound to the first nonceServer) to be rejected.
    """
    im, rmap = setup_rmap()
    identity = "Jean"

    # First handshake start (session1)
    rmap.handle_message1(_make_msg1(im, identity, nonce_client=1111))
    _, ns1 = rmap.nonces[identity]
    msg2_session1 = _make_msg2(im, ns1)

    # Second handshake start with SAME identity (session2 overwrites session1)
    rmap.handle_message1(_make_msg1(im, identity, nonce_client=2222))
    _, ns2 = rmap.nonces[identity]
    assert ns2 != ns1, "Expected a new nonceServer for the second session"

    # Now try to complete session1 using old nonceServer -> should FAIL due to overwrite
    r_old = rmap.handle_message2(msg2_session1)
    assert "error" in r_old, f
'''
message1 -> ns1
message1 -> ns2
message2(ns1)
'''
