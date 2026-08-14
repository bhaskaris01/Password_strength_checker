# Password Strength Checker

Python (Flask) + SQLite web app that checks password strength in real time.

## How to run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the app:
   ```
   python app.py
   ```
3. Open your browser at `http://127.0.0.1:5000`

The SQLite database (`passwords.db`) is created automatically on first run,
seeded with 20 common/leaked passwords.

## Project structure

```
password_strength_checker/
├── app.py                # Flask backend + strength logic + SQLite
├── requirements.txt
├── templates/
│   └── index.html        # Frontend form
└── static/
    ├── style.css          # Styling + strength bar
    └── script.js          # Real-time fetch() calls to /check
```

## How it works (viva-ready explanation)

1. User types a password into the HTML form.
2. JavaScript sends it to the Flask route `/check` via a `POST` request
   (using `fetch`), with a short debounce so it doesn't fire on every keystroke.
3. Flask runs 5 regex-based checks: length ≥ 8, uppercase, lowercase,
   digit, special character. Each passed check = 1 point (max score 5).
4. Flask queries the SQLite `common_passwords` table. If the password is
   found there, it is force-classified as **Weak**, even if it scores well.
5. Score → classification: 0–2 = Weak, 3–4 = Medium, 5 = Strong.
6. Flask returns the result as JSON; JavaScript updates the strength bar,
   label, and checklist on the page without reloading it.

## Possible improvements to mention if asked

- Hash passwords with bcrypt before storing anything (this app doesn't
  store user passwords — it only checks strength).
- Use a larger breached-password list, e.g. the "Have I Been Pwned" API.
- Add entropy-based scoring instead of simple rule counting.
