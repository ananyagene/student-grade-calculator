import hashlib
import hmac
import secrets


PBKDF2_ITERATIONS = 200_000


def hash_password(password):
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return salt, password_hash, PBKDF2_ITERATIONS


def verify_password(password, salt, password_hash, iterations):
    if not isinstance(password, str):
        return False
    calculated_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        int(iterations),
    )
    return hmac.compare_digest(calculated_hash, password_hash)


class AuthenticationManager:
    def __init__(self, database):
        self.database = database

    def account_count(self):
        return self.database.account_count()

    def create_admin(self, username, password):
        if not isinstance(username, str) or username.strip() == "":
            return False
        salt, password_hash, iterations = hash_password(password)
        return self.database.create_account(
            username=username,
            password_salt=salt,
            password_hash=password_hash,
            iterations=iterations,
            role="ADMIN",
            student_id=None,
        )

    def provision_student(self, username, password, roll_number,
                          semester, academic_year):
        if not isinstance(username, str) or username.strip() == "":
            return False
        salt, password_hash, iterations = hash_password(password)
        return self.database.provision_student_account(
            username=username,
            password_salt=salt,
            password_hash=password_hash,
            iterations=iterations,
            roll_number=roll_number,
            semester=semester,
            academic_year=academic_year,
        )

    def authenticate(self, username, password, expected_role):
        if not isinstance(username, str) or not isinstance(password, str):
            return None
        account = self.database.get_account_by_username(username)
        if not account:
            return None
        if account["role"] != expected_role:
            return None
        if not verify_password(
            password,
            account["password_salt"],
            account["password_hash"],
            account["iterations"],
        ):
            return None
        return {
            "account_id": account["account_id"],
            "username": account["username"],
            "role": account["role"],
            "student_id": account["student_id"],
        }

    def is_admin(self, account):
        return bool(account and account["role"] == "ADMIN")

    def is_student(self, account):
        return bool(account and account["role"] == "STUDENT")

    def can_manage_results(self, account):
        return self.is_admin(account)

    def clear_authenticated_session(self, session_state):
        session_state.pop("authenticated_account", None)
        session_state.pop("auth_role", None)
