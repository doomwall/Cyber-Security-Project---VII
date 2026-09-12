# Secure Notes — a deliberately vulnerable Django application

Course project for **Cyber Security Base — Project I**.

A small note-keeping website: you log in, write private notes, edit your
profile, and staff members get an overview page. It is also, on purpose,
riddled with security flaws.

**OWASP list used: [OWASP Top 10 – 2021](https://owasp.org/Top10/).**
Only the 2021 list is used; the 2017 and 2025 lists are not mixed in.

The flaws, their effects and their fixes are described in a separate essay.
This file only covers installation and where to find things in the code.

> ### Warning
> This application contains **intentional, working security vulnerabilities**.
> Run it only locally (`127.0.0.1`) and never expose it to a network or deploy
> it anywhere public. Do not reuse any of this code in a real project.

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

cd cyberproject
python3 manage.py migrate
python3 manage.py seed
python3 manage.py runserver
```

### Windows (PowerShell)

```powershell
git clone https://github.com/doomwall/Cyber-Security-Project---VII.git
cd Cyber-Security-Project---VII

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd cyberproject
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Then open **http://127.0.0.1:8000/**.

The database (`db.sqlite3`) is not committed — `migrate` creates it and `seed`
fills it with the demo data below. `seed` is safe to re-run at any time; it
resets the demo users and notes back to a known state.

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

Every flaw and its fix live **in the same version of the code** — no git
branches and no separate releases. Each vulnerable spot is marked with a
`FLAW n` comment block naming its OWASP category and CWE, and looks like this:

```python
# --- SECURE version: ...explanation...
# note = get_object_or_404(Note, pk=note_id, owner=request.user)

# --- VULNERABLE version: ...explanation...
note = get_object_or_404(Note, pk=note_id)
```

To repair a flaw, **uncomment the SECURE line(s) and comment out the
VULNERABLE line(s)**. The application works correctly in both states.

List every flaw location with:

```bash
grep -rn "FLAW " cyberproject/
```

| # | OWASP 2021 category | File | Function / setting |
| --- | --- | --- | --- |
| 1 | A01:2021 – Broken Access Control | `cyberproject/notes/views.py` | `note_detail()` |
| 2 | A02:2021 – Cryptographic Failures | _not implemented yet_ | |
| 3 | A03:2021 – Injection | _not implemented yet_ | |
| 4 | A07:2021 – Identification and Authentication Failures | _not implemented yet_ | |
| 5 | A09:2021 – Security Logging and Monitoring Failures | _not implemented yet_ | |

Browser screenshots of each flaw before and after its fix are in
[`screenshots/`](screenshots/), named `flaw-<n>-before-<k>.png` and
`flaw-<n>-after-<k>.png`.

---

## Project structure

```
cyberproject/
├── manage.py
├── cyberproject/              # project configuration
│   ├── settings.py
│   └── urls.py                # top-level URL routing
├── accounts/                  # login, profile, admin panel
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── management/commands/
│   │   └── seed.py            # creates the demo users and notes
│   └── templates/
│       ├── base.html
│       └── accounts/
└── notes/                     # the notes feature (user-owned objects)
    ├── models.py              # Note: owner, title, body
    ├── views.py
    ├── urls.py
    └── templates/notes/
```
