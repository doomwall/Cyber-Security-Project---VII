"""Password hashers.

###################################################################
# FLAW 2 -- Cryptographic Failures
#
# The hasher below stores passwords as a single round of unsalted MD5.
# MD5 is a deprecated hash function designed to be FAST, which is the
# opposite of what password storage needs, and without a salt two users
# with the same password get byte-identical hashes -- so a leaked
# database can be cracked with a public rainbow table in seconds.
#
# Django 5 no longer ships an unsalted MD5 hasher (it was removed in
# 5.1 precisely because it is unsafe), so it is implemented here by
# hand to demonstrate the flaw.
#
# To repair the app: switch PASSWORD_HASHERS in settings.py to the
# SECURE version, then restart with the run script so the existing
# users are re-hashed with the strong algorithm.
###################################################################
"""

import hashlib

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
from django.utils.translation import gettext_noop as _


class UnsaltedMD5PasswordHasher(BasePasswordHasher):
    """Insecure on purpose: one round of MD5, no salt, no key stretching."""

    algorithm = 'unsalted_md5'

    def salt(self):
        # No salt whatsoever. This is the part that makes rainbow tables work.
        return ''

    def encode(self, password, salt=''):
        digest = hashlib.md5(password.encode()).hexdigest()
        return '%s$%s' % (self.algorithm, digest)

    def decode(self, encoded):
        algorithm, digest = encoded.split('$', 1)
        assert algorithm == self.algorithm
        return {
            'algorithm': algorithm,
            'hash': digest,
            'salt': '',
        }

    def verify(self, password, encoded):
        return constant_time_compare(encoded, self.encode(password))

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            _('algorithm'): decoded['algorithm'],
            _('salt'): '(none)',
            _('hash'): mask_hash(decoded['hash'], show=6),
        }

    def harden_runtime(self, password, encoded):
        # Nothing to harden: there is no work factor to adjust.
        pass
