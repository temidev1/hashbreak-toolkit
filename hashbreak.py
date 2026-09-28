#!/usr/bin/env python3
"""
HashBreak v7.9 - Full Toolkit Edition
Hash cracker + port scanner + subdomain enum + dir buster
+ hash generator + password strength + encoders
Built by Maverick
"""

import hashlib
import requests
import sys
import time
import json
import csv
import re
import shutil
import subprocess
import itertools
import multiprocessing as mp
import hmac
import os
import socket
import ssl
import base64
import urllib.parse
import concurrent.futures
from pathlib import Path
from datetime import datetime
from http.client import HTTPConnection, HTTPSConnection

try:
    import scrypt as scrypt_module
    SCRYPT_AVAILABLE = True
except ImportError:
    SCRYPT_AVAILABLE = False

try:
    import bcrypt as bcrypt_module
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


# ============ COLORS ============
class C:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    BRIGHT_RED     = '\033[91m'
    BRIGHT_GREEN   = '\033[92m'
    BRIGHT_YELLOW  = '\033[93m'
    BRIGHT_BLUE    = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN    = '\033[96m'
    BRIGHT_WHITE   = '\033[97m'


def supports_color():
    if os.environ.get('NO_COLOR'):
        return False
    if not hasattr(sys.stdout, 'isatty'):
        return False
    return sys.stdout.isatty()


if not supports_color():
    for attr in dir(C):
        if not attr.startswith('_'):
            setattr(C, attr, '')


