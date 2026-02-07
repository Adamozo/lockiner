#!/usr/bin/env python3
"""Generate VAPID keys for Web Push notifications.

Run once, then add the output to your .env file.

Usage:
    python scripts/generate_vapid_keys.py
"""

from py_vapid import Vapid

vapid = Vapid()
vapid.generate_keys()

print("Add these to your .env file:\n")
print(f"VAPID_PRIVATE_KEY={vapid.private_pem()}")
print(f"VAPID_PUBLIC_KEY={vapid.public_key_urlsafe_base64()}")
print(f"VAPID_CONTACT_EMAIL=mailto:your-email@example.com")
