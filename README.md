# Secure Notes — a deliberately vulnerable Django application

Course project for **Cyber Security Base VII**.

A small note-keeping website: you log in, write private notes, edit your
profile, and staff members get an overview page. The security flaws are 
made on purpose for the course project

**OWASP list used: [OWASP Top 10 – 2021](https://owasp.org/Top10/).**

The flaws, their effects and their fixes are described in a separate essay.
This file only covers installation and where to find things in the code.

---

## Installation

Requires **Python 3.10+**. Django is the only dependency.

### Linux / macOS

```bash
git clone https://github.com/doomwall/Cyber-Security-Project---VII.git
cd Cyber-Security-Project---VII

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

./run.sh
```

### Windows (PowerShell)

```powershell
git clone https://github.com/doomwall/Cyber-Security-Project---VII.git
cd Cyber-Security-Project---VII

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

.\run.ps1
```

Then open **http://127.0.0.1:8000/**.

### The run script

`run.sh` / `run.ps1` **deletes and rebuilds the database on every start**, then
seeds it and launches the development server. It also prints which password
hasher is currently active, so you can see at a glance whether a flaw is
switched on.

The reset is deliberate. Passwords are hashed with whichever algorithm is
active in `settings.py` at the moment they are written, so after toggling the
cryptography flaw on or off the old hashes in the database can no longer be
verified and nobody would be able to log in. Rebuilding on every start keeps
the stored data consistent with the code, and means **the application works
both before and after every fix**.

Options:

| Command | Effect |
| --- | --- |
| `./run.sh` | reset the database, seed it, start the server |
| `./run.sh --keep` | keep the existing database (no reset, no seed) |
| `./run.sh 8080` | run on a different port |

On Windows the equivalents are `.\run.ps1`, `.\run.ps1 -Keep` and
`.\run.ps1 8080`.

---

## Demo accounts

Created by `manage.py seed`. All three share the password **`password123`**.

| Username | Staff? | Role in the demos |
| --- | --- | --- |
| `alice` | no | the "attacker" in most demos |
| `bob` | no | the victim, owns the notes worth stealing |
| `admin` | yes | can legitimately see the admin panel |

Note ids are **pinned** by the seed command so that URL-based demos always work:

| Note id | Owner | Title |
| --- | --- | --- |
| 1 | alice | Alice shopping list |
| 2 | alice | Alice diary |
| 3 | bob | Bob bank details |
| 4 | bob | Bob holiday plans |
| 5 | admin | Admin todo |

---

## Pages

| URL | Who should be able to use it |
| --- | --- |
| `/` | anyone — login page |
| `/register/` | anyone — create an account |
| `/home/` | logged-in users |
| `/notes/` | logged-in users, shows only their own notes |
| `/notes/new/` | logged-in users |
| `/notes/<id>/` | **only the owner of that note** |
| `/notes/<id>/delete/` | **only the owner of that note**, POST only |
| `/profile/` | logged-in users, own profile only |
| `/admin-panel/` | **staff only** |
| `/logout/` | logged-in users, POST |

---

## Where the flaws are

Each vulnerable spot is marked with a `FLAW n` comment block

To repair a flaw, **uncomment the SECURE line(s) and comment out the
VULNERABLE line(s)**, then restart with `./run.sh` (or `.\run.ps1`).

List every flaw location with:

```bash
grep -rn "FLAW " cyberproject/
```

| # | OWASP 2021 category | File | Function / setting |
| --- | --- | --- | --- |
| 1 | A01:2021 – Broken Access Control | `cyberproject/notes/views.py` | `note_detail()` |
| 2 | A02:2021 – Cryptographic Failures | `cyberproject/accounts/hashers.py`, `cyberproject/cyberproject/settings.py` | `UnsaltedMD5PasswordHasher`, `PASSWORD_HASHERS` |
| 3 | A03:2021 – Injection | `cyberproject/notes/views.py` | `note_create()` |
| 4 | A07:2021 – Identification and Authentication Failures | `cyberproject/accounts/views.py` | `register_view()` |
| 5 | A09:2021 – Security Logging and Monitoring Failures | `cyberproject/accounts/views.py` | `login_view()` |

Browser screenshots of each flaw before and after its fix are in
[`screenshots/`](screenshots/), named `flaw-<n>-before-<k>.png` and
`flaw-<n>-after-<k>.png`.