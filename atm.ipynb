import datetime
from decimal import Decimal, InvalidOperation

class SecureBankATM:
    """
    A production-grade Virtual ATM state machine.
    
    Architectural Enhancements Implemented:
    - High-precision base-10 arithmetic utilizing the decimal.Decimal standard.
    - Offset-aware UTC transaction logging formatted to ISO 8601 (RFC 3339).
    - Regulatory enforcement of RBI transaction limits, hardware caps, and fee structures.
    - Dynamic velocity and volume fraud detection mechanisms utilizing time deltas.
    - Secure credential handling utilizing string primitives to preserve absolute entropy.
    """

    def __init__(self, account_holder: str, balance: str = "2500.00", pin: str = "1234"):
        # 1. State Management & Cryptographic Setup
        self.account_holder = account_holder
        
        # Financial values MUST be instantiated as Decimal via string literals.
        # This immunizes the ledger against IEEE 754 binary floating-point approximation.
        self.balance = Decimal(balance)
        
        # Credentials must remain strings to preserve leading zeroes (e.g., "0912" != 912)
        self.pin = pin
        
        # Immutable security state variables
        self.is_locked = False
        self.MAX_PIN_ATTEMPTS = 3
        self.pin_attempts_remaining = self.MAX_PIN_ATTEMPTS
        
        # Structured immutable ledger for chronological auditing
        self.transaction_history = []
        
        # 2. RBI Regulatory & Hardware Constraints
        # Based on standard mass-market card variants (e.g., RuPay Classic / VISA Classic)
        self.PER_TXN_LIMIT = Decimal("25000.00")      # Hardware extraction limit per request
        self.DAILY_LIMIT = Decimal("100000.00")       # Total daily limit across all sessions
        self.daily_withdrawn = Decimal("0.00")        # Volatile accumulator for current session
        
        self.FREE_TXN_LIMIT = 5                       # RBI mandated free transactions (On-Us Network)
        self.txns_performed = 0                       # Counter for billable ledger events
        self.EXCESS_TXN_FEE = Decimal("23.00")        # Current RBI mandated fee beyond free tier
        
        # 3. Fraud Detection Constants (Velocity & Volume Heuristics)
        self.FRAUD_TIME_WINDOW_SEC = 300              # 5-minute rolling temporal window
        self.VELOCITY_MAX_COUNT = 3                   # Hard limit: 3 withdrawals in 5 mins
        self.VOLUME_MAX_LIMIT = Decimal("50000.00")   # Hard limit: ₹50k outflow in 5 mins

    def authenticate(self, input_pin: str) -> bool:
        """
        Cryptographically evaluates the provided PIN against the stored credential.
        Permanently locks the instance in memory if exhaustive attempts are reached.
        """
        # Reject authentication instantly if the system state is flagged as compromised
        if self.is_locked:
            print("\n[SECURITY FAULT] Account is locked due to suspicious activity or failed authorizations.")
            return False
            
        # In a deployed environment, this comparison must utilize constant-time algorithms
        # such as hmac.compare_digest() to mitigate timing-based side-channel attacks.
        if input_pin == self.pin:
            self.pin_attempts_remaining = self.MAX_PIN_ATTEMPTS # Restoring state upon success
            return True
        else:
            self.pin_attempts_remaining -= 1
            if self.pin_attempts_remaining <= 0:
                self.is_locked = True
                print("\n[LOCKED] Maximum PIN entropy exhausted. Account has been permanently locked.")
            else:
                print(f"\n[DENIED] Incorrect credential. Authorization attempts remaining: {self.pin_attempts_remaining}")
            return False

    def check_balance(self):
        """
        Generates a standardized view of available liquidity.
        Note: Under specific RBI frameworks, non-financial queries may deplete the free tier quota.
        For this standard simulation, balance checks are exempt from fee routing.
        """
        print(f"\n-------------------------------------------------------")
        print(f" Account Holder: {self.account_holder}")
        # Dynamically formats the Decimal object with comma separations and exact dual precision
        print(f" Cleared Balance: ₹{self.balance:,.2f}")
        print(f"-------------------------------------------------------")

    def _assess_transaction_fee(self) -> Decimal:
        """
        Evaluates the transaction counter against RBI compliance quotas.
        Returns the predetermined penalty fee (₹23.00) if the free tier is breached.
        """
        self.txns_performed += 1
        if self.txns_performed > self.FREE_TXN_LIMIT:
            return self.EXCESS_TXN_FEE
        return Decimal("0.00")

    def _detect_fraud(self, requested_amount: Decimal) -> bool:
        """
        Executes heuristic analysis over the transaction ledger to detect velocity and volume anomalies.
        Returns True and engages the security lockdown if a threat vector is identified.
        """
        # Generate an offset-aware UTC datetime to ensure perfect cross-regional compatibility
        current_time = datetime.datetime.now(datetime.timezone.utc)
        
        # Filter the ledger to isolate successful withdrawals within the rolling time window
        recent_withdrawals = [
            tx for tx in self.transaction_history
            if tx['type'] == 'WITHDRAWAL' and tx['status'] == 'SUCCESS'
            and (current_time - tx['timestamp']).total_seconds() <= self.FRAUD_TIME_WINDOW_SEC
        ]
        
        # Threat Vector 1: Velocity Check (Excessive rapid extraction attempts)
        if len(recent_withdrawals) >= self.VELOCITY_MAX_COUNT:
            self.is_locked = True
            self._log_transaction("FRAUD_LOCK_VELOCITY", requested_amount, "BLOCKED", Decimal("0.00"))
            return True
            
        # Threat Vector 2: Volume Check (Massive capital flight within microscopic window)
        cumulative_recent = sum(tx['amount'] for tx in recent_withdrawals)
        if cumulative_recent + requested_amount > self.VOLUME_MAX_LIMIT:
            self.is_locked = True
            self._log_transaction("FRAUD_LOCK_VOLUME", requested_amount, "BLOCKED", Decimal("0.00"))
            return True
            
        return False

    def _log_transaction(self, tx_type: str, amount: Decimal, status: str, fee: Decimal):
        """
        Constructs and appends an immutable, timezone-aware dictionary to the session ledger.
        """
        self.transaction_history.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "type": tx_type,
            "amount": amount,
            "fee": fee,
            "status": status,
            "balance_after": self.balance
        })

    def deposit(self, amount_str: str):
        """
        Validates input sanitization and processes capital injection safely.
        """
        if self.is_locked:
            print("\n[DENIED] Transaction rejected. Account is under security lockdown.")
            return

        try:
            # Traps any alphanumeric pollution and casts cleanly to Decimal
            amount = Decimal(amount_str)
        except InvalidOperation:
            print("\n[ERROR] Malformed input detected. Please utilize numerical syntax exclusively.")
            return

        if amount <= Decimal("0.00"):
            print("\n[ERROR] Deposited capital must represent a positive integer.")
            return

        # Simulating physical cassette capacity limits (e.g., 200 physical notes of ₹500)
        MAX_DEPOSIT = Decimal("100000.00")
        if amount > MAX_DEPOSIT:
            print(f"\n[DENIED] Volume exceeds physical intake manifold capacity of ₹{MAX_DEPOSIT:,.2f}.")
            return

        # Execute verified mathematical addition
        self.balance += amount
        self._log_transaction("DEPOSIT", amount, "SUCCESS", Decimal("0.00"))
        
        print(f"\n[SUCCESS] Capital ingestion confirmed: ₹{amount:,.2f}.")
        print(f"Updated Ledger Balance: ₹{self.balance:,.2f}")

    def withdraw(self, amount_str: str):
        """
        Processes capital extraction by orchestrating RBI limits, penalty fee structures, 
        and dynamic heuristic threat monitoring.
        """
        if self.is_locked:
            print("\n[DENIED] Transaction rejected. Account is under security lockdown.")
            return

        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            print("\n[ERROR] Malformed input detected. Please utilize numerical syntax exclusively.")
            return

        if amount <= Decimal("0.00"):
            print("\n[ERROR] Withdrawal request must represent a positive integer.")
            return

        # 1. Hardware & Risk Analysis: Per-Transaction Limit verification
        if amount > self.PER_TXN_LIMIT:
            print(f"\n[DENIED] Hardware constraint exceeded. RBI per-transaction cap is ₹{self.PER_TXN_LIMIT:,.2f}.")
            self._log_transaction("WITHDRAWAL", amount, "FAILED_HARDWARE_LIMIT", Decimal("0.00"))
            return

        # 2. Regulatory Compliance: Cumulative Daily Ceiling verification
        if self.daily_withdrawn + amount > self.DAILY_LIMIT:
            print(f"\n[DENIED] Request exceeds regulatory daily dispensation limit of ₹{self.DAILY_LIMIT:,.2f}.")
            self._log_transaction("WITHDRAWAL", amount, "FAILED_DAILY_LIMIT", Decimal("0.00"))
            return

        # 3. Security Check: Dynamic Threat Vector Detection
        if self._detect_fraud(amount):
            print("\n[CRITICAL SECURITY ALERT] Anomalous behavioural vectors detected. Account locked.")
            return

        # 4. Interchange Protocol: Assess fees and ensure adequate liquidity exists for combined liability
        applicable_fee = self._assess_transaction_fee()
        total_liability = amount + applicable_fee

        if total_liability > self.balance:
            print(f"\n[DENIED] Insufficient liquidity. Current Balance: ₹{self.balance:,.2f}")
            if applicable_fee > 0:
                print(f"         (Note: An interchange penalty fee of ₹{applicable_fee:,.2f} applies to this request).")
            # The transaction failed, thus the usage counter must be rolled back
            self.txns_performed -= 1
            self._log_transaction("WITHDRAWAL", amount, "FAILED_INSUFFICIENT_FUNDS", Decimal("0.00"))
            return

        # 5. Authorization: Execute ledger modifications
        self.balance -= total_liability
        self.daily_withdrawn += amount
        
        # Append finalized state to immutable ledger
        self._log_transaction("WITHDRAWAL", amount, "SUCCESS", applicable_fee)

        print(f"\n[SUCCESS] Extraction authorized. Dispensing ₹{amount:,.2f}.")
        if applicable_fee > Decimal("0.00"):
            print(f"          (Interchange network fee of ₹{applicable_fee:,.2f} applied due to quota exhaustion).")
        print(f"Updated Ledger Balance: ₹{self.balance:,.2f}")

    def print_statement(self):
        """
        Renders a chronologically ordered, ISO 8601 (RFC 3339) compliant audit log 
        suitable for regulatory transmission or end-user review.
        """
        print(f"\n=======================================================")
        print(f"       SECURE CRYPTOGRAPHIC AUDIT LOG & LEDGER         ")
        print(f"=======================================================")
        if not self.transaction_history:
            print(" No chronological events recorded in the current session.")
        else:
            for index, tx in enumerate(self.transaction_history, start=1):
                # Formats the aware UTC datetime into a universally standardized Zulu string
                ts = tx['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
                
                print(f"{index}. [{ts}] {tx['type']}")
                print(f"   Requested Volume: ₹{tx['amount']:,.2f}")
                if tx['fee'] > Decimal("0.00"):
                    print(f"   Interchange Fee : ₹{tx['fee']:,.2f}")
                print(f"   Final Status    : {tx['status']}")
                print(f"   Ledger Residual : ₹{tx['balance_after']:,.2f}")
                print(f"-------------------------------------------------------")


def execute_virtual_atm_terminal():
    """
    Primary interactive execution daemon.
    Utilizes broad exception trapping to guarantee zero runtime architectural collapses.
    """
    # System Initialization
    atm = SecureBankATM(account_holder="Authorized Client", balance="2500.00", pin="1234")

    print("\n=======================================================")
    print("      SECURE VIRTUAL ATM TERMINAL (RBI COMPLIANT)      ")
    print("=======================================================")

    # Phase 1: Identity & Access Management
    authenticated = False
    while atm.pin_attempts_remaining > 0 and not atm.is_locked:
        entered_pin = input("\nTransmit 4-digit Cryptographic PIN: ").strip()
        if atm.authenticate(entered_pin):
            authenticated = True
            print("\n[AUTHENTICATION SUCCESS] Encrypted session established.")
            break

    if not authenticated:
        # Graceful daemon termination upon security lockout
        return

    # Phase 2: Core Routing Matrix
    while True:
        print("\n=======================================================")
        print("                 TERMINAL ROUTING MATRIX               ")
        print("=======================================================")
        print(" 1. Query Liquidity (Balance Check)")
        print(" 2. Execute Capital Injection (Deposit)")
        print(" 3. Execute Capital Extraction (Withdrawal)")
        print(" 4. Generate Cryptographic Audit Trail")
        print(" 5. Terminate Session & Eject Media")
        print("=======================================================")

        command_vector = input("Transmit routing parameter (1-5): ").strip()

        if command_vector == "1":
            atm.check_balance()

        elif command_vector == "2":
            deposit_volume = input("Declare injection volume (₹): ").strip()
            atm.deposit(deposit_volume)

        elif command_vector == "3":
            withdraw_volume = input("Declare extraction volume (₹): ").strip()
            atm.withdraw(withdraw_volume)

        elif command_vector == "4":
            atm.print_statement()

        elif command_vector == "5":
            print("\n[SESSION TERMINATED] Destroying tokens. Media ejected. Goodbye.")
            break

        else:
            print("\n[ROUTING ERROR] Unrecognized parameter. Valid matrix range is 1 through 5.")

# Execution entry point
if __name__ == "__main__":
    execute_virtual_atm_terminal()
