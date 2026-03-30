import math
import os
import re
import collections

# ANSI Color Codes for UI
class C:
    HDR = '\033[95m'    # Purple
    BLU = '\033[94m'    # Blue
    CYN = '\033[96m'    # Cyan
    GRN = '\033[92m'    # Green
    WRN = '\033[93m'    # Yellow
    ERR = '\033[91m'    # Red
    RST = '\033[0m'     # Reset
    BLD = '\033[1m'     # Bold

# Regex to accurately measure string lengths by ignoring invisible ANSI color codes
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(s):
    return ANSI_ESCAPE.sub('', str(s))

# ============================== UI ENGINE ==============================

class Win:
    W = 80

    @staticmethod
    def top(title=""):
        t = f" {C.BLD}{title}{C.RST}{C.CYN} " if title else ""
        vlen = len(strip_ansi(t))
        d = (Win.W - vlen) // 2
        rem = Win.W - vlen - d
        print(f"{C.CYN}╭{'─'*d}{t}{'─'*rem}╮{C.RST}")

    @staticmethod
    def bot():
        print(f"{C.CYN}╰{'─'*Win.W}╯{C.RST}")

    @staticmethod
    def div(title=""):
        t = f" {C.BLD}{title}{C.RST}{C.CYN} " if title else ""
        vlen = len(strip_ansi(t))
        d = (Win.W - vlen) // 2
        rem = Win.W - vlen - d
        print(f"{C.CYN}├{'─'*d}{t}{'─'*rem}┤{C.RST}")

    @staticmethod
    def text(line=""):
        for l in str(line).split('\n'):
            while len(strip_ansi(l)) > Win.W - 2:
                part = l[:Win.W - 2]
                Win._print_line(part)
                l = "  " + l[Win.W - 2:]
            Win._print_line(l)

    @staticmethod
    def _print_line(line):
        vlen = len(strip_ansi(line))
        pad = Win.W - vlen - 2
        print(f"{C.CYN}│{C.RST} {line}{' '*max(0, pad)} {C.CYN}│{C.RST}")

# =======================================================================

GAMBIT_BANNER = r"""
 
 ██████╗  █████╗ ███╗   ███╗██████╗ ██╗████████╗
██╔════╝ ██╔══██╗████╗ ████║██╔══██╗██║╚══██╔══╝
██║  ███╗███████║██╔████╔██║██████╔╝██║   ██║   
██║   ██║██╔══██║██║╚██╔╝██║██╔══██╗██║   ██║   
╚██████╔╝██║  ██║██║ ╚═╝ ██║██████╔╝██║   ██║   
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝   
 """

def print_rainbow_banner(text):
    lines = text.strip('\n').split('\n')
    for line in lines:
        colored_line = ""
        for i, char in enumerate(line):
            r = int(math.sin(0.1 * i + 0) * 127 + 128)
            g = int(math.sin(0.1 * i + 2 * math.pi / 3) * 127 + 128)
            b = int(math.sin(0.1 * i + 4 * math.pi / 3) * 127 + 128)
            colored_line += f"\033[38;2;{r};{g};{b}m{char}"
        
        pad_left = (Win.W - 2 - len(line)) // 2
        Win._print_line(" " * max(0, pad_left) + colored_line)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_int(prompt, default=None):
    while True:
        val = input(f"{C.BLU}▶{C.RST} {prompt}").strip()
        if val == "" and default is not None:
            return default
        try:
            return int(val)
        except ValueError:
            print(f"{C.ERR}  [!] Please enter a valid integer{C.RST}")

def decrypt(p, q, e, c, N, label=""):
    try:
        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        m = pow(c, d, N)
        h = hex(m)[2:]
        if len(h) % 2: h = '0' + h
        Win.text(f"{C.CYN}  [*] Raw hex: {h}{C.RST}")
        result = bytes.fromhex(h).decode(errors='replace')
        Win.text(f"\n{C.GRN}{C.BLD}[+] DECRYPTED ({label}): {result}{C.RST}")
        return result
    except Exception as ex:
        Win.text(f"{C.ERR}  [-] Decrypt failed ({label}): {ex}{C.RST}")
        return None

def int_nth_root(A, n):
    """Finds the integer n-th root of A using a fast binary search."""
    if A < 0: return None
    if A == 0: return 0
    
    high = 1
    while pow(high, n) < A:
        high *= 2
    low = high // 2
    
    while low < high:
        mid = (low + high) // 2
        if pow(mid, n) < A:
            low = mid + 1
        else:
            high = mid
            
    return low if pow(low, n) == A else None

def isqrt_check(n):
    s = math.isqrt(n)
    return s if s*s == n else None

# ============================== ATTACKS ==============================

def attack_even_prime(N, e, c):
    Win.text(f"\n{C.BLU}[*] Trying: Even prime (p=2){C.RST}")
    if N % 2 == 0:
        Win.text(f"{C.CYN}  [!] N is even! p=2{C.RST}")
        p, q = 2, N // 2
        return decrypt(p, q, e, c, N, "even prime")
    else:
        Win.text(f"{C.WRN}  [-] N is odd, skip{C.RST}")
    return None

