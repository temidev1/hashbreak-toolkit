"""Test hash type detection across all supported formats."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from hashbreak import HashBreakModern


@pytest.fixture
def hb():
    return HashBreakModern()


def test_md5_32_hex(hb):
    assert hb.detect_hash_type("5f4dcc3b5aa765d61d8327deb882cf99") == "MD5"


def test_sha1_40_hex(hb):
    assert hb.detect_hash_type("aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d") == "SHA1"


def test_sha224_56_hex(hb):
    h = "a" * 56
    assert hb.detect_hash_type(h) == "SHA224"


def test_sha256_64_hex(hb):
    h = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert hb.detect_hash_type(h) == "SHA256"


def test_sha384_96_hex(hb):
    h = "a" * 96
    assert hb.detect_hash_type(h) == "SHA384"


def test_sha512_128_hex(hb):
    h = "a" * 128
    assert hb.detect_hash_type(h) == "SHA512"


def test_mysql41_prefix(hb):
    h = "*" + "A" * 40
    assert hb.detect_hash_type(h) == "mysql41"


def test_bcrypt_prefix(hb):
    h = "$2b$10$" + "a" * 53
    assert hb.detect_hash_type(h) == "bcrypt"


def test_scrypt_prefix(hb):
    h = "$7$" + "a" * 50
    assert hb.detect_hash_type(h) == "scrypt"


def test_pbkdf2_prefix(hb):
    h = "$pbkdf2-sha256$29000$" + "a" * 20
    assert hb.detect_hash_type(h) == "pbkdf2"


def test_wpa_pmkid_prefix(hb):
    h = "WPA*01*" + "a" * 200
    assert hb.detect_hash_type(h) == "wpa-pmkid"


def test_wpa_handshake_prefix(hb):
    h = "WPA*02*" + "a" * 200
    assert hb.detect_hash_type(h) == "wpa-hs"


def test_unknown_short_string(hb):
    assert hb.detect_hash_type("hello") is None


def test_unknown_random_hex(hb):
    assert hb.detect_hash_type("abcdef") is None


def test_empty_string(hb):
    assert hb.detect_hash_type("") is None
