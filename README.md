# GAMBIT
**General Attack & Method-Breaking Intelligence Toolkit**

A personal CTF toolkit focused on crypto challenges. Built to handle common attack patterns fast, without having to rewrite the same logic every competition.

---

## Contents

```
gambit/
├── README.md
├── .gitignore
└── src/
    ├── rsa_ctf.py   — RSA solver, runs all common attacks automatically
    └── rsa_gen.py   — RSA test case generator, generates values for each attack type
```

---

## Requirements

- Python 3.10+
- `gmpy2` (for Wiener's attack)

Install dependencies:

```bash
sudo apt install -y python3-gmpy2 libgmp-dev libmpfr-dev libmpc-dev
```

Optional — install RsaCtfTool as a heavier fallback:

```bash
cd ~/tools
git clone https://github.com/RsaCtfTool/RsaCtfTool.git
cd RsaCtfTool
pip3 install -r requirements.txt --break-system-packages
pip3 install . --break-system-packages
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Usage

### `main.py` — Solver

Run and follow the menu:

```bash
python3 src/main.py
```

**Options:**
1. Run all attacks automatically — paste N, e, c and it tries everything in order
2. Decrypt with known p and q — for when factordb gives you the factors
3. Factordb hint — prints N formatted and ready to paste into factordb.com

**Attack order:**
1. Even prime (`p=2`, checks if N is even)
2. Small e (cube root, only when `e=3`)
3. Hastads broadcast (same message, `e=3`, 3 different N values)
4. Common modulus (same N, different e values)
5. GCD multi-N (shared prime across multiple N values)
6. Fermat factorization (p and q are close)
7. Wiener's attack (small d, huge e)
8. Fallback: factordb lookup hint
---

### `gen.py` — Test Case Generator

Generates valid RSA values for each attack scenario so you can test the solver or RsaCtfTool:

```bash
python3 src/gen.py
```

**Scenarios:**
1. Even prime (`p=2`)
2. Small e (`e=3`, cube root)
3. Fermat (p and q close)
4. Wiener (small d)
5. GCD multi-N (shared prime)
6. Hastads broadcast (same message, `e=3`, 3 different keys)
7. Common modulus (same N and message, different e values)

Each scenario validates your inputs, warns if the attack won't work, and prints the exact RsaCtfTool command ready to paste.

---

## Workflow

```
given N, e, c
    └─ python3 src/main.py   → option 1 (auto)
           └─ no result?
                  └─ RsaCtfTool -n N -e e --decrypt c --attack all
                         └─ no result?
                                └─ factordb.com → paste N → get p, q → option 2
```

---

## Notes

- **Even prime attack**: RsaCtfTool rejects even N values outright — use `main.py` for this case
- **Wiener's attack**: requires `gmpy2`. Skipped automatically if not installed
- **Fermat**: capped at 1,000,000 iterations by default — increase `max_iter` in the function if needed
- **Message size**: when using `gen.py`, your message must be smaller than N as an integer
- **Primality**: `gen.py` uses Miller-Rabin for primality checks — fast on large numbers

---

## External Tools

| Tool | Purpose |
|---|---|
| [RsaCtfTool](https://github.com/RsaCtfTool/RsaCtfTool) | Heavy fallback, tries 50+ attacks |
| [factordb.com](https://factordb.com) | Online factor database, often has CTF N values |
| [CyberChef](https://gchq.github.io/CyberChef/) | Encoding/decoding, symmetric crypto |
| [dcode.fr](https://www.dcode.fr) | Classical ciphers |