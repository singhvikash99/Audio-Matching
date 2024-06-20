import hashlib
from audiomatch.fingerprints import calc


class FingerprintHandler:

    def fingerprint_exists(self, cursor, hashed_fingerprint):
        cursor.execute(
            "SELECT COUNT(*) FROM fingerprints WHERE hashed_fingerprint = ?",
            (hashed_fingerprint,),
        )
        count = cursor.fetchone()[0]
        return count > 0

    def generate_fingerprint(self, file_path):
        fingerprint = calc(file_path)
        return fingerprint
