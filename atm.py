"""
ATM Simulator
=============

A simple command-line ATM simulator. Supports PIN authentication,
balance checks, deposits, withdrawals, and a transaction history --
with a few realistic touches:

- Money is handled using Decimal, not float, so amounts are never
  corrupted by binary floating-point rounding errors.
- Withdrawals are checked against a per-transaction limit, a daily
  limit, a simple fraud heuristic (too many withdrawals, or too much
  money moved, in a short time), and a "free transactions per
  session, then a flat fee" model loosely based on how Indian banks
  charge for ATM use beyond the RBI's free-transaction limit.
- The PIN is stored as a plain string and compared directly. A real
  banking system would hash the PIN and use a constant-time
  comparison instead -- that's intentionally out of scope here.

Nothing is saved to disk: the balance and transaction history reset
every time you run the program.

Run it with:  python atm_simulator.py
"""

import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class ATMSimulator:
    """One ATM session for one account."""

    # ---- Shared settings (same for every ATM, so they live on the
    # class itself instead of being rebuilt inside __init__ each time) ----

    MAX_PIN_ATTEMPTS = 3                    # wrong PINs allowed before locking

    PER_TXN_LIMIT = Decimal("25000.00")     # max withdrawal in one go
    DAILY_LIMIT = Decimal("100000.00")      # max withdrawal per day
    MAX_DEPOSIT = Decimal("100000.00")      # max deposit in one go
    # (Real banks set their own per-transaction/daily limits per card
    # type -- there isn't one single RBI-wide number for this. These
    # are just realistic example values for the simulation.)

    FREE_TXN_LIMIT = 5                      # free withdrawals before a fee applies
    EXCESS_TXN_FEE = Decimal("23.00")       # RBI's current cap on that fee

    FRAUD_TIME_WINDOW_SEC = 300             # 5-minute rolling window
    VELOCITY_MAX_COUNT = 3                  # max withdrawals allowed in that window
    VOLUME_MAX_LIMIT = Decimal("50000.00")  # max amount withdrawn in that window

    TWO_PLACES = Decimal("0.01")            # used to round money to 2 decimal places

    def __init__(self, account_holder, balance="2500.00", pin="1234"):
        self.account_holder = account_holder

        # Always build Decimal amounts from strings, never from floats,
        # and round to exactly 2 decimal places so the balance can
        # never quietly drift to 3+ decimal places.
        self.balance = Decimal(balance).quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)

        # Kept as a string, not an int, so a PIN like "0912" doesn't
        # lose its leading zero.
        self.pin = pin

        self.is_locked = False
        self.pin_attempts_remaining = self.MAX_PIN_ATTEMPTS

        self.daily_withdrawn = Decimal("0.00")
        self.txns_performed = 0

        # Every deposit, withdrawal, and failed attempt gets appended
        # here so print_statement() can show the full session history.
        self.transaction_history = []

    # ------------------------------------------------------------------
    # Public operations
    # ------------------------------------------------------------------

    def authenticate(self, input_pin):
        """Check a PIN against the stored one. Locks the account after
        too many wrong attempts in a row."""
        if self.is_locked:
            print("\n[LOCKED] This account is locked. Please contact your bank.")
            return False

        # Note: a real system would never compare PINs directly like
        # this. It would store a hash of the PIN and compare using
        # something like hmac.compare_digest() to avoid leaking timing
        # information. Doing that properly is outside the scope of a
        # simulator like this one.
        if input_pin == self.pin:
            self.pin_attempts_remaining = self.MAX_PIN_ATTEMPTS
            return True

        self.pin_attempts_remaining -= 1
        if self.pin_attempts_remaining <= 0:
            self.is_locked = True
            print("\n[LOCKED] Too many incorrect attempts. Account locked.")
        else:
            print(f"\n[DENIED] Incorrect PIN. Attempts remaining: {self.pin_attempts_remaining}")
        return False

    def check_balance(self):
        """Print the current balance.

        This works even if the account is locked -- in real life you
        can usually still see your balance (net banking, SMS) even with
        a blocked card, so that's intentional here, not an oversight.
        """
        print("\n-------------------------------------------------------")
        print(f" Account Holder : {self.account_holder}")
        print(f" Balance        : Rs. {self.balance:,.2f}")
        print("-------------------------------------------------------")

    def deposit(self, amount_str):
        """Add money to the balance."""
        if self.is_locked:
            print("\n[DENIED] This account is locked.")
            return

        amount = self._parse_amount(amount_str)
        if amount is None:
            print("\n[ERROR] Please enter a valid amount, e.g. 500 or 500.50")
            return

        if amount <= Decimal("0.00"):
            print("\n[ERROR] Deposit amount must be greater than zero.")
            return

        if amount > self.MAX_DEPOSIT:
            print(f"\n[DENIED] Amount exceeds the maximum single deposit of Rs. {self.MAX_DEPOSIT:,.2f}.")
            return

        self.balance += amount
        self._log_transaction("DEPOSIT", amount, "SUCCESS", Decimal("0.00"))

        print(f"\n[SUCCESS] Deposited Rs. {amount:,.2f}.")
        print(f"New balance: Rs. {self.balance:,.2f}")

    def withdraw(self, amount_str):
        """
        Withdraw money. Checks, in order:
          1. the per-transaction limit
          2. the daily limit
          3. a simple fraud heuristic
          4. whether the balance covers the amount plus any fee
        Only if all four pass does the balance actually change.
        """
        if self.is_locked:
            print("\n[DENIED] This account is locked.")
            return

        amount = self._parse_amount(amount_str)
        if amount is None:
            print("\n[ERROR] Please enter a valid amount, e.g. 500 or 500.50")
            return

        if amount <= Decimal("0.00"):
            print("\n[ERROR] Withdrawal amount must be greater than zero.")
            return

        if amount > self.PER_TXN_LIMIT:
            print(f"\n[DENIED] Amount exceeds the per-transaction limit of Rs. {self.PER_TXN_LIMIT:,.2f}.")
            self._log_transaction("WITHDRAWAL", amount, "FAILED_TXN_LIMIT", Decimal("0.00"))
            return

        if self.daily_withdrawn + amount > self.DAILY_LIMIT:
            print(f"\n[DENIED] This would exceed today's withdrawal limit of Rs. {self.DAILY_LIMIT:,.2f}.")
            self._log_transaction("WITHDRAWAL", amount, "FAILED_DAILY_LIMIT", Decimal("0.00"))
            return

        if self._detect_fraud(amount):
            print("\n[ACCOUNT LOCKED] Unusual withdrawal activity detected.")
            return

        # _quote_fee() only calculates -- it doesn't change any state --
        # so there's nothing to undo if the balance check below fails.
        fee = self._quote_fee()
        total_needed = amount + fee

        if total_needed > self.balance:
            print(f"\n[DENIED] Insufficient balance. Current balance: Rs. {self.balance:,.2f}")
            if fee > Decimal("0.00"):
                print(f"          (This withdrawal would also include a Rs. {fee:,.2f} fee.)")
            self._log_transaction("WITHDRAWAL", amount, "FAILED_INSUFFICIENT_FUNDS", Decimal("0.00"))
            return

        # Everything checks out -- commit all the state changes together.
        self.txns_performed += 1
        self.balance -= total_needed
        self.daily_withdrawn += amount
        self._log_transaction("WITHDRAWAL", amount, "SUCCESS", fee)

        print(f"\n[SUCCESS] Withdrew Rs. {amount:,.2f}.")
        if fee > Decimal("0.00"):
            print(f"          A Rs. {fee:,.2f} fee applied (free transactions used up).")
        print(f"New balance: Rs. {self.balance:,.2f}")

    def print_statement(self):
        """Print every transaction from this session, oldest first."""
        print("\n=======================================================")
        print("                 TRANSACTION STATEMENT")
        print("=======================================================")

        if not self.transaction_history:
            print(" No transactions yet.")
            return

        for i, tx in enumerate(self.transaction_history, start=1):
            ts = tx["timestamp"].strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"{i}. [{ts}] {tx['type']}")
            print(f"   Amount        : Rs. {tx['amount']:,.2f}")
            if tx["fee"] > Decimal("0.00"):
                print(f"   Fee           : Rs. {tx['fee']:,.2f}")
            print(f"   Status        : {tx['status']}")
            print(f"   Balance after : Rs. {tx['balance_after']:,.2f}")
            print("-------------------------------------------------------")

    # ------------------------------------------------------------------
    # Internal helpers (leading underscore = not meant to be called
    # from outside the class)
    # ------------------------------------------------------------------

    def _parse_amount(self, amount_str):
        """
        Turn user input into a valid Decimal amount rounded to 2 decimal
        places, or return None if it isn't valid.

        This guards against two easy-to-miss edge cases:
        - Decimal("nan") and Decimal("Infinity") both parse without
          error (they're valid Decimal values!) but aren't valid money
          amounts. Comparing a NaN with <, <=, > or >= raises an error,
          so it has to be caught here, before any comparison happens.
        - Without rounding here, an amount like "10.999" would carry
          three decimal places into the balance forever, even though
          everything is displayed rounded to two -- so the number on
          screen and the number actually stored would quietly disagree.
        """
        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            return None

        if not amount.is_finite():
            return None

        return amount.quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)

    def _quote_fee(self):
        """Return the fee that would apply to the NEXT withdrawal. Pure
        calculation -- doesn't change any state, so it's safe to call
        just to check."""
        if self.txns_performed >= self.FREE_TXN_LIMIT:
            return self.EXCESS_TXN_FEE
        return Decimal("0.00")

    def _detect_fraud(self, requested_amount):
        """
        A very simple fraud heuristic: look at successful withdrawals in
        the last few minutes and lock the account if either the number
        of withdrawals or the total amount withdrawn looks unusually
        high. Real fraud detection is far more sophisticated than this --
        this is just meant to demonstrate the idea.
        """
        now = datetime.datetime.now(datetime.timezone.utc)

        recent_withdrawals = [
            tx for tx in self.transaction_history
            if tx["type"] == "WITHDRAWAL"
            and tx["status"] == "SUCCESS"
            and (now - tx["timestamp"]).total_seconds() <= self.FRAUD_TIME_WINDOW_SEC
        ]

        # Too many withdrawals in a short time
        if len(recent_withdrawals) >= self.VELOCITY_MAX_COUNT:
            self.is_locked = True
            self._log_transaction("FRAUD_LOCK_VELOCITY", requested_amount, "BLOCKED", Decimal("0.00"))
            return True

        # Too much money moved in a short time
        recent_total = sum(tx["amount"] for tx in recent_withdrawals)
        if recent_total + requested_amount > self.VOLUME_MAX_LIMIT:
            self.is_locked = True
            self._log_transaction("FRAUD_LOCK_VOLUME", requested_amount, "BLOCKED", Decimal("0.00"))
            return True

        return False

    def _log_transaction(self, tx_type, amount, status, fee):
        """Append one entry to the transaction history."""
        self.transaction_history.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "type": tx_type,
            "amount": amount,
            "fee": fee,
            "status": status,
            "balance_after": self.balance,
        })


