from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet
import base64, secrets, random, string

def getting_equal_length(num):
    # Divide the number by 4 using integer division
    quotient = num // 4
    remainder = num % 4
    # Create a list with the quotient repeated 4 times
    result = [quotient] * 4
    # Distribute the remainder among the first few elements
    for i in range(remainder):
        result[i] += 1
    return result

def generate_secure_password(length=12):
    distribution = getting_equal_length(length)

    password = []

    password += [secrets.choice(string.ascii_lowercase) for _ in range(distribution[0])]
    password += [secrets.choice(string.ascii_uppercase) for _ in range(distribution[1])]
    password += [secrets.choice(string.digits) for _ in range(distribution[2])]
    password += [secrets.choice(string.punctuation) for _ in range(distribution[3])]


    # Shuffling the password
    random.shuffle(password)

    return ''.join(password)

def derive_key(password: str, salt: bytes):
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

def encrypt(key, text):
    return Fernet(key).encrypt(text.encode())

def decrypt(key, data):
    return Fernet(key).decrypt(data).decode()