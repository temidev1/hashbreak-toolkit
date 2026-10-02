# HashBreak Toolkit

[![tests](https://github.com/temidev1/hashbreak-toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/temidev1/hashbreak-toolkit/actions/workflows/tests.yml)

Modern hash cracker + reconnaissance toolkit for Android / Termux.
Built by Maverick.

## Features

- 13 hash families: MD5, SHA1, SHA224, SHA256, SHA384, SHA512, PBKDF2, scrypt, bcrypt, NTLM, LM, MySQL41, MySQL, WPA-PMKID
- 5 attack types: dictionary, rules, mask, hybrid, online lookup
- Parallel batch mode (4 workers)
- Port scanner: CIDR, timing profiles, traceroute, banner grab, XML output
- Subdomain enum: subfinder + httpx integration
- Dir buster, hash generator, password strength, encoders

## Install

**Android / Termux (primary platform):**

    git clone https://github.com/temidev1/hashbreak-toolkit.git
    cd hashbreak-toolkit
    pkg install python git -y
    pip install -r requirements.txt

**Other platforms:**

The Python code is portable — it runs anywhere Python 3.10+ runs.

    git clone https://github.com/temidev1/hashbreak-toolkit.git
    cd hashbreak-toolkit
    pip install -r requirements.txt

- **iPhone / iPad:** iSH or a-Shell (unofficial, may be slow)
- **Linux:** run directly with native Python 3.10+
- **macOS:** run directly with native Python 3.10+
- **Windows:** WSL, or native Python 3.10+

For reproducible installs (exact versions tested by the author):

    pip install -r requirements.lock.txt

## Usage

    python hashbreak.py

Pick options 1-16 from the menu.

## Test result

**Benchmark:** 20 real breached MD5 hashes from SecLists leaked-database samples.

| | |
|---|---|
| Hardware | Android phone, Snapdragon 7-series, 8 cores |
| Platform | Termux (Android 14) |
| Python | 3.14 |
| Hash type | MD5 |
| Hashes | 20 |
| Wordlist | top 100k rockyou + top 100k md5decryptor-uk |
| Attack mode | dictionary (fast rules) |
| Workers | 4 parallel single-core subprocesses |
| **Time** | **186.93s** |
| **Crack rate** | **100%** |

Note: 100% is specific to this wordlist/dump pairing. Real-world rates vary
with wordlist coverage, password strength, and hash type.


## Contact

- GitHub: [@temidev1](https://github.com/temidev1)
- Issues: https://github.com/temidev1/hashbreak-toolkit/issues
- Discussions: https://github.com/temidev1/hashbreak-toolkit/discussions

For bug reports and feature requests, open an issue.
For general questions, use Discussions.

## License

MIT
