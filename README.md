<div align="center">
<h1>ATM Simulator</h1>
<p>
  <img src="https://img.shields.io/badge/Python-3.x-14354C?style=flat&logo=python&logoColor=white" alt="Python 3.x" />
  <img src="https://img.shields.io/badge/Dependencies-None-brightgreen?style=flat" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/Interface-CLI-blue?style=flat" alt="CLI" />
</p>
<p><i>A command-line ATM simulator in Python, built to practice safe money handling, input validation, and basic fraud-detection logic.</i></p>
</div>

---

## What this is

A simple ATM you run in your terminal — log in with a PIN, check your balance, deposit, withdraw, and view your transaction history. Built using only the Python standard library, with a few things done properly on purpose:

- **Money is handled with `Decimal`, not `float`** — so amounts like ₹10.10 don't get corrupted by binary floating-point rounding, and every value is rounded to exactly 2 decimal places before it touches the balance.
- **A basic fraud check** watches recent withdrawals in a rolling 5-minute window and locks the account if too many happen too fast, or too much money moves too fast.
- **Realistic-ish limits and fees** — a per-transaction cap, a daily cap, and a flat fee after 5 free withdrawals per session, loosely modeled on how Indian banks charge for ATM use.
- **A session transaction log** with UTC timestamps, viewable any time via the statement option.

PINs are stored and compared as plain strings for this project — a real system would hash the PIN and use a constant-time comparison instead, which is intentionally out of scope here.

## Getting started

```bash
git clone https://github.com/Akansh2309/ATM-Simulator.git
cd ATM-Simulator
python atm_simulator.py
```

No dependencies to install — just Python 3. Demo PIN is **`1234`**.

## Using it

Once you're logged in:

| Option | Action |
|---|---|
| `1` | Check balance |
| `2` | Deposit money |
| `3` | Withdraw money |
| `4` | View transaction statement |
| `5` | Exit |

3 wrong PINs in a row locks the session. The fraud check can also lock it mid-session if withdrawals look unusual — in both cases you'll need to restart the program.

## Why I built this

First real Python project — wanted something with actual logic to get right (money precision, input validation, state that has to stay consistent across a session) rather than just printing to a screen. Feedback and PRs welcome.
<hr>
<div align="center">
  <a href="https://github.com/Akansh2309">
    <img src="https://img.shields.io/badge/ARCHITECTED_BY-AKANSH_SHAW-FFFFFF?style=for-the-badge&logo=github&logoColor=black" alt="Architected by Akansh Shaw" />
  </a>
</div>
