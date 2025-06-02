from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature

def generate_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_private_key(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

def load_private_key(filepath):
    with open(filepath, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def deserialize_public_key(pem_str):
    return serialization.load_pem_public_key(pem_str.encode())
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

def sign_message(private_key, message: bytes) -> bytes:
    
    signature = private_key.sign(
        message,
        signature_algorithm=ec.ECDSA(hashes.SHA256())
    )
    return signature

def load_private_key_from_file(file_path):
    with open(file_path, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)

def verify_signature(public_key, message_bytes, signature):
    try:
        public_key.verify(signature, message_bytes, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
