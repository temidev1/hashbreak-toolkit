"""Test that online lookup is gated by consent + HASHBREAK_OFFLINE."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import hashbreak


def test_offline_env_var_blocks_lookup(monkeypatch):
    monkeypatch.setenv("HASHBREAK_OFFLINE", "1")
    # reset cached consent
    hashbreak._CONFIRMED_ONLINE[0] = False
    result = hashbreak.confirm_online_lookup("5f4dcc3b5aa765d61d8327deb882cf99")
    assert result is False


def test_consent_prompt_defaults_to_no(monkeypatch):
    monkeypatch.delenv("HASHBREAK_OFFLINE", raising=False)
    hashbreak._CONFIRMED_ONLINE[0] = False
    # simulate empty input (just Enter) = default no
    monkeypatch.setattr("builtins.input", lambda _: "")
    result = hashbreak.confirm_online_lookup("5f4dcc3b5aa765d61d8327deb882cf99")
    assert result is False


def test_consent_prompt_yes(monkeypatch):
    monkeypatch.delenv("HASHBREAK_OFFLINE", raising=False)
    hashbreak._CONFIRMED_ONLINE[0] = False
    monkeypatch.setattr("builtins.input", lambda _: "y")
    result = hashbreak.confirm_online_lookup("5f4dcc3b5aa765d61d8327deb882cf99")
    assert result is True


def test_consent_prompt_always_remembers(monkeypatch):
    monkeypatch.delenv("HASHBREAK_OFFLINE", raising=False)
    hashbreak._CONFIRMED_ONLINE[0] = False
    monkeypatch.setattr("builtins.input", lambda _: "a")
    r1 = hashbreak.confirm_online_lookup("h1")
    r2 = hashbreak.confirm_online_lookup("h2")
    assert r1 is True and r2 is True
    # cached — no second prompt happened
    assert hashbreak._CONFIRMED_ONLINE[0] is True
