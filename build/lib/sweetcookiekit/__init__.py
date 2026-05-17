import subprocess
import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class CookieRecord:
    domain: str
    name: str
    value: str
    path: str
    expires: Optional[str]
    isSecure: bool
    isHTTPOnly: bool

@dataclass
class CookieStore:
    browser: str
    browserDisplayName: str
    profileId: str
    profileName: str
    kind: str
    label: str
    records: List[CookieRecord]

def list_browsers(cli_path: str = "SweetCookieCLI") -> List[Dict[str, str]]:
    """
    List all supported browser identifiers.
    Returns a list of dicts with 'id' and 'displayName'.
    """
    cmd = [cli_path, "--list-browsers"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    browsers = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            browsers.append({"id": parts[0], "displayName": parts[1]})
    return browsers

def list_stores(
    browsers: Optional[List[str]] = None,
    all_browsers: bool = False,
    profile: Optional[str] = None,
    kind: Optional[str] = None,
    cli_path: str = "SweetCookieCLI"
) -> List[Dict[str, str]]:
    """
    List matching browser stores (profiles).
    Returns a list of dicts with store details.
    """
    cmd = [cli_path, "--list-stores"]

    if all_browsers:
        cmd.append("--all-browsers")
    elif browsers:
        cmd.extend(["--browser", ",".join(browsers)])

    if profile:
        cmd.extend(["--profile", profile])

    if kind:
        cmd.extend(["--kind", kind])

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    stores = []
    for line in result.stdout.strip().split('\n'):
        if not line or line.startswith("warning:"):
            continue
        parts = line.split('\t')
        if len(parts) >= 5:
            stores.append({
                "browser": parts[0],
                "profileName": parts[1],
                "profileId": parts[2],
                "kind": parts[3],
                "label": parts[4]
            })
    return stores

def get_cookies(
    domains: Optional[List[str]] = None,
    domain_match: Optional[str] = None,
    browsers: Optional[List[str]] = None,
    all_browsers: bool = False,
    profile: Optional[str] = None,
    kind: Optional[str] = None,
    include_expired: bool = False,
    cli_path: str = "SweetCookieCLI"
) -> List[CookieStore]:
    """
    Extract cookies from macOS browsers using SweetCookieCLI.
    """
    cmd = [cli_path, "--format", "json"]

    if domains:
        cmd.extend(["--domains", ",".join(domains)])

    if domain_match:
        cmd.extend(["--domain-match", domain_match])

    if all_browsers:
        cmd.append("--all-browsers")
    elif browsers:
        cmd.extend(["--browser", ",".join(browsers)])

    if profile:
        cmd.extend(["--profile", profile])

    if kind:
        cmd.extend(["--kind", kind])

    if include_expired:
        cmd.append("--include-expired")

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Check if stdout is empty, return empty list
    if not result.stdout.strip():
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Sometimes CLI outputs warnings to stdout before json or fails to output json cleanly.
        # Fallback empty list if invalid json. (Though CLI uses stderr for warnings).
        return []

    parsed_stores = []
    for store_data in data.get("stores", []):
        records = [
            CookieRecord(
                domain=r["domain"],
                name=r["name"],
                value=r["value"],
                path=r["path"],
                expires=r.get("expires"),
                isSecure=r["isSecure"],
                isHTTPOnly=r["isHTTPOnly"]
            )
            for r in store_data.get("records", [])
        ]

        parsed_stores.append(
            CookieStore(
                browser=store_data["browser"],
                browserDisplayName=store_data["browserDisplayName"],
                profileId=store_data["profileId"],
                profileName=store_data["profileName"],
                kind=store_data["kind"],
                label=store_data["label"],
                records=records
            )
        )

    return parsed_stores
