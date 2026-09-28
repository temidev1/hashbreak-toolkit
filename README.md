# HashBreak Toolkit

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

    pkg install python git -y
    pip install requests bcrypt pycryptodome scrypt

## Usage

    python hashbreak.py

Pick options 1-16 from the menu.

## Test result

20 real breached MD5 hashes cracked in 187 seconds. 100% success rate.

## License

MIT