def attack_gcd_multi(Ns, e, c, target_N):
    Win.text(f"\n{C.BLU}[*] Trying: GCD between multiple N values{C.RST}")
    if len(Ns) < 2:
        Win.text(f"{C.WRN}  [-] Need at least 2 N values, skip{C.RST}")
        return None
    for i in range(len(Ns)):
        for j in range(i+1, len(Ns)):
            g = math.gcd(Ns[i], Ns[j])
            if g > 2:
                Win.text(f"{C.CYN}  [!] GCD(N{i+1}, N{j+1}) = {g}{C.RST}")
                for k, Nk in enumerate(Ns):
                    if Nk % g == 0:
                        p = g
                        q = Nk // g
                        Win.text(f"      Factored N{k+1}: p={p}, q={q}")
                        if Nk == target_N:
                            return decrypt(p, q, e, c, target_N, "GCD multi-N")
            elif g == 2:
                Win.text(f"{C.CYN}  [!] GCD(N{i+1}, N{j+1}) = 2 — all N values are even{C.RST}")
    Win.text(f"{C.WRN}  [-] No shared factors found, skip{C.RST}")
    return None

def attack_fermat(N, e, c, max_iter=1_000_000):
    Win.text(f"\n{C.BLU}[*] Trying: Fermat factorization (max {max_iter} iterations){C.RST}")
    a = math.isqrt(N) + 1
    b2 = a*a - N
    for i in range(max_iter):
        b = isqrt_check(b2)
        if b is not None:
            p, q = a - b, a + b
            if p * q == N and p > 1 and q > 1:
                Win.text(f"{C.CYN}  [!] Fermat worked after {i} iterations{C.RST}")
                return decrypt(p, q, e, c, N, "Fermat")
        a += 1
        b2 = a*a - N
    Win.text(f"{C.WRN}  [-] Fermat did not find factors within iteration limit, skip{C.RST}")
    return None

def attack_small_e(N, e, c):
    Win.text(f"\n{C.BLU}[*] Trying: Small e root / Unpadded RSA{C.RST}")
    
    if e > 100:
        Win.text(f"{C.WRN}  [-] e={e} is quite large, but attempting a quick root check...{C.RST}")
        
    root = int_nth_root(c, e)
    
    if root is not None and pow(root, e) == c:
        try:
            h = hex(root)[2:]
            if len(h) % 2: h = '0' + h
            result = bytes.fromhex(h).decode(errors='replace')
            Win.text(f"{C.CYN}  [!] Perfect {e}-th root found! (m^{e} < N){C.RST}")
            Win.text(f"\n{C.GRN}{C.BLD}[+] DECRYPTED (small e): {result}{C.RST}")
            return result
        except Exception as ex:
            Win.text(f"{C.ERR}  [-] Root found but decode failed: {ex}{C.RST}")
            pass
            
    Win.text(f"{C.WRN}  [-] Root didn't yield plaintext (likely wrapped modulo N), skip{C.RST}")
    return None

def attack_hastads(Ns, cs, e):
    Win.text(f"\n{C.BLU}[*] Trying: Hastads broadcast attack (e=3, 3 ciphertexts){C.RST}")
    if e != 3:
        Win.text(f"{C.WRN}  [-] e={e}, not 3, skip{C.RST}")
        return None
    if len(Ns) < 3 or len(cs) < 3:
        Win.text(f"{C.WRN}  [-] Need at least 3 N values and 3 ciphertexts, skip{C.RST}")
        return None

    N0, N1, N2 = Ns[0], Ns[1], Ns[2]
    c0, c1, c2 = cs[0], cs[1], cs[2]
    M = N0 * N1 * N2
    m0, m1, m2 = M // N0, M // N1, M // N2

    result = (
        c0 * m0 * pow(m0, -1, N0) +
        c1 * m1 * pow(m1, -1, N1) +
        c2 * m2 * pow(m2, -1, N2)
    ) % M

    root = int_nth_root(result, 3)
    if root is None:
        Win.text(f"{C.WRN}  [-] Cube root failed, skip{C.RST}")
        return None

    h = hex(root)[2:]
    if len(h) % 2: h = '0' + h
    try:
        plaintext = bytes.fromhex(h).decode(errors='replace')
        Win.text(f"\n{C.GRN}{C.BLD}[+] DECRYPTED (Hastads): {plaintext}{C.RST}")
        return plaintext
    except Exception as ex:
        Win.text(f"{C.ERR}  [-] Decrypt failed (Hastads): {ex}{C.RST}")
        return None

