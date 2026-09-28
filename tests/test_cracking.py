"""Test crack paths against known hashes with a small wordlist."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from hashbreak import HashBreakModern, ntlm_hash, mysql_native_password


@pytest.fixture
def hb():
    h = HashBreakModern()
    # force small inline wordlist so tests are fast and deterministic
    h.words_cache = ["password", "123456", "qwerty", "admin", "letmein"]
    return h


def test_md5_password(hb):
    # MD5("password")
    result = hb.crack_classic("5f4dcc3b5aa765d61d8327deb882cf99")
    assert result == "password"


def test_md5_123456(hb):
    # MD5("123456")
    result = hb.crack_classic("e10adc3949ba59abbe56e057f20f883e")
    assert result == "123456"


def test_ntlm_hash_password():
    # NTLM("password") = MD4(UTF-16LE("password"))
    h = ntlm_hash("password")
    assert h == "8846f7eaee8fb117ad06bdd830b7586c"


def test_mysql_native_password():
    h = mysql_native_password("password")
    assert h == "*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19"


def test_mask_parse():
    from hashbreak import parse_mask, mask_size
    classes = parse_mask("?d?d?d?d")
    assert mask_size(classes) == 10000


def test_mask_upper_lower():
    from hashbreak import parse_mask, mask_size
    classes = parse_mask("?u?l")
    assert mask_size(classes) == 26 * 26


def test_mask_literal():
    from hashbreak import parse_mask
    classes = parse_mask("abc")
    assert len(classes) == 3


def test_hybrid_mask_word():
    from hashbreak import parse_mask, mask_size
    classes = parse_mask("?d?d")
    assert mask_size(classes) == 100
