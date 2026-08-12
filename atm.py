import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from flask import Flask, request, jsonify, render_template_string

class ATMSimulator:
    MAX_PIN_ATTEMPTS = 3
    PER_TXN_LIMIT = Decimal("25000.00")
    DAILY_LIMIT = Decimal("100000.00")
    MAX_DEPOSIT = Decimal("100000.00")
    FREE_TXN_LIMIT = 5
    EXCESS_TXN_FEE = Decimal("23.00")
    FRAUD_TIME_WINDOW_SEC = 300
    VELOCITY_MAX_COUNT = 3
    VOLUME_MAX_LIMIT = Decimal("50000.00")
    TWO_PLACES = Decimal("0.01")

    def __init__(self, account_holder, balance="2500.00", pin="1234"):
        self.account_holder = account_holder
        self.balance = Decimal(balance).quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)
        self.pin = pin
        self.is_locked = False
        self.pin_attempts_remaining = self.MAX_PIN_ATTEMPTS
        self.daily_withdrawn = Decimal("0.00")
        self.txns_performed = 0
        self.transaction_history = []

    def authenticate(self, input_pin):
        if self.is_locked:
            return {"success": False, "message": "[LOCKED] This account is locked."}

        if input_pin == self.pin:
            self.pin_attempts_remaining = self.MAX_PIN_ATTEMPTS
            return {"success": True, "message": "PIN accepted."}

        self.pin_attempts_remaining -= 1
        if self.pin_attempts_remaining <= 0:
            self.is_locked = True
            return {"success": False, "message": "[LOCKED] Too many incorrect attempts. Account locked."}
        return {"success": False, "message": f"[DENIED] Incorrect PIN. Attempts remaining: {self.pin_attempts_remaining}"}

    def get_balance_info(self):
        return {
            "holder": self.account_holder,
            "balance": str(self.balance)
        }

    def deposit(self, amount_str):
        if self.is_locked:
            return {"success": False, "message": "[DENIED] This account is locked."}

        amount = self._parse_amount(amount_str)
        if amount is None:
            return {"success": False, "message": "Please enter a valid amount."}
        if amount <= Decimal("0.00"):
            return {"success": False, "message": "Deposit amount must be greater than zero."}
        if amount > self.MAX_DEPOSIT:
            return {"success": False, "message": f"Amount exceeds max deposit of Rs. {self.MAX_DEPOSIT:,.2f}."}

        self.balance += amount
        self._log_transaction("DEPOSIT", amount, "SUCCESS", Decimal("0.00"))
        return {"success": True, "message": f"Deposited Rs. {amount:,.2f}. New balance: Rs. {self.balance:,.2f}"}

    def withdraw(self, amount_str):
        if self.is_locked:
            return {"success": False, "message": "[DENIED] This account is locked."}

        amount = self._parse_amount(amount_str)
        if amount is None:
            return {"success": False, "message": "Please enter a valid amount."}
        if amount <= Decimal("0.00"):
            return {"success": False, "message": "Withdrawal amount must be greater than zero."}
        if amount > self.PER_TXN_LIMIT:
            self._log_transaction("WITHDRAWAL", amount, "FAILED_TXN_LIMIT", Decimal("0.00"))
            return {"success": False, "message": f"Exceeds per-transaction limit of Rs. {self.PER_TXN_LIMIT:,.2f}."}
        if self.daily_withdrawn + amount > self.DAILY_LIMIT:
            self._log_transaction("WITHDRAWAL", amount, "FAILED_DAILY_LIMIT", Decimal("0.00"))
            return {"success": False, "message": f"Exceeds today's withdrawal limit of Rs. {self.DAILY_LIMIT:,.2f}."}
        
        if self._detect_fraud(amount):
            return {"success": False, "message": "[ACCOUNT LOCKED] Unusual withdrawal activity detected."}

        fee = self._quote_fee()
        total_needed = amount + fee

        if total_needed > self.balance:
            self._log_transaction("WITHDRAWAL", amount, "FAILED_INSUFFICIENT_FUNDS", Decimal("0.00"))
            msg = f"Insufficient balance. Current: Rs. {self.balance:,.2f}."
            if fee > 0: msg += f" (Includes Rs. {fee:,.2f} fee)"
            return {"success": False, "message": msg}

        self.txns_performed += 1
        self.balance -= total_needed
        self.daily_withdrawn += amount
        self._log_transaction("WITHDRAWAL", amount, "SUCCESS", fee)

        msg = f"Withdrew Rs. {amount:,.2f}. New balance: Rs. {self.balance:,.2f}."
        if fee > 0: msg += f" A Rs. {fee:,.2f} fee applied."
        return {"success": True, "message": msg}

    def get_statement(self):
        history = []
        for tx in self.transaction_history:
            history.append({
                "timestamp": tx["timestamp"].strftime("%Y-%m-%d %H:%M:%S UTC"),
                "type": tx["type"],
                "amount": str(tx["amount"]),
                "fee": str(tx["fee"]),
                "status": tx["status"],
                "balance_after": str(tx["balance_after"])
            })
        return history

    def _parse_amount(self, amount_str):
        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            return None
        if not amount.is_finite():
            return None
        return amount.quantize(self.TWO_PLACES, rounding=ROUND_HALF_UP)

    def _quote_fee(self):
        if self.txns_performed >= self.FREE_TXN_LIMIT:
            return self.EXCESS_TXN_FEE
        return Decimal("0.00")

    def _detect_fraud(self, requested_amount):
        now = datetime.datetime.now(datetime.timezone.utc)
        recent_withdrawals = [
            tx for tx in self.transaction_history
            if tx["type"] == "WITHDRAWAL" and tx["status"] == "SUCCESS"
            and (now - tx["timestamp"]).total_seconds() <= self.FRAUD_TIME_WINDOW_SEC
        ]
        if len(recent_withdrawals) >= self.VELOCITY_MAX_COUNT:
            self.is_locked = True
            self._log_transaction("FRAUD_LOCK_VELOCITY", requested_amount, "BLOCKED", Decimal("0.00"))
            return True
        recent_total = sum(tx["amount"] for tx in recent_withdrawals)
        if recent_total + requested_amount > self.VOLUME_MAX_LIMIT:
            self.is_locked = True
            self._log_transaction("FRAUD_LOCK_VOLUME", requested_amount, "BLOCKED", Decimal("0.00"))
            return True
        return False

    def _log_transaction(self, tx_type, amount, status, fee):
        self.transaction_history.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "type": tx_type,
            "amount": amount,
            "fee": fee,
            "status": status,
            "balance_after": self.balance,
        })