def attack_common_modulus(Ns, cs, e_list):
    Win.text(f"\n{C.BLU}[*] Trying: Common modulus attack{C.RST}")
    if len(Ns) < 2 or len(cs) < 2 or len(e_list) < 2:
        Win.text(f"{C.WRN}  [-] Need at least 2 N, c, and e values, skip{C.RST}")
        return None

    def extended_gcd(a, b):
        if b == 0: return a, 1, 0
        g, x, y = extended_gcd(b, a % b)
        return g, y, x - (a // b) * y

    for i in range(len(Ns)):
        for j in range(i+1, len(Ns)):
            if Ns[i] == Ns[j]:
                N = Ns[i]
                e1, e2 = e_list[i], e_list[j]
                c1, c2 = cs[i], cs[j]
                if math.gcd(e1, e2) != 1:
                    Win.text(f"{C.WRN}  [-] gcd(e1, e2) != 1, skip{C.RST}")
                    continue
                _, s, t = extended_gcd(e1, e2)
                if s < 0:
                    m = pow(pow(c1, -1, N), -s, N) * pow(c2, t, N) % N
                elif t < 0:
                    m = pow(c1, s, N) * pow(pow(c2, -1, N), -t, N) % N
                else:
                    m = pow(c1, s, N) * pow(c2, t, N) % N
                
                h = hex(m)[2:]
                if len(h) % 2: h = '0' + h
                try:
                    result = bytes.fromhex(h).decode(errors='replace')
                    Win.text(f"\n{C.GRN}{C.BLD}[+] DECRYPTED (common modulus): {result}{C.RST}")
                    return result
                except Exception as ex:
                    Win.text(f"{C.ERR}  [-] Decrypt failed (common modulus): {ex}{C.RST}")
    Win.text(f"{C.WRN}  [-] No matching N values found, skip{C.RST}")
    return None

def hint_factordb(N):
    Win.text(f"\n{C.CYN}[*] Manual step:{C.RST} Paste this N into {C.BLD}https://factordb.com{C.RST}")
    Win.text(f"    N = {N}")
    Win.text(f"    If it returns p and q, use option 2 (known p and q).")

def attack_wiener(N, e, c):
    Win.text(f"\n{C.BLU}[*] Trying: Wiener's attack (large e){C.RST}")
    if e < math.isqrt(math.isqrt(N)):
        Win.text(f"{C.WRN}  [-] e is not large enough for Wiener, skip{C.RST}")
        return None
    try:
        from gmpy2 import isqrt as gmpy_isqrt, mpz
    except ImportError:
        Win.text(f"{C.WRN}  [-] gmpy2 not installed, skipping Wiener (pip install gmpy2){C.RST}")
        return None

    def continued_fraction(e, N):
        cf = []
        while N:
            cf.append(e // N)
            e, N = N, e % N
        return cf

    def convergents(cf):
        convs = []
        for i in range(len(cf)):
            if i == 0: convs.append((cf[0], 1))
            elif i == 1: convs.append((cf[1]*cf[0]+1, cf[1]))
            else:
                h_prev, k_prev = convs[-1]
                h_pprev, k_pprev = convs[-2]
                convs.append((cf[i]*h_prev + h_pprev, cf[i]*k_prev + k_pprev))
        return convs

    cf = continued_fraction(e, N)
    for k, d in convergents(cf):
        if k == 0: continue
        if (e * d - 1) % k != 0: continue
        phi = (e * d - 1) // k
        b = N - phi + 1
        disc = b*b - 4*N
        if disc < 0: continue
        sq = isqrt_check(disc)
        if sq is None: continue
        p = (b + sq) // 2
        q = (b - sq) // 2
        if p * q == N:
            Win.text(f"{C.CYN}  [!] Wiener worked: d={d}{C.RST}")
            m = pow(c, d, N)
            h = hex(m)[2:]
            if len(h) % 2: h = '0' + h
            try:
                result = bytes.fromhex(h).decode(errors='replace')
                Win.text(f"\n{C.GRN}{C.BLD}[+] DECRYPTED (Wiener): {result}{C.RST}")
                return result
            except Exception as ex:
                Win.text(f"{C.ERR}  [-] Decrypt failed (Wiener): {ex}{C.RST}")
                return None
    Win.text(f"{C.WRN}  [-] Wiener failed, skip{C.RST}")
    return None

def decrypt_known(e, c, N):
    Win.top("DECRYPT WITH KNOWN P AND Q")
    Win.text("Provide prime factors below.")
    Win.bot()
    p = get_int("p = ")
    q = get_int("q = ")
    
    Win.top("RESULTS")
    res = decrypt(p, q, e, c, N, "known factors")
    Win.bot()
    return res

# ============================== INPUT MENU ==============================

def get_inputs():
    Win.top("DATA INPUT")
    Win.text(f"{C.WRN}Provide your variables. Leave e blank for 65537.{C.RST}")
    Win.bot()
    
    N = get_int("N = ")
    e = get_int("e (default 65537) = ", default=65537)
    c = get_int("c = ")

    MULTI_N = [N]
    MULTI_C = [c]
    E_LIST = [e]

    Win.top("MULTIPLE CIPHERTEXTS")
    Win.text(f"Do you have multiple ciphertexts? (y/n)")
    Win.bot()
    
    if input(f"{C.BLU}▶{C.RST} ").strip().lower() == "y":
        Win.top("COMMON MODULUS")
        Win.text(f"Is this common modulus? (same N, different e) (y/n)")
        Win.bot()
        
        if input(f"{C.BLU}▶{C.RST} ").strip().lower() == "y":
            c2 = get_int("c2 = ")
            e2 = get_int("e2 = ")
            MULTI_N.append(N)
            MULTI_C.append(c2)
            E_LIST.append(e2)
        else:
            Win.top("EXTRA PAIRS")
            Win.text("Enter additional N and c pairs. Blank line to stop:")
            Win.bot()
            while True:
                n_line = input(f"{C.BLU}▶{C.RST} N = ").strip()
                if n_line == "": break
                c_line = input(f"{C.BLU}▶{C.RST} c = ").strip()
                try:
                    MULTI_N.append(int(n_line))
                    MULTI_C.append(int(c_line))
                    E_LIST.append(e)
                except ValueError:
                    print(f"{C.ERR}  [!] Invalid input, skipping pair{C.RST}")

    return N, e, c, MULTI_N, MULTI_C, E_LIST

# ============================== SYMMETRIC CRYPTO ==============================

def ask(question, options):
    Win.top("CHOOSE OPTION")
    Win.text(f"{C.WRN}{question}{C.RST}")
    Win.div()
    for i, opt in enumerate(options):
        Win.text(f"  {C.CYN}{i+1}.{C.RST} {opt}")
    Win.text(f"  {C.CYN}q.{C.RST} Back")
    Win.bot()
    while True:
        val = input(f"{C.BLU}▶{C.RST} Choice: ").strip().lower()
        if val == 'q':
            return None
        try:
            idx = int(val) - 1
            if 0 <= idx < len(options):
                return idx
            print(f"{C.ERR}  [!] Invalid choice{C.RST}")
        except ValueError:
            print(f"{C.ERR}  [!] Enter a number{C.RST}")

def generate_ecb_template():
    Win.top("ECB BYTE-AT-A-TIME")
    Win.text(f"{C.WRN}Template generation for ECB coming soon...{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter to return...{C.RST}")

def generate_padding_oracle_template():
    Win.top("PADDING ORACLE CONFIG")
    Win.text("Provide the target details to bake into the script.")
    Win.bot()
    
    host = input(f"{C.BLU}▶{C.RST} Target IP/Domain (e.g., 10.10.10.5): ").strip()
    port = get_int("Target Port (e.g., 1337) = ")
    cipher_hex = input(f"{C.BLU}▶{C.RST} Target Ciphertext (Hex): ").strip()
    block_size = get_int("Block Size (default 16) = ", default=16)

    Win.top("GENERATING SCRIPT")
    Win.text("Writing cbc_padding_oracle.py to current directory...")
    Win.bot()
    
    template = f"""from pwn import *
import binascii
import time

# --- TARGET CONFIGURATION ---
HOST = '{host}'
PORT = {port}
CIPHERTEXT_HEX = '{cipher_hex}'
BLOCK_SIZE = {block_size}

def oracle(ciphertext_bytes):
    # Connect to the remote server
    # r = remote(HOST, PORT, level='error')
    
    # Send the modified ciphertext (format based on CTF)
    # r.sendlineafter(b'> ', binascii.hexlify(ciphertext_bytes))
    
    # Read the response and check for padding error
    # response = r.recvall(timeout=1)
    # r.close()
    
    # RETURN TRUE if padding is VALID, FALSE if padding is INVALID
    # return b"Padding Error" not in response
    pass

# --- HEAVY CRYPTO LOGIC ---
def split_blocks(data, size):
    return [data[i:i+size] for i in range(0, len(data), size)]

def decrypt_block(prev_block, cipher_block):
    decrypted = bytearray(BLOCK_SIZE)
    intermediate = bytearray(BLOCK_SIZE)
    
    for byte_idx in range(BLOCK_SIZE - 1, -1, -1):
        padding_val = BLOCK_SIZE - byte_idx
        
        # Prepare the malicious previous block
        malicious_block = bytearray(BLOCK_SIZE)
        for i in range(byte_idx + 1, BLOCK_SIZE):
            malicious_block[i] = intermediate[i] ^ padding_val
            
        # Bruteforce the current byte
        valid_byte_found = False
        for guess in range(256):
            malicious_block[byte_idx] = guess
            
            # Anti-ban safety delay (adjust as needed for CTF rules)
            time.sleep(0.05)
            
            # Ask the oracle if this modified block + target block has valid padding
            if oracle(malicious_block + cipher_block):
                intermediate[byte_idx] = guess ^ padding_val
                decrypted[byte_idx] = intermediate[byte_idx] ^ prev_block[byte_idx]
                print(f"[+] Found byte {{byte_idx}}: {{chr(decrypted[byte_idx])}}")
                valid_byte_found = True
                break
                
        if not valid_byte_found:
            print(f"[-] Failed to find byte at index {{byte_idx}}")
            return None
            
    return decrypted

if __name__ == '__main__':
    print("[*] Starting CBC Padding Oracle Attack...")
    target_bytes = bytes.fromhex(CIPHERTEXT_HEX)
    blocks = split_blocks(target_bytes, BLOCK_SIZE)
    
    plaintext = b""
    for i in range(1, len(blocks)):
        print(f"[*] Decrypting Block {{i}}...")
        dec = decrypt_block(blocks[i-1], blocks[i])
        if dec:
            plaintext += dec
        else:
            print("[-] Decryption aborted.")
            break
            
    print(f"\\n[+] FINAL PLAINTEXT: {{plaintext}}")
"""
    try:
        with open("cbc_padding_oracle.py", "w") as f:
            f.write(template)
        Win.text(f"  {C.GRN}[+] cbc_padding_oracle.py written successfully!{C.RST}")
        Win.text(f"  {C.WRN}[!] Edit the 'oracle()' function inside the script to match the CTF.{C.RST}")
    except Exception as e:
        Win.text(f"  {C.ERR}[-] Failed to write file: {e}{C.RST}")
        
    Win.bot()
    input(f"\n{C.CYN}Press Enter to continue...{C.RST}")

def step_symmetric_menu():
    while True:
        clear_screen()
        Win.top("SYMMETRIC CRYPTO (AES/DES)")
        Win.text("What kind of access or vulnerability do you suspect?")
        Win.bot()
        
        choice = ask(
            "Choose an attack vector:",
            [
                "ECB Byte-at-a-Time (I control input, output length changes)",
                "CBC Padding Oracle (Server returns 'Invalid Padding' errors)",
                "CBC Bit-Flipping (Change 'user' to 'admin' in a token)"
            ]
        )
        
        if choice is None:
            break
        elif choice == 0:
            generate_ecb_template()
        elif choice == 1:
            generate_padding_oracle_template()
        elif choice == 2:
            Win.top("CBC BIT-FLIPPING")
            Win.text(f"{C.WRN}Template generation coming soon...{C.RST}")
            Win.bot()
            input(f"\n{C.CYN}Press Enter to return...{C.RST}")

# ============================== ASYMMETRIC HUB ==============================

def step_rsa_menu():
    while True:
        clear_screen()
        Win.top("RSA / ASYMMETRIC (GAMBIT CORE)")
        Win.div("MENU")
        Win.text(f"  {C.CYN}1.{C.RST} Run all automated attacks (Fermat, Wiener, Hastads, etc)")
        Win.text(f"  {C.CYN}2.{C.RST} Decrypt with known p and q")
        Win.text(f"  {C.CYN}3.{C.RST} Hint: look up N on factordb")
        Win.text(f"  {C.CYN}q.{C.RST} Back to Asymmetric menu")
        Win.bot()

        choice = input(f"\n{C.BLD}Choice:{C.RST} ").strip().lower()

        if choice == "q":
            break
        elif choice == "1":
            N, e, c, MULTI_N, MULTI_C, E_LIST = get_inputs()
            clear_screen()
            Win.top("RESULTS")
            result = (
                attack_even_prime(N, e, c) or
                attack_small_e(N, e, c) or
                attack_hastads(MULTI_N, MULTI_C, e) or
                attack_common_modulus(MULTI_N, MULTI_C, E_LIST) or
                attack_gcd_multi(MULTI_N, e, c, N) or
                attack_fermat(N, e, c) or
                attack_wiener(N, e, c)
            )
            if not result:
                Win.text(f"\n{C.ERR}[-] No automatic attack worked.{C.RST}")
                hint_factordb(N)
            Win.bot()
            input(f"\n{C.CYN}Press Enter to return...{C.RST}")
        elif choice == "2":
            Win.top("DATA INPUT")
            Win.text("Provide standard parameters.")
            Win.bot()
            N = get_int("N = ")
            e = get_int("e (default 65537) = ", default=65537)
            c = get_int("c = ")
            decrypt_known(e, c, N)
            input(f"\n{C.CYN}Press Enter to return...{C.RST}")
        elif choice == "3":
            Win.top("DATA INPUT")
            Win.text("Provide modulus N.")
            Win.bot()
            N = get_int("N = ")
            Win.top("HINT")
            hint_factordb(N)
            Win.bot()
            input(f"\n{C.CYN}Press Enter to return...{C.RST}")
        else:
            print(f"{C.ERR}  [!] Invalid choice{C.RST}")

def step_asymmetric_menu():
    while True:
        clear_screen()
        Win.top("ASYMMETRIC CRYPTOGRAPHY")
        Win.div("DOMAINS")
        Win.text(f"  {C.CYN}1.{C.RST} RSA (Factoring, Wiener, Hastads, etc.)")
        Win.text(f"  {C.CYN}2.{C.RST} Elliptic Curve (ECC) - Invalid Curve, Nonce Reuse")
        Win.text(f"  {C.CYN}3.{C.RST} Diffie-Hellman / ElGamal (Discrete Log, Smooth Primes)")
        Win.bot()
        
        choice = ask("Select a target system:", ["RSA", "ECC", "Diffie-Hellman / ElGamal"])
        if choice is None:
            break
        elif choice == 0:
            step_rsa_menu() # Now correctly routes to the RSA hub above
        elif choice == 1:
            Win.top("ECC TEMPLATES")
            Win.text(f"{C.WRN}Note: ECC is best solved using SageMath, not standard Python.{C.RST}")
            Win.bot()
            input(f"\n{C.CYN}Press Enter to return...{C.RST}")
        elif choice == 2:
            Win.top("DH / ELGAMAL")
            Win.text(f"{C.WRN}Template generation coming soon...{C.RST}")
            Win.bot()
            input(f"\n{C.CYN}Press Enter to return...{C.RST}")

def score_text(text):
    """Scores a string based on English character frequencies."""
    english_freq = {
        'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253,
        'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094,
        'i': 0.06966, 'j': 0.00015, 'k': 0.00772, 'l': 0.04025,
        'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929,
        'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
        'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150,
        'y': 0.01974, 'z': 0.00074, ' ': 0.13000
    }
    score = 0
    for char in text.lower():
        if char in english_freq:
            score += english_freq[char]
    return score

def attack_single_byte_xor():
    Win.top("SINGLE-BYTE XOR BRUTEFORCE")
    Win.text("Attempts all 256 possible byte keys and ranks them by English frequency.")
    Win.bot()
    
    ct_hex = input(f"{C.BLU}▶{C.RST} Ciphertext (Hex): ").strip()
    try:
        ct_bytes = bytes.fromhex(ct_hex)
    except ValueError:
        print(f"{C.ERR}  [!] Invalid hex string.{C.RST}")
        input(f"\n{C.CYN}Press Enter to return...{C.RST}")
        return

    results = []
    for key in range(256):
        decrypted = bytes([b ^ key for b in ct_bytes])
        try:
            dec_str = decrypted.decode('ascii')
            score = score_text(dec_str)
            results.append((score, key, dec_str))
        except UnicodeDecodeError:
            continue # Skip garbage bytes that aren't valid ASCII

    results.sort(reverse=True, key=lambda x: x[0])

    Win.top("TOP 5 LIKELY RESULTS")
    if not results:
        Win.text(f"{C.ERR}[-] No valid ASCII outputs found.{C.RST}")
    else:
        for i in range(min(5, len(results))):
            score, key, text = results[i]
            Win.text(f"  {C.CYN}Key: 0x{key:02x}{C.RST} | {C.GRN}{text[:60]}{'...' if len(text)>60 else ''}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter to return...{C.RST}")

def attack_crib_drag():
    Win.top("XOR CRIB DRAGGING")
    Win.text("Slides a known plaintext (crib) across the ciphertext.")
    Win.text("Useful for Many-Time Pad / Nonce Reuse attacks.")
    Win.bot()
    
    ct_hex = input(f"{C.BLU}▶{C.RST} Ciphertext (Hex): ").strip()
    crib_str = input(f"{C.BLU}▶{C.RST} Crib (Known Plaintext): ").strip()
    
    try:
        ct_bytes = bytes.fromhex(ct_hex)
        crib_bytes = crib_str.encode('ascii')
    except ValueError:
        print(f"{C.ERR}  [!] Invalid input formats.{C.RST}")
        input(f"\n{C.CYN}Press Enter to return...{C.RST}")
        return

    if len(crib_bytes) > len(ct_bytes):
        print(f"{C.ERR}  [!] Crib cannot be longer than the ciphertext.{C.RST}")
        input(f"\n{C.CYN}Press Enter to return...{C.RST}")
        return

    Win.top("CRIB DRAG RESULTS")
    Win.text("Showing printable results where the XOR yields valid ASCII:")
    Win.div()
    
    found_any = False
    for i in range(len(ct_bytes) - len(crib_bytes) + 1):
        ct_slice = ct_bytes[i:i+len(crib_bytes)]
        xored = bytes([a ^ b for a, b in zip(ct_slice, crib_bytes)])
        
        # Check if the result is mostly printable
        if all(32 <= b <= 126 for b in xored):
            Win.text(f"  {C.CYN}Pos {i:02d}:{C.RST} {C.GRN}{xored.decode('ascii')}{C.RST}")
            found_any = True

    if not found_any:
         Win.text(f"  {C.WRN}No fully printable ASCII blocks found during drag.{C.RST}")
            
    Win.bot()
    input(f"\n{C.CYN}Press Enter to return...{C.RST}")

# ============================== STREAM CIPHER ==============================

def step_stream_menu():
    while True:
        clear_screen()
        Win.top("STREAM CIPHERS & XOR")
        Win.text("Stream ciphers (including CTR mode) are basically complex XOR.")
        Win.bot()
        
        Win.top("CHOOSE OPTION")
        Win.text("Select an attack vector:")
        Win.div()
        Win.text(f"  {C.CYN}1.{C.RST} XOR: Single-byte bruteforce")
        Win.text(f"  {C.CYN}2.{C.RST} XOR: Crib Dragging (Known Plaintext)")
        Win.text(f"  {C.CYN}3.{C.RST} AES-CTR / ChaCha20: Nonce Reuse (Turns into XOR)")
        Win.text(f"  {C.CYN}4.{C.RST} AES-CTR / ChaCha20: Bit-flipping")
        Win.text(f"  {C.CYN}q.{C.RST} Back")
        Win.bot()
        
        choice = input(f"\n{C.BLD}Choice:{C.RST} ").strip().lower()
        if choice == 'q': 
            break
        elif choice == '1':
            attack_single_byte_xor()
        elif choice == '2':
            attack_crib_drag()
        elif choice in ['3', '4']:
            Win.top("ADVANCED STREAM CIPHERS")
            Win.text(f"{C.WRN}Note: Nonce reuse and bit-flipping rely heavily on the exact{C.RST}")
            Win.text(f"{C.WRN}structure of the CTF challenge (JSON, cookies, etc).{C.RST}")
            Win.text("Use the Crib Drag tool above to extract keys if nonce is reused.")
            Win.bot()
            input(f"\n{C.CYN}Press Enter to return...{C.RST}")
        else:
            print(f"{C.ERR}  [!] Invalid choice{C.RST}")

# ============================== CLASSICAL ==============================

def calculate_ioc(text):
    """Calculates the Index of Coincidence to predict cipher family."""
    alpha_ct = ''.join(c for c in text if c.isalpha()).upper()
    n = len(alpha_ct)
    if n <= 1: return 0, 0
    counts = collections.Counter(alpha_ct).values()
    ioc = sum(c * (c - 1) for c in counts) / (n * (n - 1))
    return ioc, n

def identify_classical():
    Win.top("CLASSICAL IDENTIFIER (RANKED)")
    Win.text("Analyzes mathematical frequency to predict the cipher type.")
    Win.bot()
    
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip()
    if not ct: return
    
    ioc, n = calculate_ioc(ct)
    if n == 0:
        Win.text(f"{C.ERR}  [-] No alphabetic characters found.{C.RST}")
        return
        
    Win.top("ANALYSIS RESULTS")
    Win.text(f"  Length: {n} chars | Calculated IoC: {ioc:.4f}")
    Win.div("LIKELY CIPHERS (RANKED)")
    
    if ioc > 0.060:
        Win.text(f"  {C.GRN}1. Monoalphabetic (Caesar/ROT/Atbash){C.RST}")
        Win.text(f"     Single alphabet mapping; highest statistical match.")
        Win.text(f"  {C.CYN}2. Transposition (Rail Fence/Columnar){C.RST}")
        Win.text(f"     Order is scrambled but letter frequency remains identical.")
        Win.text(f"  {C.CYN}3. Affine{C.RST}")
        Win.text(f"     Linear mathematical substitution (ax + b).")
    elif ioc < 0.048:
        Win.text(f"  {C.GRN}1. Polyalphabetic (Vigenère/Beaufort){C.RST}")
        Win.text(f"     Multiple alphabets used to flatten frequency spikes.")
        Win.text(f"  {C.CYN}2. Autokey{C.RST}")
        Win.text(f"     Sophisticated polyalphabetic cipher using message as key.")
    else:
        Win.text(f"  {C.GRN}1. Digraph/Matrix (Playfair/Hill){C.RST}")
        Win.text(f"     Encryption of letter pairs or blocks; typical mid-range IoC.")
        Win.text(f"  {C.CYN}2. Short Text Variance{C.RST}")
        Win.text(f"     IoC is less reliable with samples under 50 characters.")
        
    Win.bot()
    input(f"\n{C.CYN}Press Enter to return...{C.RST}")

def solve_caesar():
    Win.top("CAESAR / ROT BRUTEFORCE")
    Win.text("Prints all 25 possible shifts.")
    Win.bot()
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip()
    if not ct: return
    Win.top("RESULTS")
    for shift in range(1, 26):
        pt = ""
        for char in ct:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                pt += chr((ord(char) - base - shift) % 26 + base)
            else: pt += char
        Win.text(f"  {C.CYN}ROT-{shift:<2}{C.RST} : {C.GRN}{pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter to return...{C.RST}")

def solve_vigenere():
    Win.top("VIGENÈRE DECRYPT")
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip()
    key = input(f"{C.BLU}▶{C.RST} Key: ").strip().upper()
    if not ct or not key: return
    pt, key_idx = "", 0
    for char in ct:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shift = ord(key[key_idx % len(key)]) - ord('A')
            pt += chr((ord(char) - base - shift) % 26 + base)
            key_idx += 1
        else: pt += char
    Win.text(f"  {C.GRN}[+] RESULT: {pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter to return...{C.RST}")

def solve_atbash():
    Win.top("ATBASH SOLVER")
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip()
    pt = "".join(chr(ord('A') + (25 - (ord(c.upper()) - ord('A')))) if c.isalpha() else c for c in ct)
    Win.text(f"  {C.GRN}[+] RESULT: {pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter to return...{C.RST}")

def solve_affine():
    Win.top("AFFINE DECRYPT")
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip().upper()
    a, b = get_int("Value 'a' (multiplicative): "), get_int("Value 'b' (additive): ")
    a_inv = next((i for i in range(26) if (a * i) % 26 == 1), -1)
    if a_inv == -1:
        Win.text(f"{C.ERR}  [-] 'a'={a} has no modular inverse. Invalid key.{C.RST}")
        return
    pt = "".join(chr(((a_inv * ((ord(c) - ord('A')) - b)) % 26) + ord('A')) if c.isalpha() else c for c in ct)
    Win.text(f"  {C.GRN}[+] RESULT: {pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter to return...{C.RST}")

def solve_playfair():
    Win.top("PLAYFAIR DECRYPT")
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip().upper().replace('J', 'I')
    ct = ''.join(filter(str.isalpha, ct))
    key = input(f"{C.BLU}▶{C.RST} Key: ").strip().upper().replace('J', 'I')
    if not ct or len(ct) % 2 != 0:
        Win.text(f"{C.ERR}  [-] Ciphertext must be even length.{C.RST}")
        return
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    m_str = "".join(collections.OrderedDict.fromkeys(key + alphabet))
    matrix = [list(m_str[i:i+5]) for i in range(0, 25, 5)]
    def get_pos(char):
        for r in range(5):
            for c in range(5):
                if matrix[r][c] == char: return r, c
    pt = ""
    for i in range(0, len(ct), 2):
        r1, c1 = get_pos(ct[i])
        r2, c2 = get_pos(ct[i+1])
        if r1 == r2: pt += matrix[r1][(c1-1)%5] + matrix[r2][(c2-1)%5]
        elif c1 == c2: pt += matrix[(r1-1)%5][c1] + matrix[(r2-1)%5][c2]
        else: pt += matrix[r1][c2] + matrix[r2][c1]
    Win.text(f"  {C.GRN}[+] RESULT: {pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter...{C.RST}")

def solve_hill_2x2():
    Win.top("HILL CIPHER (2x2)")
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip().upper()
    a, b, c, d = get_int("M[0,0]: "), get_int("M[0,1]: "), get_int("M[1,0]: "), get_int("M[1,1]: ")
    det = (a * d - b * c) % 26
    det_inv = next((i for i in range(26) if (det * i) % 26 == 1), -1)
    if det_inv == -1:
        Win.text(f"{C.ERR}  [-] Determinant {det} is not invertible.{C.RST}")
        return
    ka, kb, kc, kd = (d*det_inv)%26, (-b*det_inv)%26, (-c*det_inv)%26, (a*det_inv)%26
    pt = ""
    for i in range(0, len(ct), 2):
        v1, v2 = ord(ct[i]) - ord('A'), ord(ct[i+1]) - ord('A')
        pt += chr((ka * v1 + kb * v2) % 26 + ord('A'))
        pt += chr((kc * v1 + kd * v2) % 26 + ord('A'))
    Win.text(f"  {C.GRN}[+] RESULT: {pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter...{C.RST}")

def solve_hill_3x3():
    Win.top("HILL CIPHER (3x3)")
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip().upper()
    m = [[get_int(f"M[{i},{j}]: ") for j in range(3)] for i in range(3)]
    det = (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0]) + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])) % 26
    det_inv = next((i for i in range(26) if (det * i) % 26 == 1), -1)
    if det_inv == -1:
        Win.text(f"{C.ERR}  [-] Determinant {det} is not invertible.{C.RST}")
        return
    def get_minor(r, c):
        items = [m[i][j] for i in range(3) for j in range(3) if i != r and j != c]
        return (items[0]*items[3] - items[1]*items[2])
    inv_m = [[0]*3 for _ in range(3)]
    for r in range(3):
        for c in range(3):
            sign = 1 if (r + c) % 2 == 0 else -1
            inv_m[c][r] = (sign * get_minor(r, c) * det_inv) % 26
    pt = ""
    for i in range(0, len(ct), 3):
        v = [ord(ct[i+j]) - ord('A') for j in range(3)]
        for r in range(3):
            pt += chr(sum(inv_m[r][k] * v[k] for k in range(3)) % 26 + ord('A'))
    Win.text(f"  {C.GRN}[+] RESULT: {pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter...{C.RST}")