def main():
    atm = ATMSimulator(account_holder="Demo User", balance="2500.00", pin="1234")

    print("=======================================================")
    print("                    ATM SIMULATOR")
    print("=======================================================")
    print("(Demo PIN is 1234 -- this is a simulation, not a real bank)")

    # ---- Step 1: authenticate before showing the menu ----
    authenticated = False
    while atm.pin_attempts_remaining > 0 and not atm.is_locked:
        entered_pin = input("\nEnter your 4-digit PIN: ").strip()
        if atm.authenticate(entered_pin):
            authenticated = True
            print("\n[SUCCESS] PIN accepted.")
            break

    if not authenticated:
        print("\nToo many incorrect attempts. Exiting.")
        return

    # ---- Step 2: main menu loop ----
    while True:
        # Checked at the top of every loop, not just right after a
        # withdrawal, so a mid-session fraud lock ends the session the
        # same way a failed-PIN lock does.
        if atm.is_locked:
            print("\n[SESSION ENDED] Your account is locked. Please contact your bank.")
            break

        print("\n=======================================================")
        print(" 1. Check Balance")
        print(" 2. Deposit")
        print(" 3. Withdraw")
        print(" 4. Print Statement")
        print(" 5. Exit")
        print("=======================================================")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            atm.check_balance()
        elif choice == "2":
            amount_str = input("Enter deposit amount (Rs.): ").strip()
            atm.deposit(amount_str)
        elif choice == "3":
            amount_str = input("Enter withdrawal amount (Rs.): ").strip()
            atm.withdraw(amount_str)
        elif choice == "4":
            atm.print_statement()
        elif choice == "5":
            print("\nThank you for using the ATM. Goodbye!")
            break
        else:
            print("\n[ERROR] Please choose a number from 1 to 5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSession interrupted. Goodbye!")