# ==========================================
# FLASK WEB SERVER SETUP
# ==========================================
app = Flask(__name__)
# Initialize a single global ATM instance for the server
atm_instance = ATMSimulator(account_holder="Demo User", balance="2500.00", pin="1234")

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>ATM Simulator</title>
    <style>
        body { font-family: monospace; background: #1e1e1e; color: #00ff00; max-width: 600px; margin: 40px auto; padding: 20px; }
        input, button { background: #333; color: #00ff00; border: 1px solid #00ff00; padding: 10px; margin: 5px 0; font-family: monospace;}
        button { cursor: pointer; width: 100%; }
        button:hover { background: #00ff00; color: #1e1e1e; }
        #output { border: 1px solid #00ff00; padding: 15px; min-height: 100px; margin-top: 20px; white-space: pre-wrap;}
        .hidden { display: none; }
    </style>
</head>
<body>
    <h2>=== ATM SIMULATOR ===</h2>
    <div id="login-section">
        <p>Enter 4-digit PIN (Demo: 1234):</p>
        <input type="password" id="pin" />
        <button onclick="login()">Enter</button>
    </div>

    <div id="dashboard" class="hidden">
        <button onclick="checkBalance()">1. Check Balance</button>
        <div style="display:flex; gap:10px;">
            <input type="number" id="amt" placeholder="Amount (Rs.)" style="flex:1;" />
            <button onclick="deposit()" style="flex:1;">2. Deposit</button>
            <button onclick="withdraw()" style="flex:1;">3. Withdraw</button>
        </div>
        <button onclick="printStatement()">4. Print Statement</button>
    </div>

    <div id="output">System Ready...</div>

    <script>
        let loggedIn = false;
        
        async function postData(action, payload={}) {
            payload.action = action;
            const res = await fetch('/api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            return await res.json();
        }

        function out(text) { document.getElementById('output').innerText = text; }

        async function login() {
            const pin = document.getElementById('pin').value;
            const res = await postData('login', { pin: pin });
            out(res.message);
            if (res.success) {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('dashboard').classList.remove('hidden');
            }
        }

        async function checkBalance() {
            const res = await fetch('/api/balance').then(r => r.json());
            out(`Account Holder: ${res.holder}\\nBalance: Rs. ${res.balance}`);
        }

        async function deposit() {
            const amt = document.getElementById('amt').value;
            const res = await postData('deposit', { amount: amt });
            out(res.message);
        }

        async function withdraw() {
            const amt = document.getElementById('amt').value;
            const res = await postData('withdraw', { amount: amt });
            out(res.message);
        }

        async function printStatement() {
            const res = await fetch('/api/statement').then(r => r.json());
            if (res.length === 0) return out("No transactions yet.");
            let text = "--- TRANSACTION STATEMENT ---\\n";
            res.forEach((tx, i) => {
                text += `${i+1}. [${tx.timestamp}] ${tx.type}\\n    Amount: Rs. ${tx.amount} | Status: ${tx.status}\\n`;
            });
            out(text);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_UI)

@app.route("/api/balance", methods=["GET"])
def api_balance():
    return jsonify(atm_instance.get_balance_info())

@app.route("/api/statement", methods=["GET"])
def api_statement():
    return jsonify(atm_instance.get_statement())

@app.route("/api", methods=["POST"])
def api_action():
    data = request.json
    action = data.get("action")
    
    if action == "login":
        return jsonify(atm_instance.authenticate(data.get("pin", "")))
    elif action == "deposit":
        return jsonify(atm_instance.deposit(data.get("amount", "")))
    elif action == "withdraw":
        return jsonify(atm_instance.withdraw(data.get("amount", "")))
        
    return jsonify({"success": False, "message": "Unknown action."}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