# ============ BANNER ============
BANNER_ART = r"""
 ██╗  ██╗ █████╗ ███████╗██╗  ██╗██████╗ ██████╗ ███████╗ █████╗ ██╗  ██╗
 ██║  ██║██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗██║ ██╔╝
 ███████║███████║███████╗███████║██████╔╝██████╔╝█████╗  ███████║█████╔╝ 
 ██╔══██║██╔══██║╚════██║██╔══██║██╔══██╗██╔══██╗██╔══╝  ██╔══██║██╔═██╗ 
 ██║  ██║██║  ██║███████║██║  ██║██████╔╝██║  ██║███████╗██║  ██║██║  ██╗
 ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""


def banner():
    print()
    print(C.BRIGHT_CYAN + BANNER_ART + C.RESET)
    line1 = "                    v7.9  ·  Full Toolkit  ·  Termux"
    line2 = "                       Built by Maverick"
    line3 = "         Cracker  ·  Recon  ·  OSINT  ·  Utilities"
    print(C.CYAN + line1 + C.RESET)
    print(C.BRIGHT_GREEN + C.BOLD + line2 + C.RESET)
    print(C.DIM + line3 + C.RESET)
    print()


ANSI_RE = re.compile(r'\033\[[0-9;]*m')


def visible_len(text):
    return len(ANSI_RE.sub('', text))


SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']


def progress_bar(done, total, width=30, extra=""):
    if total <= 0:
        return
    pct = done / total
    filled = int(width * pct)
    bar = '█' * filled + '░' * (width - filled)
    pct_str = f"{pct * 100:5.1f}%"
    line = f"  {C.CYAN}[{bar}]{C.RESET} {C.BOLD}{pct_str}{C.RESET} {C.DIM}{extra}{C.RESET}"
    print(f"\r{line}      ", end='', flush=True)


def progress_done():
    print()


def box_line(text, width, color=C.CYAN, align='left'):
    visible = visible_len(text)
    pad = width - visible - 2
    if pad < 0:
        plain = ANSI_RE.sub('', text)
        text = plain[:width - 2]
        pad = 0
    if align == 'center':
        left = pad // 2
        right = pad - left
        return f"{color}║{C.RESET} {' ' * left}{text}{' ' * right} {color}║{C.RESET}"
    return f"{color}║{C.RESET} {text}{' ' * pad} {color}║{C.RESET}"


def box_top(width, color=C.CYAN):
    return f"{color}╔{'═' * (width - 2)}╗{C.RESET}"


def box_bottom(width, color=C.CYAN):
    return f"{color}╚{'═' * (width - 2)}╝{C.RESET}"


def box_mid(width, color=C.CYAN):
    return f"{color}╠{'═' * (width - 2)}╣{C.RESET}"


def big_success(message, width=70):
    print()
    print(C.BRIGHT_GREEN + "  ╔" + "═" * (width - 4) + "╗" + C.RESET)
    line = f"  ║  ✅  {message}"
    pad = width - 4 - len("  ✅  " + message)
    print(C.BRIGHT_GREEN + line + " " * max(0, pad) + "║" + C.RESET)
    print(C.BRIGHT_GREEN + "  ╚" + "═" * (width - 4) + "╝" + C.RESET)
    print()


def big_failure(message, width=70):
    print()
    print(C.BRIGHT_RED + "  ╔" + "═" * (width - 4) + "╗" + C.RESET)
    line = f"  ║  ❌  {message}"
    pad = width - 4 - len("  ❌  " + message)
    print(C.BRIGHT_RED + line + " " * max(0, pad) + "║" + C.RESET)
    print(C.BRIGHT_RED + "  ╚" + "═" * (width - 4) + "╝" + C.RESET)
    print()


# ============ HASH PATTERNS ============
HASH_PATTERNS = [
    ('scrypt',        r'^\$7\$',                               'scrypt'),
    ('scrypt',        r'^\$scrypt\$',                          'scrypt'),
    ('bcrypt',        r'^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}',  'bcrypt'),
    ('sha512crypt',   r'^\$6\$',                               'sha512crypt'),
    ('sha256crypt',   r'^\$5\$',                               'sha256crypt'),
    ('md5crypt',      r'^\$1\$',                               'md5crypt'),
    ('phpass',        r'^\$P\$',                               'phpass'),
    ('PBKDF2',        r'^\$pbkdf2',                            'pbkdf2'),
    ('MySQL41',       r'^\*[0-9A-Fa-f]{40}$',                  'mysql41'),
    ('MySQL',         r'^[0-9A-Fa-f]{16}$',                    'mysql'),
    ('WPA-PMKID',     r'^WPA\*01\*',                           'wpa-pmkid'),
    ('WPA-HANDSHAKE', r'^WPA\*02\*',                           'wpa-hs'),
]

HASHCAT_MODE = {
    'MD5': 0, 'SHA1': 100, 'SHA224': 1300, 'SHA256': 1400,
    'SHA384': 10800, 'SHA512': 1700, 'NTLM': 1000,
    'bcrypt': 3200, 'sha512crypt': 1800, 'sha256crypt': 7400,
    'md5crypt': 500, 'phpass': 400, 'scrypt': 8900,
    'mysql41': 300, 'mysql': 200, 'lm': 3000,
    'wpa-pmkid': 22000, 'wpa-hs': 22000,
}

MASK_CLASSES = {
    '?l': 'abcdefghijklmnopqrstuvwxyz',
    '?u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    '?d': '0123456789',
    '?s': '!@#$%^&*()-_=+[]{};:,.<>?/\\|`~"\'',
    '?a': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{};:,.<>?/\\|`~"\'',
}

RULES_FAST = [
    lambda w: w,
    lambda w: w.capitalize(),
    lambda w: w.upper(),
    lambda w: w.lower(),
    lambda w: w + '1',
    lambda w: w + '12',
    lambda w: w + '123',
    lambda w: w + '1234',
    lambda w: w + '12345',
    lambda w: w + '123456',
    lambda w: w + '!',
    lambda w: w + '!!',
    lambda w: w + '@',
    lambda w: w + '#',
    lambda w: w + '$',
    lambda w: w + '?',
    lambda w: w + '.',
    lambda w: w + '0',
    lambda w: w + '01',
    lambda w: w + '007',
    lambda w: w + '2024',
    lambda w: w + '2025',
    lambda w: w + '2026',
    lambda w: '1' + w,
    lambda w: '123' + w,
    lambda w: '!' + w,
    lambda w: w.capitalize() + '1',
    lambda w: w.capitalize() + '123',
    lambda w: w.capitalize() + '!',
    lambda w: w.upper() + '1',
    lambda w: w.replace('a', '@').replace('o', '0').replace('i', '1').replace('e', '3'),
    lambda w: w.replace('a', '4').replace('e', '3').replace('i', '1').replace('o', '0'),
    lambda w: w.capitalize().replace('a', '@').replace('o', '0'),
    lambda w: w + w,
    lambda w: w + '_',
    lambda w: '_' + w,
    lambda w: w + '123!',
    lambda w: w + '@123',
    lambda w: w.capitalize() + '@123',
    lambda w: w.capitalize() + '@',
    lambda w: w[::-1],
    lambda w: w + 'qwerty',
    lambda w: w + 'abc',
    lambda w: w + '2020',
    lambda w: w + '2021',
    lambda w: w + '2022',
    lambda w: w + '2023',
    lambda w: re.sub(r'[aeiou]', lambda m: {'a':'4','e':'3','i':'1','o':'0','u':'9'}[m.group()], w.lower()),
    lambda w: w + w[-1] if w else w,
    lambda w: w + w[-1] + w[-1] if w else w,
    lambda w: w + '1!',
    lambda w: w.capitalize() + '1!',
]

SUFFIXES = ['1', '123', '1234', '!', '@', '2024', '2025', '2026', '01', '007']


def _should_apply_suffix(candidate):
    if not candidate:
        return False
    last = candidate[-1]
    if last in '!@#$%^&*._-':
        return False
    return True


def apply_rules_fast(word):
    seen = set()
    for rule in RULES_FAST:
        try:
            cand = rule(word)
            if cand and cand not in seen:
                seen.add(cand)
                yield cand
        except Exception:
            continue


def apply_rules_deep(word):
    seen = set()
    first_layer = []
    for rule in RULES_FAST:
        try:
            cand = rule(word)
            if cand and cand not in seen:
                seen.add(cand)
                first_layer.append(cand)
                yield cand
        except Exception:
            continue
    for base in first_layer:
        if not _should_apply_suffix(base):
            continue
        for suffix in SUFFIXES:
            cand = base + suffix
            if cand and cand not in seen:
                seen.add(cand)
                yield cand


def ntlm_hash(word):
    try:
        return hashlib.new('md4', word.encode('utf-16le')).hexdigest()
    except ValueError:
        try:
            from Crypto.Hash import MD4
            h = MD4.new()
            h.update(word.encode('utf-16le'))
            return h.hexdigest()
        except ImportError:
            return None


def lm_hash(word):
    try:
        from Crypto.Cipher import DES
    except ImportError:
        return None
    MAGIC = b"KGS!@#$%"
    def des_encrypt(key7):
        key = key7 + b'\x00' * (8 - len(key7))
        key8 = bytearray(8)
        key8[0] = key[0] & 0xFE
        key8[1] = ((key[0] << 7) | (key[1] >> 1)) & 0xFE
        key8[2] = ((key[1] << 6) | (key[2] >> 2)) & 0xFE
        key8[3] = ((key[2] << 5) | (key[3] >> 3)) & 0xFE
        key8[4] = ((key[3] << 4) | (key[4] >> 4)) & 0xFE
        key8[5] = ((key[4] << 3) | (key[5] >> 5)) & 0xFE
        key8[6] = ((key[5] << 2) | (key[6] >> 6)) & 0xFE
        key8[7] = (key[6] << 1) & 0xFE
        cipher = DES.new(bytes(key8), DES.MODE_ECB)
        return cipher.encrypt(MAGIC)
    pw = word.upper().encode('ascii', errors='ignore')[:14]
    pw = pw + b'\x00' * (14 - len(pw))
    h1 = des_encrypt(pw[:7])
    h2 = des_encrypt(pw[7:14])
    return (h1 + h2).hex()


def mysql_native_password(word):
    s1 = hashlib.sha1(word.encode()).digest()
    s2 = hashlib.sha1(s1).digest()
    return '*' + s2.hex().upper()


def parse_hc22000(hash_str):
    parts = hash_str.strip().split('*')
    if len(parts) < 6 or parts[0] != 'WPA' or parts[1] != '01':
        return None
    pmkid = parts[2]
    ap_mac = parts[3]
    sta_mac = parts[4]
    essid_hex = parts[5]
    try:
        essid = bytes.fromhex(essid_hex)
        ap_mac_b = bytes.fromhex(ap_mac)
        sta_mac_b = bytes.fromhex(sta_mac)
    except ValueError:
        return None
    return pmkid, ap_mac_b, sta_mac_b, essid


def compute_pmkid(password, essid, ap_mac, sta_mac):
    pmk = hashlib.pbkdf2_hmac('sha1', password.encode(), essid, 4096, 32)
    data = b"PMK Name" + ap_mac + sta_mac
    return hmac.new(pmk, data, hashlib.sha1).digest()[:16]


def parse_mask(mask):
    classes = []
    i = 0
    while i < len(mask):
        if mask[i] == '?' and i + 1 < len(mask):
            key = mask[i:i+2]
            if key in MASK_CLASSES:
                classes.append(MASK_CLASSES[key])
                i += 2
                continue
        classes.append(mask[i])
        i += 1
    return classes


def mask_size(classes):
    n = 1
    for c in classes:
        n *= len(c)
    return n


# ============ WORKERS ============
def _wpa_worker(args):
    chunk, pmkid, ap_mac, sta_mac, essid, rules_mode = args
    rule_fn = apply_rules_fast if rules_mode == 'fast' else apply_rules_deep
    for word in chunk:
        for candidate in rule_fn(word):
            if compute_pmkid(candidate, essid, ap_mac, sta_mac).hex() == pmkid:
                return candidate
    return None


def _worker(args):
    chunk, fn_name, target, rules_mode = args
    fn = getattr(hashlib, fn_name)
    rule_fn = apply_rules_fast if rules_mode == 'fast' else apply_rules_deep
    for word in chunk:
        for candidate in rule_fn(word):
            if fn(candidate.encode('utf-8')).hexdigest() == target:
                return candidate
    return None


def _ntlm_worker(args):
    chunk, target, rules_mode = args
    rule_fn = apply_rules_fast if rules_mode == 'fast' else apply_rules_deep
    for word in chunk:
        for candidate in rule_fn(word):
            h = ntlm_hash(candidate)
            if h and h == target:
                return candidate
    return None


def _lm_worker(args):
    chunk, target, rules_mode = args
    rule_fn = apply_rules_fast if rules_mode == 'fast' else apply_rules_deep
    for word in chunk:
        for candidate in rule_fn(word):
            h = lm_hash(candidate)
            if h and h == target:
                return candidate
    return None


def _mysql_worker(args):
    chunk, target, rules_mode = args
    rule_fn = apply_rules_fast if rules_mode == 'fast' else apply_rules_deep
    for word in chunk:
        for candidate in rule_fn(word):
            if mysql_native_password(candidate).upper() == target.upper():
                return candidate
    return None


def _mask_worker(args):
    classes, start, end, fn_name, target = args
    fn = getattr(hashlib, fn_name)
    for idx in range(start, end):
        n = idx
        chars = []
        for c in reversed(classes):
            chars.append(c[n % len(c)])
            n //= len(c)
        candidate = ''.join(reversed(chars))
        if fn(candidate.encode('utf-8')).hexdigest() == target:
            return candidate
    return None


def _hybrid_worker(args):
    chunk, fn_name, target, classes, msize, mode = args
    fn = getattr(hashlib, fn_name)
    for word in chunk:
        for idx in range(msize):
            n = idx
            chars = []
            for c in reversed(classes):
                chars.append(c[n % len(c)])
                n //= len(c)
            mstr = ''.join(reversed(chars))
            candidate = word + mstr if mode == 'suffix' else mstr + word
            if fn(candidate.encode('utf-8')).hexdigest() == target:
                return candidate
    return None


# ============ TOOLKIT HELPERS ============
TOP_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 161, 162, 389, 443, 445,
    465, 514, 587, 636, 993, 995, 1080, 1433, 1521, 1723, 2049, 2082, 2083,
    2181, 2375, 3000, 3306, 3389, 4443, 5000, 5432, 5900, 5984, 6379, 7001,
    8000, 8008, 8080, 8081, 8443, 8888, 9000, 9090, 9200, 9300, 11211, 27017,
]


def scan_port(host, port, timeout=1.5):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                # try grabbing a banner
                banner = ""
                try:
                    s.settimeout(0.8)
                    banner = s.recv(128).decode(errors='ignore').strip().split('\n')[0][:60]
                except Exception:
                    pass
                return (port, True, banner)
            return (port, False, "")
    except Exception:
        return (port, False, "")


def port_to_service(port):
    services = {
        21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
        80: "http", 110: "pop3", 135: "msrpc", 139: "netbios", 143: "imap",
        161: "snmp", 389: "ldap", 443: "https", 445: "smb", 465: "smtps",
        514: "syslog", 587: "smtp", 636: "ldaps", 993: "imaps", 995: "pop3s",
        1080: "socks", 1433: "mssql", 1521: "oracle", 1723: "pptp",
        2049: "nfs", 2082: "cpanel", 2083: "cpanel-ssl", 2181: "zookeeper",
        2375: "docker", 3000: "node", 3306: "mysql", 3389: "rdp",
        4443: "https-alt", 5000: "flask", 5432: "postgres", 5900: "vnc",
        5984: "couchdb", 6379: "redis", 7001: "weblogic", 8000: "http-alt",
        8008: "http-alt", 8080: "http-proxy", 8081: "http-alt",
        8443: "https-alt", 8888: "http-alt", 9000: "php-fpm",
        9090: "http-alt", 9200: "elasticsearch", 9300: "elasticsearch",
        11211: "memcached", 27017: "mongodb",
    }
    return services.get(port, "")


DIR_WORDLIST = [
    "admin", "administrator", "login", "wp-admin", "wp-login.php", "wp-config.php",
    "wp-content", "wp-includes", "backup", "backups", "backup.zip", "backup.tar.gz",
    "db.sql", "database.sql", "dump.sql", "config", "config.php", "config.json",
    "config.yml", ".env", ".git", ".git/config", ".git/HEAD", ".gitignore",
    ".htaccess", ".htpasswd", ".DS_Store", "robots.txt", "sitemap.xml",
    "phpmyadmin", "pma", "myadmin", "mysql", "mysqladmin", "adminer.php",
    "api", "api/v1", "api/v2", "graphql", "swagger.json", "openapi.json",
    "uploads", "files", "download", "downloads", "images", "img", "css", "js",
    "static", "assets", "public", "private", "secret", "secrets", "keys",
    "test", "tests", "testing", "dev", "development", "staging", "stage",
    "old", "old-site", "backup-old", "new", "beta", "alpha",
    "cgi-bin", "shell", "cmd", "exec", "system", "admin.php", "login.php",
    "index.php", "index.html", "home", "dashboard", "panel", "control",
    "user", "users", "account", "accounts", "profile", "register", "signup",
    "logout", "forgot", "reset", "password", "passwords", "token", "tokens",
    "docs", "doc", "documentation", "readme", "README.md", "CHANGELOG.md",
    "LICENSE", "package.json", "composer.json", "requirements.txt",
    "server-status", "server-info", "phpinfo.php", "info.php", "test.php",
    "install", "setup", "upgrade", "update", "migrate",
    "console", "terminal", "log", "logs", "access.log", "error.log",
    "checkout", "cart", "orders", "products", "shop", "store",
    "blog", "news", "articles", "posts", "feed", "rss",
    "contact", "about", "help", "support", "faq",
]


SUBDOMAIN_WORDLIST = [
    "www", "mail", "ftp", "webmail", "smtp", "pop", "imap", "mx", "ns1", "ns2",
    "ns3", "ns4", "dns", "dns1", "dns2", "api", "api-v1", "api-v2", "app",
    "apps", "dev", "development", "staging", "stage", "test", "testing",
    "qa", "uat", "prod", "production", "admin", "administrator", "panel",
    "cpanel", "whm", "webdisk", "cpcalendars", "cpcontacts", "autodiscover",
    "autoconfig", "blog", "shop", "store", "cdn", "static", "assets", "img",
    "images", "media", "files", "download", "downloads", "uploads", "docs",
    "doc", "documentation", "wiki", "help", "support", "faq", "forum",
    "community", "chat", "meet", "video", "stream", "live", "vpn", "remote",
    "rdp", "ssh", "git", "gitlab", "github", "bitbucket", "jenkins", "ci",
    "cd", "jira", "confluence", "slack", "mattermost", "monitor", "monitoring",
    "grafana", "prometheus", "kibana", "elastic", "elasticsearch", "logstash",
    "kafka", "rabbitmq", "redis", "mysql", "postgres", "mongo", "mongodb",
    "db", "database", "sql", "backup", "backups", "old", "new", "beta",
    "alpha", "v1", "v2", "v3", "mobile", "m", "wap", "portal", "sso", "auth",
    "login", "signup", "register", "account", "accounts", "secure", "ssl",
    "tls", "internal", "intranet", "extranet", "partner", "partners",
    "vendor", "vendors", "client", "clients", "customer", "customers",
]


# ============ MAIN CLASS ============


# ============ ADVANCED PORT SCANNER HELPERS ============

TOP_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 161, 162, 389, 443, 445,
    465, 514, 587, 636, 993, 995, 1080, 1433, 1521, 1723, 2049, 2082, 2083,
    2181, 2375, 3000, 3306, 3389, 4443, 5000, 5432, 5900, 5984, 6379, 7001,
    8000, 8008, 8080, 8081, 8443, 8888, 9000, 9090, 9200, 9300, 11211, 27017,
]


def grab_banner(sock, port):
    """try to get a banner. sends probes for services that don't auto-banner."""
    banner = b""
    try:
        sock.settimeout(1.5)
        # some services send banner immediately
        try:
            banner = sock.recv(1024)
        except socket.timeout:
            pass

        if not banner:
            # try protocol-specific probes
            if port in (80, 8080, 8000, 8008, 8888, 443, 8443):
                try:
                    sock.send(b"GET / HTTP/1.0\r\nHost: " + sock.getpeername()[0].encode() + b"\r\n\r\n")
                    banner = sock.recv(2048)
                except Exception:
                    pass
            elif port == 22:
                # SSH banner comes automatically, but try again if missed
                pass
            elif port == 21:
                # FTP banner automatic
                pass
            elif port == 25:
                try:
                    sock.send(b"EHLO test\r\n")
                    banner = sock.recv(512)
                except Exception:
                    pass
            elif port in (143, 993, 110, 995):
                pass  # banner automatic
    except Exception:
        pass
    return banner.decode(errors="ignore", ) if banner else ""