def solve_railfence():
    Win.top("RAIL FENCE DECRYPT")
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip()
    rails = get_int("Rails: ")
    fence = [['\n' for _ in range(len(ct))] for _ in range(rails)]
    rail, direction = 0, 1
    for i in range(len(ct)):
        fence[rail][i] = '*'
        rail += direction
        if rail == 0 or rail == rails - 1: direction *= -1
    idx = 0
    for r in range(rails):
        for c in range(len(ct)):
            if fence[r][c] == '*':
                fence[r][c], idx = ct[idx], idx + 1
    pt, rail, direction = "", 0, 1
    for i in range(len(ct)):
        pt += fence[rail][i]
        rail += direction
        if rail == 0 or rail == rails - 1: direction *= -1
    Win.text(f"  {C.GRN}[+] RESULT: {pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter...{C.RST}")

def solve_columnar():
    Win.top("COLUMNAR TRANSPOSITION")
    ct = input(f"{C.BLU}▶{C.RST} Ciphertext: ").strip()
    key = input(f"{C.BLU}▶{C.RST} Key: ").strip()
    col_len, row_len = len(key), math.ceil(len(ct) / len(key))
    key_indices = sorted(range(col_len), key=lambda k: key[k])
    matrix = [['' for _ in range(col_len)] for _ in range(row_len)]
    idx = 0
    for col in key_indices:
        for row in range(row_len):
            if idx < len(ct):
                matrix[row][col], idx = ct[idx], idx + 1
    pt = "".join("".join(row) for row in matrix)
    Win.text(f"  {C.GRN}[+] RESULT: {pt}{C.RST}")
    Win.bot()
    input(f"\n{C.CYN}Press Enter...{C.RST}")

