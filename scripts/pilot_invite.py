"""Prepare an invitation digest locally; does not activate access or contact a service."""
import argparse
from datetime import datetime, timezone, timedelta
import getpass
import hashlib
import hmac
import json
import re


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--subject',required=True,help='Pseudonymous pilot user ID')
    parser.add_argument('--days',type=int,default=14,help='Invitation lifetime (1-90 days)')
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',args.subject) or not 1<=args.days<=90:
        parser.error('Use a pseudonymous ID and an invitation lifetime of 1-90 days.')
    code=getpass.getpass('Private invitation code (at least 32 random characters): ')
    confirmation=getpass.getpass('Confirm private invitation code: ')
    if not 32<=len(code)<=200 or not hmac.compare_digest(code,confirmation):
        parser.error('Codes must match and contain 32-200 characters.')
    expiry=(datetime.now(timezone.utc)+timedelta(days=args.days)).isoformat(timespec='seconds')
    print(json.dumps({args.subject:{'sha256':hashlib.sha256(code.encode()).hexdigest(),
                                    'expires_at':expiry}},indent=2))


if __name__=='__main__': main()