def identify_service(banner, port):
    """parse banner to identify actual software + version"""
    if not banner:
        return (port_to_service(port), "")

    b = banner.lower()

    # SSH
    if "ssh-" in b:
        import re as _re
        m = _re.search(r"ssh-([0-9.]+)-?([a-z0-9_.-]*)", b)
        if m:
            return ("ssh", f"{m.group(2)} {m.group(1)}".strip())
        return ("ssh", "")
    # HTTP server
    if "http/" in b:
        import re as _re
        m = _re.search(r"server:\s*([^\r\n]+)", banner, _re.IGNORECASE)
        if m:
            return ("http", m.group(1).strip()[:28])
        return ("http", "")
    # FTP
    if "ftp" in b and "220" in banner[:10]:
        return ("ftp", banner[:60].strip())
    # SMTP
    if "smtp" in b or "220 " in banner[:10] and "mail" in b:
        return ("smtp", banner[:60].strip())
    # MySQL
    if "mysql" in b:
        return ("mysql", "")
    # Redis
    if b.startswith("-err") or "+pong" in b or "redis" in b:
        return ("redis", "")
    # MongoDB
    if "mongodb" in b or "ismaster" in b:
        return ("mongodb", "")
    # Generic fallback
    return (port_to_service(port), "")


def scan_port_advanced(host, port, timeout=1.5):
    """connect, grab banner, identify service. returns (port, banner, service, version) or None."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            r = s.connect_ex((host, port))
            if r != 0:
                return None
            banner = grab_banner(s, port)
            service, version = identify_service(banner, port)
            return (port, banner, service, version)
    except Exception:
        return None


def guess_os(open_ports):
    """return a list of OS hints from banners + open ports.
    NOT authoritative — banners can lie, containers exist, and proper OS
    detection needs TTL/TCP-stack fingerprinting (which needs raw sockets)."""
    hints = []
    for port, banner, service, version in open_ports:
        b = (banner or "").lower()
        v = (version or "").lower()
        if "ubuntu" in b or "ubuntu" in v:
            hints.append("Linux · Ubuntu string in banner")
        if "debian" in b or "debian" in v:
            hints.append("Linux · Debian string in banner")
        if "centos" in b or "centos" in v:
            hints.append("Linux · CentOS string in banner")
        if "fedora" in b or "fedora" in v:
            hints.append("Linux · Fedora string in banner")
        if "freebsd" in b or "freebsd" in v:
            hints.append("FreeBSD · string in banner")
        if "openbsd" in b or "openbsd" in v:
            hints.append("OpenBSD · string in banner")
        if "iis" in v or "microsoft-iis" in v:
            hints.append("Windows · IIS HTTP server")
        if port in (445, 139):
            hints.append(f"Windows · SMB open on {port}")
        if port == 3389:
            hints.append("Windows · RDP open on 3389")
        if port == 5985 or port == 5986:
            hints.append("Windows · WinRM open")
        if port == 22:
            hints.append("Linux/Unix · SSH open (default on most)")
    return list(dict.fromkeys(hints))   # dedupe, preserve order




def expand_targets(target_str):
    """expand CIDR, comma-lists, single hosts into a list of hostnames/IPs"""
    targets = []
    for part in target_str.split(','):
        part = part.strip()
        if not part:
            continue
        if '/' in part:
            # CIDR
            try:
                ips = cidr_to_ips(part)
                targets.extend(ips)
            except Exception:
                pass
        elif '-' in part and part.replace('-', '').replace('.', '').isdigit():
            # IP range like 192.168.1.1-10
            try:
                prefix, last = part.rsplit('.', 1)
                if '-' in last:
                    a, b = last.split('-')
                    for i in range(int(a), int(b) + 1):
                        targets.append(f"{prefix}.{i}")
                else:
                    targets.append(part)
            except Exception:
                targets.append(part)
        else:
            targets.append(part)
    return list(dict.fromkeys(targets))   # dedupe


def cidr_to_ips(cidr):
    """convert CIDR to list of IPs. /24 = 254 hosts, /16 = 65k, /8 = 16M (warn)."""
    import ipaddress
    net = ipaddress.ip_network(cidr, strict=False)
    if net.num_addresses > 4096:
        print(f"  {C.YELLOW}⚠ {cidr} has {net.num_addresses:,} hosts — scanning first 4096{C.RESET}")
    return [str(ip) for i, ip in enumerate(net.hosts()) if i < 4096]


def ping_host(ip, timeout=1.0):
    """ping check: try TCP connect to port 80, 443, 22 in sequence"""
    for port in (80, 443, 22):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((ip, port)) == 0:
                    return True
        except Exception:
            pass
    return False



# ============ TRACEROUTE (TCP-based, no root needed) ============

def tcp_traceroute(target, port=80, max_hops=20, timeout=2.0):
    """TCP traceroute: send SYN with increasing TTL, read ICMP time-exceeded.
    Returns list of (hop_num, ip_or_star, rtt_ms)."""
    results = []
    try:
        dest_ip = socket.gethostbyname(target)
    except socket.gaierror:
        return results

    for ttl in range(1, max_hops + 1):
        hop_ip = None
        rtt_ms = None
        try:
            # create a raw ICMP receiver (falls back to nothing on non-root)
            # instead use TCP connect with custom TTL via socket option
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            try:
                s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            except (OSError, AttributeError):
                # IP_TTL not settable without root on some platforms
                s.close()
                return results

            t0 = time.time()
            s.connect_ex((dest_ip, port))
            rtt_ms = (time.time() - t0) * 1000
            # get peer address
            peer = s.getpeername()
            hop_ip = peer[0]
            s.close()

            results.append((ttl, hop_ip, rtt_ms))

            if hop_ip == dest_ip:
                break

        except socket.timeout:
            results.append((ttl, "*", None))
        except Exception:
            results.append((ttl, "*", None))

    return results


# ============ NMAP SERVICE PROBE DB ============

SERVICE_PROBES = []   # list of (name, payload_bytes, ports_list)


def load_service_probes(path=None):
    """parse nmap-service-probes. returns list of (name, payload, ports)."""
    global SERVICE_PROBES
    if SERVICE_PROBES:
        return SERVICE_PROBES

    if not path:
        path = str(Path.home() / "nmap-service-probes")
    if not Path(path).exists():
        return []

    probes = []
    current = None
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('Probe '):
                # Probe TCP GetRequest q|GET / HTTP/1.0\\r\\n\\r\\n|
                try:
                    parts = line.split(' ', 3)
                    proto = parts[1]
                    name = parts[2]
                    rest = parts[3]
                    if rest.startswith('q|'):
                        end = rest.rfind('|')
                        payload_str = rest[2:end]
                        # unescape nmap's backslash escapes
                        payload_str = payload_str.replace('\\r', '\r').replace('\\n', '\n').replace('\\\\', '\\')
                        payload = payload_str.encode('latin-1', errors='ignore')
                        probes.append((name, payload))
                except Exception:
                    continue

    SERVICE_PROBES = probes
    return probes


def probe_port(ip, port, timeout=2.0):
    """send nmap probes to a port, return (service, version, evidence) from match rules."""
    probes = load_service_probes()
    if not probes:
        return None

    evidence_parts = []
    # try the generic probes first (GetRequest, GenericLines, etc)
    priority = ["GetRequest", "HTTPOptions", "GenericLines", "NULL", "Help", "RTSPRequest"]
    ordered = sorted(probes, key=lambda p: (p[0] not in priority, p[0]))

    for name, payload in ordered[:10]:   # try up to 10 probes
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((ip, port)) != 0:
                    return None
                if payload:
                    s.sendall(payload)
                try:
                    resp = s.recv(4096)
                except socket.timeout:
                    resp = b""
                if resp:
                    evidence_parts.append((name, resp))
                    # naive: return first service-looking string
                    text = resp.decode('latin-1', errors='ignore')
                    svc, ver = identify_service(text, port)
                    if svc and svc != "unknown":
                        return (svc, ver, text[:200])
        except Exception:
            continue

    if evidence_parts:
        text = evidence_parts[0][1].decode('latin-1', errors='ignore')
        svc, ver = identify_service(text, port)
        return (svc, ver, text[:200])

    return None


class HashBreakModern:
    def __init__(self):
        self.results = []
        self.cracked_count = 0
        self.failed_count = 0
        self.debug_mode = False
        self.use_hashcat = False
        self.workers = max(1, mp.cpu_count())
        if os.environ.get('HASHBREAK_NO_POOL'):
            self.workers = 1
        self.classic_lengths = {
            32: 'MD5', 40: 'SHA1', 56: 'SHA224', 64: 'SHA256',
            96: 'SHA384', 128: 'SHA512'
        }

    def display_banner(self):
        banner()

    def log(self, message, level="INFO"):
        if self.debug_mode:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"  {C.DIM}[{timestamp}] {level}: {message}{C.RESET}")

    def detect_hash_type(self, hash_str):
        hash_str = hash_str.strip()
        for name, pattern, kind in HASH_PATTERNS:
            if re.match(pattern, hash_str, re.IGNORECASE):
                return kind
        length = len(hash_str)
        if length in self.classic_lengths:
            return self.classic_lengths[length]
        return None

    def online_lookup(self, hash_str):
        self.log("Trying online lookup...")
        try:
            r = requests.get(f'https://md5.gromweb.com/?md5={hash_str}', timeout=6)
            if r.status_code == 200:
                m = re.search(r'<em class="long-content string">([^<]+)</em>', r.text)
                if m:
                    return m.group(1)
        except Exception:
            pass
        return None

    def load_wordlist(self, wordlist_path=None):
        if not wordlist_path:
            wordlist_paths = [
                str(Path.home() / 'top1m.txt'),
                str(Path.home() / 'merged_ng.txt'),
                str(Path.home() / 'rockyou.txt'),
                '/usr/share/wordlists/rockyou.txt',
                str(Path.home() / 'wordlist.txt'),
                'wordlist.txt',
            ]
            for path in wordlist_paths:
                p = Path(path)
                if p.exists() and p.stat().st_size > 1000:
                    wordlist_path = path
                    break
            if not wordlist_path:
                return self.create_default_wordlist()
        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                return [w.strip() for w in f.readlines() if w.strip()]
        except FileNotFoundError:
            return self.create_default_wordlist()

    def create_default_wordlist(self):
        return ['password', '123456', '12345678', 'qwerty', 'abc123',
                'admin', 'root', 'test', 'guest', 'user', 'admin123',
                'pass', 'welcome', 'sunshine', 'shadow', 'passw0rd']

    # ============ CRACKING METHODS ============
    def crack_pbkdf2(self, hash_str, wordlist=None):
        if not wordlist:
            wordlist = self.load_wordlist()
        parts = hash_str.split('$')
        if len(parts) < 5:
            return None
        try:
            if parts[1].startswith('pbkdf2-'):
                algo = parts[1].split('-', 1)[1]
                rounds = int(parts[2])
                salt = parts[3]
                target = parts[4]
            else:
                algo = parts[2]
                rounds = int(parts[3])
                salt = parts[4]
                target = parts[5]
        except (ValueError, IndexError):
            return None
        target = target.strip().lower()
        for word in wordlist:
            for candidate in apply_rules_deep(word):
                dk = hashlib.pbkdf2_hmac(algo, candidate.encode('utf-8'),
                                         salt.encode('utf-8'), rounds)
                if dk.hex().lower() == target:
                    return candidate
        return None

    def crack_scrypt(self, hash_str, wordlist=None):
        if not SCRYPT_AVAILABLE:
            return None
        if not wordlist:
            wordlist = self.load_wordlist()
        parts = hash_str.split('$')
        if len(parts) < 6:
            return None
        try:
            N = int(parts[2]) if parts[2] else 16384
            r = int(parts[3]) if parts[3] else 8
            p = int(parts[4]) if parts[4] else 1
            salt = parts[5]
            target = parts[6] if len(parts) > 6 else ''
        except (ValueError, IndexError):
            return None
        target = target.lower()
        for word in wordlist:
            for candidate in apply_rules_deep(word):
                dk = scrypt_module.hash(candidate.encode(), salt=salt.encode(),
                                        N=N, r=r, p=p, dklen=32)
                if dk.hex().lower() == target:
                    return candidate
        return None

    def crack_bcrypt(self, hash_str, wordlist=None):
        if not BCRYPT_AVAILABLE:
            return None
        if not wordlist:
            wordlist = self.load_wordlist()
        target = hash_str.strip().encode()
        count = 0
        start = time.time()
        total = len(wordlist)
        print(f"  {C.DIM}bcrypt is deliberately slow — expect ~200-400 h/s{C.RESET}")
        for word in wordlist:
            count += 1
            if count % 50 == 0:
                elapsed = time.time() - start
                rate = count / elapsed if elapsed > 0 else 0
                eta = (total - count) / rate if rate > 0 else 0
                progress_bar(count, total, extra=f"{rate:6.1f} h/s   ETA {int(eta)}s")
            for candidate in apply_rules_fast(word):
                try:
                    if bcrypt_module.checkpw(candidate.encode(), target):
                        progress_done()
                        return candidate
                except Exception:
                    continue
        progress_done()
        return None

    def crack_wpa_pmkid(self, hash_str, wordlist=None):
        if not wordlist:
            wordlist = self.load_wordlist()
        parsed = parse_hc22000(hash_str)
        if not parsed:
            print(f"  {C.RED}❌ failed to parse .hc22000 line{C.RESET}")
            return None
        pmkid, ap_mac, sta_mac, essid = parsed
        print(f"  {C.CYAN}PMKID{C.RESET}  {pmkid}")
        print(f"  {C.CYAN}ESSID{C.RESET}  {essid.decode(errors='replace')}")
        print()
        words = wordlist if isinstance(wordlist, list) else [
            w.strip() for w in open(wordlist, encoding='utf-8', errors='ignore').readlines() if w.strip()
        ]
        total = len(words)
        if total == 0:
            return None
        n_chunks = self.workers * 4
        chunk_size = max(1, total // n_chunks)
        chunks = [words[i:i + chunk_size] for i in range(0, total, chunk_size)]
        print(f"  {C.DIM}multiprocess · {self.workers} workers · {total} words{C.RESET}")
        start = time.time()
        found = [None]
        processed = [0]
        with mp.Pool(self.workers) as pool:
            tasks = [(c, pmkid, ap_mac, sta_mac, essid, 'fast') for c in chunks]
            for result in pool.imap_unordered(_wpa_worker, tasks, chunksize=1):
                processed[0] += chunk_size
                elapsed = time.time() - start
                done = min(processed[0], total)
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                progress_bar(done, total, extra=f"{rate:6.1f} w/s   ETA {int(eta)}s")
                if result is not None:
                    found[0] = result
                    pool.terminate()
                    break
        progress_done()
        return found[0]

    def _run_ntlm(self, hash_str, words, rules_mode, label):
        target = hash_str.lower()
        total = len(words)
        start = time.time()
        n_chunks = self.workers * 4
        chunk_size = max(1, total // n_chunks)
        chunks = [words[i:i + chunk_size] for i in range(0, total, chunk_size)]
        print(f"  {C.DIM}phase: {label}{C.RESET}")
        found = [None]
        processed = [0]
        with mp.Pool(self.workers) as pool:
            tasks = [(c, target, rules_mode) for c in chunks]
            for result in pool.imap_unordered(_ntlm_worker, tasks, chunksize=1):
                processed[0] += chunk_size
                elapsed = time.time() - start
                done = min(processed[0], total)
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                progress_bar(done, total, extra=f"{rate:6.0f} w/s   ETA {int(eta)}s")
                if result is not None:
                    found[0] = result
                    pool.terminate()
                    break
        progress_done()
        return found[0]

    def _run_lm(self, hash_str, words, rules_mode, label):
        target = hash_str.lower()
        total = len(words)
        start = time.time()
        n_chunks = self.workers * 4
        chunk_size = max(1, total // n_chunks)
        chunks = [words[i:i + chunk_size] for i in range(0, total, chunk_size)]
        print(f"  {C.DIM}phase: {label}{C.RESET}")
        found = [None]
        processed = [0]
        with mp.Pool(self.workers) as pool:
            tasks = [(c, target, rules_mode) for c in chunks]
            for result in pool.imap_unordered(_lm_worker, tasks, chunksize=1):
                processed[0] += chunk_size
                elapsed = time.time() - start
                done = min(processed[0], total)
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                progress_bar(done, total, extra=f"{rate:6.0f} w/s   ETA {int(eta)}s")
                if result is not None:
                    found[0] = result
                    pool.terminate()
                    break
        progress_done()
        return found[0]

    def _run_mysql(self, hash_str, words, rules_mode, label):
        target = hash_str.strip()
        total = len(words)
        start = time.time()
        n_chunks = self.workers * 4
        chunk_size = max(1, total // n_chunks)
        chunks = [words[i:i + chunk_size] for i in range(0, total, chunk_size)]
        print(f"  {C.DIM}phase: {label}{C.RESET}")
        found = [None]
        processed = [0]
        with mp.Pool(self.workers) as pool:
            tasks = [(c, target, rules_mode) for c in chunks]
            for result in pool.imap_unordered(_mysql_worker, tasks, chunksize=1):
                processed[0] += chunk_size
                elapsed = time.time() - start
                done = min(processed[0], total)
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                progress_bar(done, total, extra=f"{rate:6.0f} w/s   ETA {int(eta)}s")
                if result is not None:
                    found[0] = result
                    pool.terminate()
                    break
        progress_done()
        return found[0]

    def _run_pass(self, words, fn_name, target, rules_mode, label):
        total = len(words)
        start = time.time()
        n_chunks = self.workers * 4
        chunk_size = max(1, total // n_chunks)
        chunks = [words[i:i + chunk_size] for i in range(0, total, chunk_size)]
        print(f"  {C.DIM}phase: {label}{C.RESET}")
        found = [None]
        processed = [0]
        with mp.Pool(self.workers) as pool:
            tasks = [(c, fn_name, target, rules_mode) for c in chunks]
            for result in pool.imap_unordered(_worker, tasks, chunksize=1):
                processed[0] += chunk_size
                elapsed = time.time() - start
                done = min(processed[0], total)
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                progress_bar(done, total, extra=f"{rate:6.0f} w/s   ETA {int(eta)}s")
                if result is not None:
                    found[0] = result
                    pool.terminate()
                    break
        progress_done()
        return found[0]

    def crack_classic(self, hash_str, wordlist=None):
        if not wordlist:
            wordlist = self.load_wordlist()
        hash_type = self.detect_hash_type(hash_str)
        if hash_type not in self.classic_lengths.values():
            return None
        fn_name_map = {
            'MD5': 'md5', 'SHA1': 'sha1', 'SHA224': 'sha224',
            'SHA256': 'sha256', 'SHA384': 'sha384', 'SHA512': 'sha512',
        }
        fn_name = fn_name_map.get(hash_type)
        if not fn_name:
            return None
        target = hash_str.lower().strip()
        if isinstance(wordlist, list):
            words = wordlist
        else:
            try:
                with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                    words = [w.strip() for w in f.readlines() if w.strip()]
            except Exception:
                words = self.create_default_wordlist()
        result = self._run_pass(words, fn_name, target, 'fast', 'fast rules')
        if result:
            return result
        result = self._run_pass(words, fn_name, target, 'deep', 'deep rules (2-layer)')
        if result:
            return result
        if hash_type == 'MD5' and len(target) == 32 and os.environ.get('TRY_NTLM'):
            result = self._run_ntlm(target, words, 'fast', 'ntlm fallback (fast)')
            if result:
                return result
            result = self._run_ntlm(target, words, 'deep', 'ntlm fallback (deep)')
            if result:
                return result
        return None

    def crack_mask(self, hash_str, mask):
        hash_type = self.detect_hash_type(hash_str)
        if hash_type not in self.classic_lengths.values():
            return None
        fn_name_map = {
            'MD5': 'md5', 'SHA1': 'sha1', 'SHA224': 'sha224',
            'SHA256': 'sha256', 'SHA384': 'sha384', 'SHA512': 'sha512',
        }
        fn_name = fn_name_map.get(hash_type)
        if not fn_name:
            return None
        target = hash_str.lower().strip()
        classes = parse_mask(mask)
        total = mask_size(classes)
        print(f"  {C.CYAN}mask{C.RESET}      {mask}")
        print(f"  {C.CYAN}keyspace{C.RESET}  {total:,} candidates")
        print()
        start = time.time()
        n_chunks = self.workers * 4
        chunk_size = max(1, total // n_chunks)
        found = [None]
        processed = [0]
        with mp.Pool(self.workers) as pool:
            tasks = []
            for start_i in range(0, total, chunk_size):
                end_i = min(start_i + chunk_size, total)
                tasks.append((classes, start_i, end_i, fn_name, target))
            for result in pool.imap_unordered(_mask_worker, tasks, chunksize=1):
                processed[0] += chunk_size
                elapsed = time.time() - start
                done = min(processed[0], total)
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                progress_bar(done, total, extra=f"{rate:6.0f} c/s   ETA {int(eta)}s")
                if result is not None:
                    found[0] = result
                    pool.terminate()
                    break
        progress_done()
        return found[0]

    def crack_hybrid(self, hash_str, mask, wordlist=None, mode='suffix', limit_words=None):
        if not wordlist:
            wordlist = self.load_wordlist()
        hash_type = self.detect_hash_type(hash_str)
        if hash_type not in self.classic_lengths.values():
            print(f"  {C.RED}hash type {hash_type} not supported by hybrid{C.RESET}")
            return None
        fn_name_map = {
            'MD5': 'md5', 'SHA1': 'sha1', 'SHA224': 'sha224',
            'SHA256': 'sha256', 'SHA384': 'sha384', 'SHA512': 'sha512',
        }
        fn_name = fn_name_map.get(hash_type)
        if not fn_name:
            return None
        target = hash_str.lower().strip()
        classes = parse_mask(mask)
        msize = mask_size(classes)
        if isinstance(wordlist, list):
            words = wordlist
        else:
            try:
                with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                    words = [w.strip() for w in f.readlines() if w.strip()]
            except Exception:
                words = self.create_default_wordlist()
        if limit_words and limit_words < len(words):
            words = words[:limit_words]
            print(f"  {C.YELLOW}⚠ limited to first {limit_words} words{C.RESET}")
        total = len(words) * msize
        print(f"  {C.CYAN}mask{C.RESET}      {mask}  ({msize:,} per word)")
        print(f"  {C.CYAN}words{C.RESET}     {len(words):,}")
        print(f"  {C.CYAN}mode{C.RESET}      {mode}")
        print(f"  {C.CYAN}keyspace{C.RESET}  {total:,}")
        print()
        start = time.time()
        n_chunks = min(self.workers * 4, len(words))
        chunk_size = max(1, len(words) // n_chunks)
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        found = [None]
        processed = [0]
        with mp.Pool(self.workers) as pool:
            tasks = [(c, fn_name, target, classes, msize, mode) for c in chunks]
            for result in pool.imap_unordered(_hybrid_worker, tasks, chunksize=1):
                processed[0] += chunk_size * msize
                elapsed = time.time() - start
                done = min(processed[0], total)
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                progress_bar(done, total, extra=f"{rate:6.0f} c/s   ETA {int(eta)}s")
                if result is not None:
                    found[0] = result
                    pool.terminate()
                    break
        progress_done()
        return found[0]

    def crack_single(self, hash_str):
        hash_type = self.detect_hash_type(hash_str)
        if not hash_type:
            return None
        if hash_type in ('MD5', 'SHA1'):
            result = self.online_lookup(hash_str)
            if result:
                return {'password': result, 'method': 'Online', 'type': hash_type}
        if hash_type == 'scrypt':
            result = self.crack_scrypt(hash_str)
            if result:
                return {'password': result, 'method': 'Scrypt', 'type': hash_type}
        elif hash_type == 'pbkdf2':
            result = self.crack_pbkdf2(hash_str)
            if result:
                return {'password': result, 'method': 'PBKDF2', 'type': hash_type}
        elif hash_type == 'bcrypt':
            result = self.crack_bcrypt(hash_str)
            if result:
                return {'password': result, 'method': 'bcrypt dictionary', 'type': hash_type}
        elif hash_type == 'mysql41':
            words = self.load_wordlist()
            result = self._run_mysql(hash_str, words, 'deep', 'mysql41 deep rules')
            if result:
                return {'password': result, 'method': 'MySQL41', 'type': hash_type}
        elif hash_type == 'wpa-pmkid':
            result = self.crack_wpa_pmkid(hash_str)
            if result:
                return {'password': result, 'method': 'WPA-PMKID', 'type': hash_type}
        elif hash_type == 'wpa-hs':
            print(f"  {C.YELLOW}⚠ WPA handshake (WPA*02*) not implemented{C.RESET}")
            return None
        else:
            result = self.crack_classic(hash_str)
            if result:
                return {'password': result, 'method': 'Two-phase', 'type': hash_type}
        return None

    # ============ TOOLKIT: PORT SCANNER ============
    def tool_port_scan(self):
        width = 66
        print()
        print(box_top(width))
        print(box_line(f"{C.BOLD}PORT SCANNER{C.RESET}", width, align='center'))
        print(box_mid(width))
        print(box_line(f"{C.DIM}TCP connect · banner · version · CIDR · ping sweep{C.RESET}", width))
        print(box_bottom(width))
        print()

        target = input(f"  {C.CYAN}target{C.RESET} (host, IP, CIDR, or comma-list) ❯ ").strip()
        if not target:
            print(f"  {C.YELLOW}no target{C.RESET}")
            return

        print()
        print(f"  {C.CYAN}scan profile{C.RESET}")
        print(f"    {C.CYAN}[1]{C.RESET} top 100 ports       {C.DIM}-T4 (aggressive){C.RESET}")
        print(f"    {C.CYAN}[2]{C.RESET} top 1000 ports      {C.DIM}-T4{C.RESET}")
        print(f"    {C.CYAN}[3]{C.RESET} full 1-65535        {C.DIM}-T4{C.RESET}")
        print(f"    {C.CYAN}[4]{C.RESET} custom range        {C.DIM}-T4{C.RESET}")
        print(f"    {C.CYAN}[5]{C.RESET} custom list         {C.DIM}-T4{C.RESET}")
        profile = input(f"  {C.CYAN}choice{C.RESET} [1-5, default 1] ❯ ").strip() or "1"

        if profile == '4':
            rng = input(f"  {C.CYAN}range{C.RESET} (start-end) ❯ ").strip()
            try:
                a, b = rng.split('-')
                ports = list(range(int(a), int(b) + 1))
            except Exception:
                print(f"  {C.RED}bad range{C.RESET}")
                return
        elif profile == '5':
            cs = input(f"  {C.CYAN}ports{C.RESET} (comma separated) ❯ ").strip()
            try:
                ports = [int(p.strip()) for p in cs.split(',') if p.strip()]
            except Exception:
                print(f"  {C.RED}bad port list{C.RESET}")
                return
        elif profile == '3':
            ports = list(range(1, 65536))
        elif profile == '2':
            ports = sorted(set(list(range(1, 1025)) + TOP_PORTS + [1433, 1521, 2049, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 8888, 9000, 9090, 11211, 27017]))
        else:
            ports = TOP_PORTS

        print()
        print(f"  {C.CYAN}timing{C.RESET}")
        print(f"    {C.CYAN}[1]{C.RESET} T0 paranoid     {C.DIM}(5s timeout, 5 threads){C.RESET}")
        print(f"    {C.CYAN}[2]{C.RESET} T1 sneaky       {C.DIM}(3s timeout, 20 threads){C.RESET}")
        print(f"    {C.CYAN}[3]{C.RESET} T2 polite       {C.DIM}(2s timeout, 100 threads){C.RESET}")
        print(f"    {C.CYAN}[4]{C.RESET} T3 normal       {C.DIM}(1.5s timeout, 300 threads){C.RESET}")
        print(f"    {C.CYAN}[5]{C.RESET} T4 aggressive   {C.DIM}(1s timeout, 500 threads){C.RESET} {C.GREEN}← default{C.RESET}")
        print(f"    {C.CYAN}[6]{C.RESET} T5 insane       {C.DIM}(0.5s timeout, 1000 threads){C.RESET}")
        timing = input(f"  {C.CYAN}choice{C.RESET} [1-6, default 5] ❯ ").strip() or "5"
        timing_map = {
            '1': (5.0, 5), '2': (3.0, 20), '3': (2.0, 100),
            '4': (1.5, 300), '5': (1.0, 500), '6': (0.5, 1000)
        }
        timeout_s, thread_count = timing_map.get(timing, (1.0, 500))

        ping_first = input(f"  {C.CYAN}ping sweep first to skip dead hosts?{C.RESET} [Y/n] ❯ ").strip().lower()
        do_ping = ping_first != 'n'

        # expand targets
        targets = expand_targets(target)
        if not targets:
            print(f"  {C.RED}❌ no valid targets{C.RESET}")
            return

        print()
        print(f"  {C.CYAN}targets{C.RESET}   {len(targets)} host(s)")
        print(f"  {C.CYAN}ports{C.RESET}     {len(ports):,} per host")
        print(f"  {C.CYAN}timing{C.RESET}    T{int(timing)-1} · {timeout_s}s · {thread_count} threads")
        print()

        all_results = {}
        scan_start = time.time()

        for t_idx, tgt in enumerate(targets, 1):
            print(f"  {C.BRIGHT_CYAN}[{t_idx}/{len(targets)}]{C.RESET} {tgt}")

            try:
                ip = socket.gethostbyname(tgt)
            except socket.gaierror:
                print(f"           {C.RED}❌ cannot resolve{C.RESET}")
                continue

            if do_ping and len(targets) > 1:
                alive = ping_host(ip, timeout_s)
                if not alive:
                    print(f"           {C.DIM}host appears down, skipping{C.RESET}")
                    all_results[tgt] = {"ip": ip, "alive": False, "open_ports": []}
                    continue

            open_ports = []
            last_print = [0.0]
            total = len(ports)
            done = [0]

            def scan_one(p):
                return scan_port_advanced(ip, p, timeout=timeout_s)

            with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as ex:
                futures = {ex.submit(scan_one, p): p for p in ports}
                for fut in concurrent.futures.as_completed(futures):
                    done[0] += 1
                    r = fut.result()
                    if r:
                        open_ports.append(r)

                    now = time.time()
                    if now - last_print[0] > 0.3:
                        elapsed = now - scan_start
                        rate = done[0] / (now - scan_start) if (now - scan_start) > 0 else 0
                        eta = (total - done[0]) / rate if rate > 0 else 0
                        extra = f"{rate:6.0f} p/s  open: {len(open_ports)}  ETA {int(eta)}s"
                        progress_bar(done[0], total, extra=extra)
                        last_print[0] = now

            progress_done()
            print()

            open_ports.sort()
            all_results[tgt] = {"ip": ip, "alive": True, "open_ports": open_ports}

            if open_ports:
                os_hints = guess_os(open_ports)
                if os_hints:
                    print(f"           {C.CYAN}os hints{C.RESET} {C.DIM}(not authoritative){C.RESET}")
                    for h in os_hints:
                        print(f"             {C.BRIGHT_YELLOW}·{C.RESET} {h}")
                    print()

                print(f"           {C.CYAN}{'PORT':<7} {'SERVICE':<12} {'VERSION':<26} {'BANNER':<40}{C.RESET}")
                print(f"           {C.DIM}{'─' * 7} {'─' * 12} {'─' * 26} {'─' * 40}{C.RESET}")
                for port, banner, service, version in open_ports:
                    svc = service or port_to_service(port) or "?"
                    ver = (version or "")[:26]
                    bnr = (banner or "")[:40].replace('\n', ' ').replace('\r', '')
                    print(f"           {C.BRIGHT_GREEN}{port:<7}{C.RESET} {C.YELLOW}{svc:<12}{C.RESET} {C.MAGENTA}{ver:<26}{C.RESET} {C.DIM}{bnr:<40}{C.RESET}")
                print()
            else:
                print(f"           {C.YELLOW}no open ports{C.RESET}")
                print()

        scan_elapsed = time.time() - scan_start

        # summary
        total_open = sum(len(r["open_ports"]) for r in all_results.values())
        alive_hosts = sum(1 for r in all_results.values() if r.get("alive", True))
        print(f"  {C.BRIGHT_GREEN}scan complete{C.RESET}")
        print(f"  {C.CYAN}hosts scanned{C.RESET}    {len(all_results)}")
        print(f"  {C.CYAN}hosts alive{C.RESET}      {alive_hosts}")
        print(f"  {C.CYAN}open ports{C.RESET}       {total_open}")
        print(f"  {C.CYAN}total time{C.RESET}       {scan_elapsed:.1f}s")
        print()

        # traceroute (if single target)
        if len(targets) == 1:
            print()
            trace_choice = input(f"  {C.CYAN}traceroute to target?{C.RESET} [y/N] ❯ ").strip().lower()
            if trace_choice == 'y':
                print()
                print(f"  {C.CYAN}traceroute{C.RESET}  {targets[0]} (port 80, max 20 hops)")
                print()
                hops = tcp_traceroute(targets[0], port=80, max_hops=20, timeout=2.0)
                if hops:
                    for h, ip, rtt in hops:
                        if ip == "*":
                            print(f"    {h:>2}  {C.DIM}*{C.RESET}")
                        else:
                            rtt_str = f"{rtt:.1f}ms" if rtt else ""
                            print(f"    {h:>2}  {C.BRIGHT_CYAN}{ip:<16}{C.RESET} {C.DIM}{rtt_str}{C.RESET}")
                    print()
                else:
                    print(f"    {C.YELLOW}no hops (IP_TTL not settable without root on this platform){C.RESET}")
                    print()

        # save output
        save_fmt = input(f"  {C.CYAN}save results?{C.RESET} [j=json, x=xml, n=no] ❯ ").strip().lower()
        if save_fmt in ('j', 'x'):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            if save_fmt == 'j':
                fname = f"portscan_{ts}.json"
                data = {
                    "target_raw": target,
                    "scan_time": datetime.now().isoformat(),
                    "duration_seconds": round(scan_elapsed, 2),
                    "timing_profile": f"T{int(timing)-1}",
                    "timeout": timeout_s,
                    "threads": thread_count,
                    "ports_per_host": len(ports),
                    "results": {
                        t: {
                            "ip": r["ip"],
                            "alive": r.get("alive", True),
                            "open_ports": [
                                {"port": p, "service": s, "version": v, "banner": b}
                                for p, b, s, v in r["open_ports"]
                            ]
                        }
                        for t, r in all_results.items()
                    }
                }
                with open(fname, "w") as f:
                    json.dump(data, f, indent=2)
            else:
                fname = f"portscan_{ts}.xml"
                with open(fname, "w") as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    f.write(f'<nmaprun scanner="hashbreak" args="{target}" start="{int(scan_start)}" startstr="{datetime.now().isoformat()}">\n')
                    for t, r in all_results.items():
                        f.write(f'  <host>\n    <address addr="{r["ip"]}" addrtype="ipv4"/>\n')
                        f.write(f'    <hostnames><hostname name="{t}"/></hostnames>\n')
                        f.write(f'    <ports>\n')
                        for p, b, s, v in r["open_ports"]:
                            b_esc = (b or "").replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                            f.write(f'      <port protocol="tcp" portid="{p}">\n')
                            f.write(f'        <state state="open"/>\n')
                            f.write(f'        <service name="{s or ""}" version="{v or ""}">\n')
                            if b_esc:
                                # strip newlines from banner before writing XML
                                b_clean = b_esc[:200].replace('\n', ' ').replace('\r', ' ')
                                f.write(f'          <servicefp>{b_clean}</servicefp>\n')
                            f.write(f'        </service>\n')
                            f.write(f'      </port>\n')
                        f.write(f'    </ports>\n  </host>\n')
                    f.write(f'  <runstats><finished time="{int(time.time())}"/></runstats>\n')
                    f.write('</nmaprun>\n')
            print(f"  {C.BRIGHT_GREEN}✓{C.RESET} saved: {C.CYAN}{fname}{C.RESET}")
            print()


    def tool_subdomain_enum(self):
        width = 66
        print()
        print(box_top(width))
        print(box_line(f"{C.BOLD}SUBDOMAIN ENUMERATOR{C.RESET}", width, align='center'))
        print(box_bottom(width))
        print()

        domain = input(f"  {C.CYAN}domain{C.RESET} (e.g. example.com) ❯ ").strip().lower()
        if not domain:
            print(f"  {C.YELLOW}no domain{C.RESET}")
            return
        domain = re.sub(r'^https?://', '', domain).split('/')[0]

        # check if real recon tools are available
        subfinder_ok = shutil.which('subfinder') is not None
        httpx_ok = shutil.which('httpx') is not None

        use_real = subfinder_ok and httpx_ok

        print()
        if use_real:
            print(f"  {C.BRIGHT_GREEN}⚡{C.RESET} using {C.BOLD}subfinder + httpx{C.RESET} (real passive sources)")
        else:
            missing = []
            if not subfinder_ok: missing.append("subfinder")
            if not httpx_ok: missing.append("httpx")
            print(f"  {C.YELLOW}⚠{C.RESET} {', '.join(missing)} not on PATH — using built-in wordlist")
            print(f"  {C.DIM}install: go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest{C.RESET}")
            print(f"  {C.DIM}         go install github.com/projectdiscovery/httpx/cmd/httpx@latest{C.RESET}")
        print()

        # speed mode
        speed = None
        if use_real:
            print(f"  {C.CYAN}speed{C.RESET}")
            print(f"    {C.CYAN}[1]{C.RESET} fast     {C.DIM}crtsh + hackertarget, no httpx — 30s-4min{C.RESET}")
            print(f"    {C.CYAN}[2]{C.RESET} normal   {C.DIM}3 sources + httpx probe — 1-5min{C.RESET}")
            print(f"    {C.CYAN}[3]{C.RESET} deep     {C.DIM}all 30 sources + httpx — 3-8min{C.RESET} {C.GREEN}← default{C.RESET}")
            speed = input(f"  {C.CYAN}choice{C.RESET} [1-3, default 3] ❯ ").strip() or "3"
            print()

        if use_real:
            start = time.time()

            # speed mode 1: fast — crtsh + hackertarget, no httpx
            if speed == '1':
                print(f"  {C.DIM}querying crtsh + hackertarget...{C.RESET}")
                try:
                    proc = subprocess.run(
                        ['subfinder', '-d', domain, '-silent',
                         '-sources', 'crtsh,hackertarget',
                         '-timeout', '8'],
                        capture_output=True, text=True, timeout=120
                    )
                    elapsed = time.time() - start
                    print(f"  {C.BRIGHT_GREEN}✓{C.RESET} done in {elapsed:.1f}s")
                    subs = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
                    lines = [f"https://{s}" for s in subs]
                except subprocess.TimeoutExpired:
                    print(f"  {C.RED}❌ timed out after 2 minutes{C.RESET}")
                    return
            # speed mode 2: normal — 3 sources + httpx
            elif speed == '2':
                print(f"  {C.DIM}querying crtsh + virustotal + hackertarget...{C.RESET}")
                try:
                    p1 = subprocess.Popen(
                        ['subfinder', '-d', domain, '-silent',
                         '-sources', 'crtsh,virustotal,hackertarget',
                         '-timeout', '15'],
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
                    )
                    p2 = subprocess.Popen(
                        ['httpx', '-silent', '-timeout', '5', '-threads', '50'],
                        stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
                    )
                    if p1.stdout:
                        p1.stdout.close()
                    out, _ = p2.communicate(timeout=300)
                    elapsed = time.time() - start
                    print(f"  {C.BRIGHT_GREEN}✓{C.RESET} done in {elapsed:.1f}s")
                    lines = [l.strip() for l in out.splitlines() if l.strip()]
                except subprocess.TimeoutExpired:
                    print(f"  {C.RED}❌ timed out after 3 minutes{C.RESET}")
                    p1.kill()
                    p2.kill()
                    return
            # speed mode 3: deep — all sources + httpx (default)
            else:
                print(f"  {C.DIM}querying 30+ passive sources...{C.RESET}")
                try:
                    p1 = subprocess.Popen(
                        ['subfinder', '-d', domain, '-silent'],
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
                    )
                    p2 = subprocess.Popen(
                        ['httpx', '-silent'],
                        stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
                    )
                    if p1.stdout:
                        p1.stdout.close()
                    out, _ = p2.communicate(timeout=300)
                    elapsed = time.time() - start
                    print(f"  {C.BRIGHT_GREEN}✓{C.RESET} done in {elapsed:.1f}s")
                    lines = [l.strip() for l in out.splitlines() if l.strip()]
                except subprocess.TimeoutExpired:
                    print(f"  {C.RED}❌ timed out after 5 minutes{C.RESET}")
                    p1.kill()
                    p2.kill()
                    return

            # ===== DISPLAY (runs for any speed mode) =====
            lines = [l.strip() for l in out.splitlines() if l.strip()] if 'out' in locals() else lines
            print()
            if lines:
                print(f"  {C.BRIGHT_GREEN}{C.BOLD}FOUND {len(lines)} LIVE SUBDOMAINS{C.RESET}")
                print()
                print(f"  {C.CYAN}{'URL':<70}{C.RESET}")
                print(f"  {C.DIM}{'─' * 70}{C.RESET}")
                for url in lines[:200]:
                    color = C.BRIGHT_GREEN if 'https' in url else C.YELLOW
                    print(f"  {color}{url:<70}{C.RESET}")
                if len(lines) > 200:
                    print(f"\n  {C.DIM}... and {len(lines) - 200} more{C.RESET}")
                print()

                save = input(f"  {C.CYAN}save to file?{C.RESET} [y/N] ❯ ").strip().lower()
                if save == 'y':
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"subdomains_{domain.replace('.', '_')}_{ts}.txt"
                    with open(fname, "w") as f:
                        for url in lines:
                            f.write(url + "\n")
                    print(f"  {C.BRIGHT_GREEN}✓{C.RESET} saved: {C.CYAN}{fname}{C.RESET}")
                    print()
            else:
                print(f"  {C.YELLOW}no live subdomains found{C.RESET}")
                print()

        else:
            # built-in fallback — 134-word list
            print(f"  {C.CYAN}words{C.RESET}   {len(SUBDOMAIN_WORDLIST)}")

            canary_sub = f"nonexistent-{int(time.time())}-canary-xyz"
            canary_ip = None
            try:
                canary_ip = socket.gethostbyname(f"{canary_sub}.{domain}")
                print(f"  {C.YELLOW}⚠ wildcard DNS detected{C.RESET}")
            except socket.gaierror:
                canary_ip = None
            print()

            found = []
            def check_sub(sub):
                fqdn = f"{sub}.{domain}"
                try:
                    ip = socket.gethostbyname(fqdn)
                    if canary_ip and ip == canary_ip:
                        return None
                    return (sub, ip)
                except socket.gaierror:
                    return None
                except Exception:
                    return None

            done = 0
            total = len(SUBDOMAIN_WORDLIST)
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
                futures = {ex.submit(check_sub, s): s for s in SUBDOMAIN_WORDLIST}
                for fut in concurrent.futures.as_completed(futures):
                    done += 1
                    r = fut.result()
                    if r:
                        found.append(r)
                    elapsed = time.time() - start
                    rate = done / elapsed if elapsed > 0 else 0
                    eta = (total - done) / rate if rate > 0 else 0
                    progress_bar(done, total, extra=f"{rate:5.0f} q/s  found: {len(found)}  ETA {int(eta)}s")

            progress_done()
            print()

            if found:
                found.sort()
                print(f"  {C.BRIGHT_GREEN}{C.BOLD}FOUND SUBDOMAINS{C.RESET}")
                print()
                for sub, ip in found:
                    print(f"  {C.BRIGHT_GREEN}{sub + '.' + domain:<40}{C.RESET} {C.YELLOW}{ip:<20}{C.RESET}")
                print()
            else:
                print(f"  {C.YELLOW}no subdomains found{C.RESET}")
                print()


    def tool_dir_buster(self):
        width = 66
        print()
        print(box_top(width))
        print(box_line(f"{C.BOLD}DIRECTORY BUSTER{C.RESET}", width, align='center'))
        print(box_bottom(width))
        print()
        url = input(f"  {C.CYAN}url{C.RESET} (e.g. https://example.com) ❯ ").strip()
        if not url:
            print(f"  {C.YELLOW}no url{C.RESET}")
            return
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        base = url.rstrip('/')

        print()
        print(f"  {C.CYAN}target{C.RESET}   {base}")
        print(f"  {C.CYAN}paths{C.RESET}    {len(DIR_WORDLIST)}")
        print()

        found = []

        def check_path(path):
            target = f"{base}/{path}"
            try:
                r = requests.head(target, timeout=5, allow_redirects=True)
                if r.status_code < 400:
                    return (path, r.status_code, len(r.content) if r.content else 0)
                return None
            except Exception:
                return None

        done = 0
        total = len(DIR_WORDLIST)
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            futures = {ex.submit(check_path, p): p for p in DIR_WORDLIST}
            for fut in concurrent.futures.as_completed(futures):
                done += 1
                r = fut.result()
                if r:
                    found.append(r)
                elapsed = time.time() - start
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                progress_bar(done, total, extra=f"{rate:5.0f} r/s   found: {len(found)}   ETA {int(eta)}s")

        progress_done()
        print()

        if found:
            found.sort()
            print(f"  {C.BRIGHT_GREEN}{C.BOLD}FOUND PATHS{C.RESET}")
            print()
            print(f"  {C.CYAN}{'STATUS':<8} {'SIZE':<10} {'PATH':<50}{C.RESET}")
            print(f"  {C.DIM}{'─' * 8} {'─' * 10} {'─' * 50}{C.RESET}")
            for path, code, size in found:
                color = C.BRIGHT_GREEN if code == 200 else C.YELLOW if code < 400 else C.DIM
                print(f"  {color}{code:<8}{C.RESET} {C.DIM}{size:<10}{C.RESET} {C.WHITE}{path:<50}{C.RESET}")
            print()
        else:
            print(f"  {C.YELLOW}no paths found{C.RESET}")
            print()

    # ============ TOOLKIT: HASH GENERATOR ============
    def tool_hash_generator(self):
        width = 66
        print()
        print(box_top(width))
        print(box_line(f"{C.BOLD}HASH GENERATOR{C.RESET}", width, align='center'))
        print(box_bottom(width))
        print()
        text = input(f"  {C.CYAN}text{C.RESET} ❯ ")
        if not text:
            print(f"  {C.YELLOW}no text{C.RESET}")
            return
        b = text.encode()
        print()
        print(f"  {C.CYAN}md5{C.RESET}      {C.BRIGHT_GREEN}{hashlib.md5(b).hexdigest()}{C.RESET}")
        print(f"  {C.CYAN}sha1{C.RESET}     {C.BRIGHT_GREEN}{hashlib.sha1(b).hexdigest()}{C.RESET}")
        print(f"  {C.CYAN}sha224{C.RESET}   {C.BRIGHT_GREEN}{hashlib.sha224(b).hexdigest()}{C.RESET}")
        print(f"  {C.CYAN}sha256{C.RESET}   {C.BRIGHT_GREEN}{hashlib.sha256(b).hexdigest()}{C.RESET}")
        print(f"  {C.CYAN}sha384{C.RESET}   {C.BRIGHT_GREEN}{hashlib.sha384(b).hexdigest()}{C.RESET}")
        print(f"  {C.CYAN}sha512{C.RESET}   {C.BRIGHT_GREEN}{hashlib.sha512(b).hexdigest()}{C.RESET}")
        n = ntlm_hash(text)
        if n:
            print(f"  {C.CYAN}ntlm{C.RESET}     {C.BRIGHT_GREEN}{n}{C.RESET}")
        print(f"  {C.CYAN}base64{C.RESET}   {C.BRIGHT_GREEN}{base64.b64encode(b).decode()}{C.RESET}")
        print(f"  {C.CYAN}url{C.RESET}      {C.BRIGHT_GREEN}{urllib.parse.quote(text)}{C.RESET}")
        print()

    # ============ TOOLKIT: PASSWORD STRENGTH ============
    def tool_password_strength(self):
        width = 66
        print()
        print(box_top(width))
        print(box_line(f"{C.BOLD}PASSWORD STRENGTH CHECKER{C.RESET}", width, align='center'))
        print(box_bottom(width))
        print()
        pw = input(f"  {C.CYAN}password{C.RESET} ❯ ")
        if not pw:
            print(f"  {C.YELLOW}no password{C.RESET}")
            return

        # entropy estimate
        charset = 0
        if any(c.islower() for c in pw): charset += 26
        if any(c.isupper() for c in pw): charset += 26
        if any(c.isdigit() for c in pw): charset += 10
        if any(not c.isalnum() for c in pw): charset += 33
        import math
        entropy = len(pw) * math.log2(charset) if charset > 0 else 0

        # wordlist check
        in_wordlist = False
        words = self.load_wordlist()
        if pw in words or pw.lower() in [w.lower() for w in words[:200000]]:
            in_wordlist = True

        print()
        print(f"  {C.CYAN}length{C.RESET}     {len(pw)}")
        print(f"  {C.CYAN}charset{C.RESET}    {charset} symbols")
        print(f"  {C.CYAN}entropy{C.RESET}    {entropy:.1f} bits")

        if in_wordlist:
            print(f"  {C.BRIGHT_RED}⚠ found in wordlist — common password{C.RESET}")
        else:
            print(f"  {C.BRIGHT_GREEN}✓ not in top wordlist{C.RESET}")

        # rating
        if in_wordlist or entropy < 30:
            rating = f"{C.BRIGHT_RED}WEAK{C.RESET}"
        elif entropy < 50:
            rating = f"{C.YELLOW}MODERATE{C.RESET}"
        elif entropy < 70:
            rating = f"{C.BRIGHT_GREEN}STRONG{C.RESET}"
        else:
            rating = f"{C.BRIGHT_GREEN}{C.BOLD}VERY STRONG{C.RESET}"

        print()
        print(f"  {C.CYAN}rating{C.RESET}     {rating}")
        print()

    # ============ TOOLKIT: ENCODERS ============
    def tool_encoders(self):
        width = 66
        print()
        print(box_top(width))
        print(box_line(f"{C.BOLD}ENCODER / DECODER{C.RESET}", width, align='center'))
        print(box_bottom(width))
        print()
        print(f"  {C.CYAN}[1]{C.RESET} base64 encode")
        print(f"  {C.CYAN}[2]{C.RESET} base64 decode")
        print(f"  {C.CYAN}[3]{C.RESET} url encode")
        print(f"  {C.CYAN}[4]{C.RESET} url decode")
        print(f"  {C.CYAN}[5]{C.RESET} hex encode")
        print(f"  {C.CYAN}[6]{C.RESET} hex decode")
        print(f"  {C.CYAN}[7]{C.RESET} rot13")
        print(f"  {C.CYAN}[8]{C.RESET} binary")
        print()
        choice = input(f"  {C.BRIGHT_CYAN}❯{C.RESET} ").strip()
        text = input(f"  {C.CYAN}input{C.RESET} ❯ ")

        try:
            if choice == '1':
                print(f"\n  {C.BRIGHT_GREEN}{base64.b64encode(text.encode()).decode()}{C.RESET}\n")
            elif choice == '2':
                print(f"\n  {C.BRIGHT_GREEN}{base64.b64decode(text).decode(errors='replace')}{C.RESET}\n")
            elif choice == '3':
                print(f"\n  {C.BRIGHT_GREEN}{urllib.parse.quote(text)}{C.RESET}\n")
            elif choice == '4':
                print(f"\n  {C.BRIGHT_GREEN}{urllib.parse.unquote(text)}{C.RESET}\n")
            elif choice == '5':
                print(f"\n  {C.BRIGHT_GREEN}{text.encode().hex()}{C.RESET}\n")
            elif choice == '6':
                print(f"\n  {C.BRIGHT_GREEN}{bytes.fromhex(text).decode(errors='replace')}{C.RESET}\n")
            elif choice == '7':
                import codecs
                print(f"\n  {C.BRIGHT_GREEN}{codecs.encode(text, 'rot_13')}{C.RESET}\n")
            elif choice == '8':
                print(f"\n  {C.BRIGHT_GREEN}{' '.join(format(b, '08b') for b in text.encode())}{C.RESET}\n")
        except Exception as e:
            print(f"\n  {C.RED}error: {e}{C.RESET}\n")

    # ============ BATCH, RESULTS, EXPORT ============
    def batch_crack(self, file_path):
        """subprocess-per-hash — each hash runs in its own isolated Python process.
        avoids multiprocessing pool state corruption across many hashes."""
        file_path = os.path.expanduser(file_path)
        try:
            with open(file_path, 'r') as f:
                hashes = [h.strip() for h in f.readlines() if h.strip()]
        except FileNotFoundError:
            print(f"  {C.RED}❌ File not found: {file_path}{C.RESET}")
            return
        if not hashes:
            print(f"  {C.RED}❌ No hashes in file{C.RESET}")
            return

        total = len(hashes)
        print()
        print(f"  {C.BRIGHT_CYAN}{C.BOLD}BATCH CRACKING{C.RESET}  {C.DIM}{total} hashes{C.RESET}")
        print()

        start_time = time.time()
        self.cracked_count = 0
        self.failed_count = 0
        self.results = []

        # process hashes in parallel — N single-core subprocesses at once
        import concurrent.futures
        parallelism = 4   # 4 hashes at a time, each single-core

        def crack_one(hash_str):
            try:
                env = os.environ.copy()
                env['HASHBREAK_NO_POOL'] = '1'
                proc = subprocess.run(
                    [sys.executable, __file__, hash_str],
                    capture_output=True, text=True, timeout=900, env=env
                )
                output = proc.stdout
            except subprocess.TimeoutExpired:
                return (hash_str, None, 'timeout')
            except Exception as e:
                return (hash_str, None, f'error: {e}')

            hash_type = self.detect_hash_type(hash_str) or 'Unknown'
            if "✅" in output and "CRACKED" in output:
                for line in output.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("password"):
                        parts = stripped.split(None, 1)
                        if len(parts) == 2:
                            return (hash_str, parts[1].strip(), hash_type)
            return (hash_str, None, hash_type)

        print(f"  {C.DIM}parallel batch: {parallelism} hashes at a time, single-core each{C.RESET}")
        print()

        done_count = [0]
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallelism) as ex:
            futures = {ex.submit(crack_one, h): h for h in hashes}
            for fut in concurrent.futures.as_completed(futures):
                hash_str, password, hash_type = fut.result()
                done_count[0] += 1
                idx = done_count[0]

                if password:
                    self.cracked_count += 1
                    self.results.append({
                        'hash': hash_str,
                        'password': password,
                        'method': 'batch-subprocess',
                        'type': hash_type
                    })
                    print(f"  {C.CYAN}[{idx}/{total}]{C.RESET} {C.DIM}{hash_str[:40]}{C.RESET}")
                    print(f"           {C.BRIGHT_GREEN}✅ {password}{C.RESET}")
                else:
                    self.failed_count += 1
                    self.results.append({
                        'hash': hash_str,
                        'password': None,
                        'method': 'Failed',
                        'type': hash_type
                    })
                    print(f"  {C.CYAN}[{idx}/{total}]{C.RESET} {C.DIM}{hash_str[:40]}{C.RESET}")
                    print(f"           {C.BRIGHT_RED}❌ not cracked{C.RESET}")

        elapsed = time.time() - start_time
        print()
        print(f"  {C.CYAN}Total hashes{C.RESET}    {total}")
        print(f"  {C.BRIGHT_GREEN}Cracked{C.RESET}         {self.cracked_count} ✅")
        print(f"  {C.BRIGHT_RED}Failed{C.RESET}          {self.failed_count} ❌")
        print(f"  {C.CYAN}Success rate{C.RESET}    {(self.cracked_count/total*100):.1f}%")
        print(f"  {C.CYAN}Time{C.RESET}            {elapsed:.2f}s")
        print()

    def display_results(self, filter_type=None):
        if not self.results:
            print(f"  {C.YELLOW}No results to display{C.RESET}")
            return
        if filter_type == 'cracked':
            filtered = [r for r in self.results if r['password']]
        elif filter_type == 'failed':
            filtered = [r for r in self.results if not r['password']]
        else:
            filtered = self.results
        print()
        print(f"  {C.BRIGHT_CYAN}{C.BOLD}RESULTS{C.RESET}  {C.DIM}({len(filtered)} of {len(self.results)}){C.RESET}")
        print()
        if len(filtered) > 0:
            for idx, result in enumerate(filtered[:50], 1):
                pw = result['password'] or "—"
                if result['password']:
                    pw_color = C.BRIGHT_GREEN
                else:
                    pw_color = C.DIM
                    pw = "not cracked"
                hash_text = (result['hash'][:28] + "...") if len(result['hash']) > 30 else result['hash']
                print(f"  {C.DIM}{idx:<4}{C.RESET} {C.WHITE}{hash_text:<32}{C.RESET} {pw_color}{pw:<25}{C.RESET} {C.YELLOW}{result['type']:<12}{C.RESET}")
            if len(filtered) > 50:
                print(f"\n  {C.DIM}... and {len(filtered) - 50} more{C.RESET}")
        print()

    def export_results(self, format_type='json'):
        if not self.results:
            print(f"  {C.YELLOW}No results to export{C.RESET}")
            return
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if format_type == 'json':
            filename = f'hashbreak_modern_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump({
                    'tool': 'HashBreak v7.9',
                    'built_by': 'Maverick',
                    'timestamp': datetime.now().isoformat(),
                    'results': self.results
                }, f, indent=2)
        elif format_type == 'csv':
            filename = f'hashbreak_modern_{timestamp}.csv'
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['hash', 'password', 'method', 'type'])
                writer.writeheader()
                writer.writerows(self.results)
        print(f"  {C.BRIGHT_GREEN}✓{C.RESET} exported: {C.CYAN}{filename}{C.RESET}")
        print()

    def check_dependencies(self):
        width = 66
        print(box_top(width))
        print(box_line(f"{C.BOLD}SYSTEM CHECK{C.RESET}", width, align='center'))
        print(box_mid(width))
        for dep, ok in [('scrypt', SCRYPT_AVAILABLE), ('bcrypt', BCRYPT_AVAILABLE), ('requests', True)]:
            mark = f"{C.BRIGHT_GREEN}✓{C.RESET}" if ok else f"{C.BRIGHT_RED}✗{C.RESET}"
            print(box_line(f"{mark} {dep}", width))
        print(box_mid(width))
        print(box_line(f"{C.BRIGHT_GREEN}✓{C.RESET} {self.workers} CPU cores", width))
        print(box_line(f"{C.BRIGHT_GREEN}✓{C.RESET} 13 hash families  ·  5 attack types", width))
        print(box_line(f"{C.BRIGHT_GREEN}✓{C.RESET} 5 recon / utility tools", width))
        print(box_bottom(width))
        print()

    def show_menu(self):
        width = 66
        print(box_top(width))
        print(box_line(f"{C.BRIGHT_CYAN}{C.BOLD}MAIN MENU{C.RESET}", width, align='center'))
        print(box_mid(width))
        print(box_line(f"{C.MAGENTA}{C.BOLD}CRACKING{C.RESET}", width))
        items_crack = [
            ("1", "Crack single hash"),
            ("2", "Batch crack (from file)"),
            ("3", "View results"),
            ("4", "Filter results"),
            ("5", "Export results"),
            ("6", "Hash type info"),
            ("7", "Settings"),
            ("8", "Exit"),
            ("9", "Mask attack"),
            ("10", "Hybrid attack (wordlist + mask)"),
        ]
        for num, label in items_crack:
            print(box_line(f"{C.BRIGHT_CYAN}[{num}]{C.RESET}  {label}", width))

        print(box_mid(width))
        print(box_line(f"{C.MAGENTA}{C.BOLD}TOOLKIT{C.RESET}", width))
        items_tools = [
            ("11", "Port scanner"),
            ("12", "Subdomain enumerator"),
            ("13", "Directory buster"),
            ("14", "Hash generator"),
            ("15", "Password strength checker"),
            ("16", "Encoder / decoder"),
        ]
        for num, label in items_tools:
            print(box_line(f"{C.BRIGHT_CYAN}[{num}]{C.RESET}  {label}", width))

        print(box_bottom(width))

    def run_interactive(self):
        self.display_banner()
        self.check_dependencies()

        while True:
            self.show_menu()
            choice = input(f"\n  {C.BRIGHT_CYAN}❯{C.RESET} ").strip()

            if choice == '1':
                h = input(f"  {C.CYAN}hash{C.RESET} ❯ ").strip()
                if not h: continue
                print(f"\n  {C.CYAN}detected{C.RESET}  {C.BOLD}{self.detect_hash_type(h)}{C.RESET}\n")
                r = self.crack_single(h)
                if r:
                    big_success("CRACKED")
                    print(f"  {C.CYAN}password{C.RESET}  {C.BRIGHT_GREEN}{C.BOLD}{r['password']}{C.RESET}")
                    print(f"  {C.CYAN}method{C.RESET}    {r['method']}")
                    print(f"  {C.CYAN}type{C.RESET}      {r['type']}\n")
                else:
                    big_failure(f"NOT CRACKED  ({self.detect_hash_type(h)})")

            elif choice == '2':
                fp = input(f"  {C.CYAN}file path{C.RESET} ❯ ").strip()
                if fp: self.batch_crack(fp)

            elif choice == '3': self.display_results()
            elif choice == '4':
                print(f"  {C.CYAN}[1]{C.RESET} cracked  {C.CYAN}[2]{C.RESET} failed  {C.CYAN}[3]{C.RESET} all")
                fc = input(f"  {C.BRIGHT_CYAN}❯{C.RESET} ").strip()
                self.display_results('cracked' if fc == '1' else 'failed' if fc == '2' else None)

            elif choice == '5':
                print(f"  {C.CYAN}[1]{C.RESET} JSON  {C.CYAN}[2]{C.RESET} CSV")
                ec = input(f"  {C.BRIGHT_CYAN}❯{C.RESET} ").strip()
                if ec == '1': self.export_results('json')
                elif ec == '2': self.export_results('csv')

            elif choice == '6':
                width = 66
                print()
                print(box_top(width))
                print(box_line(f"{C.BOLD}SUPPORTED HASH TYPES{C.RESET}", width, align='center'))
                print(box_mid(width))
                print(box_line(f"{C.BRIGHT_GREEN}✓{C.RESET} MD5, SHA1, SHA224, SHA256, SHA384, SHA512", width))
                print(box_line(f"{C.BRIGHT_GREEN}✓{C.RESET} PBKDF2, scrypt, bcrypt, phpass", width))
                print(box_line(f"{C.BRIGHT_GREEN}✓{C.RESET} NTLM, LM (Windows)", width))
                print(box_line(f"{C.BRIGHT_GREEN}✓{C.RESET} MySQL41, MySQL (pre-4.1)", width))
                print(box_line(f"{C.BRIGHT_GREEN}✓{C.RESET} WPA-PMKID (WiFi .hc22000)", width))
                print(box_bottom(width))
                print()

            elif choice == '7':
                print(f"  debug: {C.BOLD}{'ON' if self.debug_mode else 'OFF'}{C.RESET}")
                if input(f"  {C.CYAN}toggle? (y/n){C.RESET} ❯ ").strip().lower() == 'y':
                    self.debug_mode = not self.debug_mode
                print()

            elif choice == '8':
                print(f"\n  {C.BRIGHT_GREEN}{C.BOLD}👋 Goodbye, Maverick.{C.RESET}\n")
                break

            elif choice == '9':
                h = input(f"  {C.CYAN}hash{C.RESET} ❯ ").strip()
                if not h: continue
                print(f"\n  {C.DIM}?l lowercase  ?u uppercase  ?d digits  ?s symbols  ?a any{C.RESET}\n")
                mask = input(f"  {C.CYAN}mask{C.RESET} ❯ ").strip()
                if not mask: continue
                r = self.crack_mask(h, mask)
                if r:
                    big_success("CRACKED")
                    print(f"  {C.CYAN}password{C.RESET}  {C.BRIGHT_GREEN}{C.BOLD}{r}{C.RESET}\n")
                else:
                    big_failure("NOT CRACKED")

            elif choice == '10':
                h = input(f"  {C.CYAN}hash{C.RESET} ❯ ").strip()
                if not h: continue
                mask = input(f"  {C.CYAN}mask{C.RESET} ❯ ").strip()
                if not mask: continue
                mode_in = input(f"  {C.CYAN}mode{C.RESET} [suffix/prefix] ❯ ").strip().lower()
                mode = 'prefix' if mode_in.startswith('p') else 'suffix'
                lim = input(f"  {C.CYAN}limit words{C.RESET} [empty = all] ❯ ").strip()
                try: limit_words = int(lim) if lim else None
                except ValueError: limit_words = None
                r = self.crack_hybrid(h, mask, mode=mode, limit_words=limit_words)
                if r:
                    big_success("CRACKED")
                    print(f"  {C.CYAN}password{C.RESET}  {C.BRIGHT_GREEN}{C.BOLD}{r}{C.RESET}\n")
                else:
                    big_failure("NOT CRACKED")

            elif choice == '11': self.tool_port_scan()
            elif choice == '12': self.tool_subdomain_enum()
            elif choice == '13': self.tool_dir_buster()
            elif choice == '14': self.tool_hash_generator()
            elif choice == '15': self.tool_password_strength()
            elif choice == '16': self.tool_encoders()

            else:
                print(f"  {C.RED}invalid choice{C.RESET}")


def main():
    hb = HashBreakModern()
    if len(sys.argv) > 1:
        hb.display_banner()
        r = hb.crack_single(sys.argv[1])
        if r:
            big_success("CRACKED")
            print(f"  {C.CYAN}password{C.RESET}  {C.BRIGHT_GREEN}{C.BOLD}{r['password']}{C.RESET}\n")
        else:
            big_failure("NOT CRACKED")
    else:
        hb.run_interactive()


if __name__ == '__main__':
    main()
