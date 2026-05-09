"""
profiles.py — Profile manager for the COMPOUND_APPROACH Portal.

Profiles define who is "driving" the portal. Each profile has its own
vault folder suggestion, accent color, and status message.
"""

import json
from pathlib import Path

DEFAULT_PROFILES = {
    "profiles": {
        "joseph": {
            "name": "Joseph Harris",
            "email": "joseph.harris.tx@gmail.com",
            "vault_open": "01_JOSEPH",
            "accent": "#88c0d0",
            "status": "Building the bridge."
        },
        "trey": {
            "name": "Trey",
            "email": None,
            "vault_open": "02_TREY",
            "accent": "#a3be8c",
            "status": "Operator mode."
        },
        "shared": {
            "name": "Shared",
            "email": None,
            "vault_open": "03_SHARED",
            "accent": "#ebcb8b",
            "status": "Collaborative space."
        }
    }
}


def load_profiles(data_dir: Path) -> dict:
    path = data_dir / "profiles.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    save_profiles(data_dir, DEFAULT_PROFILES)
    return DEFAULT_PROFILES


def save_profiles(data_dir: Path, profiles: dict):
    path = data_dir / "profiles.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)


def get_profile(data_dir: Path, profile_key: str) -> dict | None:
    profiles = load_profiles(data_dir)
    return profiles.get("profiles", {}).get(profile_key)


def list_profile_keys(data_dir: Path) -> list[str]:
    profiles = load_profiles(data_dir)
    return list(profiles.get("profiles", {}).keys())
