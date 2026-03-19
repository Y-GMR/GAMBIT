import math
import os
import re

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

def int_cbrt(n):
    if n < 0: return -int_cbrt(-n)
    if n == 0: return 0
    try:
        from gmpy2 import iroot
        root, exact = iroot(n, 3)
        return int(root) if exact else None
    except ImportError:
        pass
    x = int(round(n ** (1/3)))
    x = max(x, 1)
    while True:
        x1 = (2 * x + n // (x * x)) // 3
        if x1 >= x: break
        x = x1
    for i in [x-1, x, x+1]:
        if i > 0 and i**3 == n: return i
    return None

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
    Win.text(f"\n{C.BLU}[*] Trying: Small e cube root (e=3){C.RST}")
    if e != 3:
        Win.text(f"{C.WRN}  [-] e={e}, not 3, skip{C.RST}")
        return None
    root = int_cbrt(c)
    if root is not None and pow(root, 3) == c:
        try:
            h = hex(root)[2:]
            if len(h) % 2: h = '0' + h
            result = bytes.fromhex(h).decode(errors='replace')
            Win.text(f"{C.CYN}  [!] Cube root worked (message was tiny){C.RST}")
            Win.text(f"\n{C.GRN}{C.BLD}[+] DECRYPTED (small e): {result}{C.RST}")
            return result
        except:
            pass
    Win.text(f"{C.WRN}  [-] Cube root didn't yield plaintext, skip{C.RST}")
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

    root = int_cbrt(result)
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

# ============================== MAIN MENU ==============================

def main():
    while True:
        clear_screen()
        Win.top("")
        print_rainbow_banner(GAMBIT_BANNER)
        Win.div("MENU")
        Win.text(f"  {C.CYN}1.{C.RST} Run all attacks")
        Win.text(f"  {C.CYN}2.{C.RST} Decrypt with known p and q")
        Win.text(f"  {C.CYN}3.{C.RST} Hint: look up N on factordb")
        Win.text(f"  {C.CYN}q.{C.RST} Quit")
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

        elif choice == "2":
            Win.top("DATA INPUT")
            Win.text("Provide standard parameters.")
            Win.bot()
            N = get_int("N = ")
            e = get_int("e (default 65537) = ", default=65537)
            c = get_int("c = ")
            decrypt_known(e, c, N)

        elif choice == "3":
            Win.top("DATA INPUT")
            Win.text("Provide modulus N.")
            Win.bot()
            N = get_int("N = ")
            Win.top("HINT")
            hint_factordb(N)
            Win.bot()

        else:
            print(f"{C.ERR}  [!] Invalid choice{C.RST}")

        input(f"\n{C.CYN}Press Enter to return to menu...{C.RST}")

if __name__ == "__main__":
    main()