def step_classical_menu():
    while True:
        clear_screen()
        Win.top("CLASSICAL HUB")
        Win.text("Letter-level swapping and reordering.")
        Win.bot()

        Win.top("CHOOSE OPTION")
        Win.text("Select an action or solver:")
        Win.div()
        Win.text(f"  {C.CYN}1.{C.RST} Identify Cipher (Ranked IoC)")
        Win.text(f"  {C.CYN}2.{C.RST} Caesar / ROT (Bruteforce)")
        Win.text(f"  {C.CYN}3.{C.RST} Vigenère (Known Key)")
        Win.text(f"  {C.CYN}4.{C.RST} Atbash / Affine")
        Win.text(f"  {C.CYN}5.{C.RST} Playfair")
        Win.text(f"  {C.CYN}6.{C.RST} Hill Cipher (2x2 / 3x3)")
        Win.text(f"  {C.CYN}7.{C.RST} Transposition (Rail Fence / Columnar)")
        Win.text(f"  {C.CYN}q.{C.RST} Back")
        Win.bot()
        
        choice = input(f"\n{C.BLD}Choice:{C.RST} ").strip().lower()
        if choice == 'q': break
        elif choice == '1': identify_classical()
        elif choice == '2': solve_caesar()
        elif choice == '3': solve_vigenere()
        elif choice == '4':
            sub = ask("Select Type:", ["Atbash (A=Z)", "Affine (ax + b)"])
            if sub == 0: solve_atbash()
            elif sub == 1: solve_affine()
        elif choice == '5': solve_playfair()
        elif choice == '6':
            sub = ask("Dimension:", ["2x2 Matrix", "3x3 Matrix"])
            if sub == 0: solve_hill_2x2()
            elif sub == 1: solve_hill_3x3()
        elif choice == '7':
            sub = ask("Transposition:", ["Rail Fence (Zigzag)", "Columnar"])
            if sub == 0: solve_railfence()
            elif sub == 1: solve_columnar()

# ============================== MAIN MENU ==============================

def main():
    while True:
        clear_screen()
        Win.top("")
        print_rainbow_banner(GAMBIT_BANNER)
        Win.div("DOMAINS")
        Win.text(f"  {C.CYN}1.{C.RST} Asymmetric (RSA, ECC, Diffie-Hellman)")
        Win.text(f"  {C.CYN}2.{C.RST} Symmetric Block Ciphers (AES ECB/CBC)")
        Win.text(f"  {C.CYN}3.{C.RST} Symmetric Stream Ciphers (XOR, CTR, ChaCha20)")
        Win.text(f"  {C.CYN}4.{C.RST} Classical & Matrix (Caesar, Vigenere, Hill, Playfair)")
        Win.text(f"  {C.CYN}q.{C.RST} Quit")
        Win.bot()

        choice = input(f"\n{C.BLD}Choice:{C.RST} ").strip().lower()

        if choice == 'q':
            break
        elif choice == '1':
            step_asymmetric_menu()
        elif choice == '2':
            step_symmetric_menu()
        elif choice == '3':
            step_stream_menu()
        elif choice == '4':
            step_classical_menu()

if __name__ == "__main__":
    main()