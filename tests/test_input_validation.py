"""Test target validators — malicious/invalid input must be rejected."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from hashbreak import validate_domain, validate_target, is_private_ip


# --- domain validation ---

def test_valid_domain():
    ok, norm, err = validate_domain("example.com")
    assert ok and norm == "example.com" and err == ""


def test_domain_strips_scheme():
    ok, norm, _ = validate_domain("https://example.com/path")
    assert ok and norm == "example.com"


def test_domain_lowercase():
    ok, norm, _ = validate_domain("EXAMPLE.COM")
    assert ok and norm == "example.com"


def test_domain_empty_rejected():
    ok, _, err = validate_domain("")
    assert not ok and "empty" in err


def test_domain_no_dot_rejected():
    ok, _, _ = validate_domain("localhost")
    assert not ok


def test_domain_shell_injection_rejected():
    # semicolon, backticks, pipe — should all fail
    for bad in ["example.com; rm -rf /", "example.com|cat /etc/passwd",
                "example.com`whoami`", "example.com$(id)"]:
        ok, _, _ = validate_domain(bad)
        assert not ok, f"should reject: {bad}"


def test_domain_spaces_rejected():
    ok, _, _ = validate_domain("example .com")
    assert not ok


def test_domain_too_long_rejected():
    ok, _, err = validate_domain("a" * 300 + ".com")
    assert not ok and "long" in err


# --- IP classification ---

def test_private_ip_192_168():
    assert is_private_ip("192.168.1.1")


def test_private_ip_10():
    assert is_private_ip("10.0.0.1")


def test_private_ip_172():
    assert is_private_ip("172.16.0.1")


def test_private_ip_loopback():
    assert is_private_ip("127.0.0.1")


def test_public_ip_8_8_8_8():
    assert not is_private_ip("8.8.8.8")


def test_public_ip_1_1_1_1():
    assert not is_private_ip("1.1.1.1")


# --- target validation ---

def test_target_single_host():
    ok, targets, _ = validate_target("example.com")
    assert ok and targets == ["example.com"]


def test_target_empty_rejected():
    ok, _, err = validate_target("")
    assert not ok and "empty" in err


def test_target_cidr_24():
    ok, targets, _ = validate_target("192.168.1.0/24")
    assert ok and len(targets) > 200


def test_target_cidr_large_capped_not_rejected():
    """large CIDR blocks are accepted but capped to 4096 hosts (not rejected)"""
    ok, targets, _ = validate_target("10.0.0.0/8")
    assert ok
    assert len(targets) == 4096   # capped, not 16 million


def test_target_comma_list():
    ok, targets, _ = validate_target("a.com,b.com,c.com")
    assert ok and len(targets) == 3
