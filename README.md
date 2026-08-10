<div align="center">

<h1>VIRTUAL ATM TERMINAL</h1>

<p>
  <img src="https://img.shields.io/badge/Language-Python_3.x-14354C?style=plastic&logo=python&logoColor=white" alt="Python 3.x" />
  <img src="https://img.shields.io/badge/Dependencies-None-ED8B00?style=plastic" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/Deployment-Local_CLI-00599C?style=plastic&logo=powershell&logoColor=white" alt="Local CLI" />
</p>

<blockquote>
  <i>An interactive, command-line banking environment engineered for precision financial computation, strict regulatory enforcement, and dynamic threat mitigation.</i>
</blockquote>

</div>

---

### SYSTEM ARCHITECTURE & LOGIC

This application bypasses basic scripting paradigms to establish a robust, simulated financial backend. It is designed to demonstrate core software engineering principles, including state management, heuristic analysis, and secure ledger maintenance.

*   **Precision Arithmetic:** Eliminates standard IEEE 754 floating-point inaccuracies by implementing Python's native `decimal` library, guaranteeing absolute ledger integrity.
*   **Heuristic Fraud Detection:** Actively tracks transaction velocity and volume across a rolling temporal window. The system triggers immediate session lockouts upon detecting anomalous capital extraction vectors.
*   **Regulatory Compliance:** Enforces real-world financial constraints, including per-transaction hardware limits, daily cumulative caps, and automated interchange fee structures.
*   **Cryptographic Authentication:** Dynamically evaluates user credentials, permanently locking the terminal state if maximum entropy (invalid attempts) is exhausted.
*   **Immutable Audit Trails:** Generates comprehensive, session-based transaction logs formatted to ISO 8601 standards with offset-aware UTC timestamps.

---

### EXECUTION PROTOCOLS

The terminal relies exclusively on the Python Standard Library. Follow these explicit steps to initialize the environment locally.

**Step 01: Clone the Repository**
------
Pull the source code to your local machine using Git.

```bash
git clone [https://github.com/Akansh2309/ATM-Simulator.git](https://github.com/Akansh2309/ATM-Simulator.git)
```
**Step 02: Navigate the Directory**<br>
------
Target the newly cloned repository folder.

<b>cd ATM-Simulator</b>


**Step 03: Initialize the Terminal**<br>
------
Execute the Python script to boot the interactive state machine.

<b>python atm.py</b>


<blockquote>Security Note:  The default credential required to bypass the initial authentication lock is <strong>1234</strong>.
</blockquote>

<h1>INTERACTIVE ROUTING MATRIX</h1>
Upon successful authentication, input the corresponding integer into the terminal block to execute system operations:<br><br>

*  **1. Query Liquidity** (Interrogate current cleared balances)<br>
*Transmit routing parameter (1-5): **1***


*  **2. Execute Capital Injection** (Safely ingest funds into the ledger)<br>
*Transmit routing parameter (1-5): **2***


*  **3. Execute Capital Extraction** (Withdraw funds subject to real-time fraud analysis)<br>
*Transmit routing parameter (1-5): **3***


*  **4. Generate Audit Trail** (Output complete chronological session ledger)<br>
*Transmit routing parameter (1-5): **4***


*  **5. Terminate Session** (Securely destroy session tokens and halt program)<br>
*Transmit routing parameter (1-5): **5***
<hr>
<hr>
<!-- Option 1: The White Custom Badge -->
<div align="center">
  <a href="https://github.com/Akansh2309">
    <img src="https://img.shields.io/badge/ARCHITECTED_BY-AKANSH_SHAW-FFFFFF?style=for-the-badge&logo=github&logoColor=black" alt="Architected by Akansh Shaw" />
  </a>
</div>

