import math
import random
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

FORGE_BANNER = r"""
 
   ██████╗  █████╗ ███╗   ███╗██████╗ ██╗████████╗
  ██╔════╝ ██╔══██╗████╗ ████║██╔══██╗██║╚══██╔══╝
██║  ███╗███████║██╔████╔██║██████╔╝██║   ██║   
██║   ██║██╔══██║██║╚██╔╝██║██╔══██╗██║   ██║   
╚██████╔╝██║  ██║██║ ╚═╝ ██║██████╔╝██║   ██║   
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝  
                                           *create
"""

def print_rainbow_banner(text):
    lines = [line.replace('\xa0', ' ').rstrip() for line in text.strip('\n').split('\n')]
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

def get_int(prompt):
    while True:
        try:
            return int(input(f"{C.BLU}▶{C.RST} {prompt}").strip())
        except ValueError:
            print(f"{C.ERR}  [!] Enter a valid integer{C.RST}")

def get_msg():
    return input(f"{C.BLU}▶{C.RST} Enter message to encrypt (default: flag{{test}}): ").strip() or "flag{test}"

def get_alpha_msg():
    """Get a message and strip non-alpha for classical ciphers."""
    msg = input(f"{C.BLU}▶{C.RST} Enter message (letters only, default: FLAGTEST): ").strip().upper() or "FLAGTEST"
    alpha = ''.join(c for c in msg if c.isalpha())
    if alpha != msg:
        print(f"{C.WRN}  [*] Non-alpha chars stripped. Using: {alpha}{C.RST}")
    return alpha

def encode_msg(msg):
    return int.from_bytes(msg.encode(), "big")

def encrypt(m, e, n):
    return pow(m, e, n)

def is_prime(n, k=20):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def next_prime(n):
    n += 1 if n % 2 == 0 else 2
    while not is_prime(n):
        n += 2
    return n

def print_output(label, inputs, ciphertext, plaintext, notes=None):
    """Standard output box for all scenarios."""
    Win.top("GENERATED OUTPUT")
    if notes:
        for note in notes:
            Win.text(f"{C.WRN}{note}{C.RST}")
        Win.div()
    for k, v in inputs.items():
        Win.text(f"{k} = {v}")
    Win.text(" ")
    Win.text(f"Ciphertext = {C.GRN}{ciphertext}{C.RST}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{plaintext}{C.RST}")
    Win.bot()

# ============================== RSA SCENARIOS ==============================

def scenario_even_prime():
    Win.top("EVEN PRIME (p=2)")
    Win.text("p = 2, causing n to be an even number.")
    Win.text(f"{C.WRN}Provide q (any prime number) {C.RST}")
    Win.bot()
    
    q = get_int("q = ")
    if not is_prime(q):
        print(f"{C.ERR}  [!] Warning: {q} is not prime, results may be wrong{C.RST}")
    msg = get_msg()

    p = 2
    n = p * q
    e = 65537
    phi = (p-1)*(q-1)
    d = pow(e, -1, phi)
    m = encode_msg(msg)
    if m >= n:
        print(f"{C.ERR}  [!] Message too long for this n, use shorter message{C.RST}")
        return
    c = encrypt(m, e, n)
    
    Win.top("GENERATED OUTPUT")
    Win.text(f"n = {n}")
    Win.text(f"e = {e}")
    Win.text(f"c = {c}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.text(" ")
    Win.text(f"{C.CYN}RsaCtfTool command:{C.RST}")
    Win.text(f"RsaCtfTool -n {n} -e {e} --decrypt {c} --attack all")
    Win.bot()

def scenario_small_e():
    Win.top("SMALL E (e=3)")
    Win.text("Message is tiny so c = m^3 < n.")
    Win.text(f"{C.WRN}Provide p and q (large primes).{C.RST}")
    Win.bot()
    
    p = get_int("p = ")
    q = get_int("q = ")
    if not is_prime(p) or not is_prime(q):
        print(f"{C.ERR}  [!] Warning: p or q may not be prime{C.RST}")
    msg = get_msg()

    n = p * q
    e = 3
    phi = (p-1)*(q-1)
    try:
        d = pow(e, -1, phi)
    except Exception:
        print(f"{C.ERR}  [!] gcd(e, phi) != 1, choose different p/q{C.RST}")
        return
    m = encode_msg(msg)
    if m >= n:
        print(f"{C.ERR}  [!] Message too long for this n{C.RST}")
        return
    c = encrypt(m, e, n)

    Win.top("GENERATED OUTPUT")
    if c == pow(m, 3):
        Win.text(f"{C.GRN}[+] m^3 < n, cube root attack will work directly{C.RST}")
    else:
        Win.text(f"{C.ERR}[!] m^3 >= n (wraps around modulus), cube root attack may not work{C.RST}")
    Win.div()
    Win.text(f"n = {n}")
    Win.text(f"e = {e}")
    Win.text(f"c = {c}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.text(" ")
    Win.text(f"{C.CYN}RsaCtfTool command:{C.RST}")
    Win.text(f"RsaCtfTool -n {n} -e {e} --decrypt {c} --attack all")
    Win.bot()

def scenario_fermat():
    Win.top("FERMAT FACTORIZATION")
    Win.text("p and q are very close together.")
    Win.text(f"{C.WRN}Provide a starting prime p, q will be the next prime after p.{C.RST}")
    Win.bot()
    
    p = get_int("p = ")
    if not is_prime(p):
        p = next_prime(p)
        print(f"{C.CYN}  [*] Adjusted to nearest prime: p = {p}{C.RST}")
    msg = get_msg()

    q = next_prime(p)
    n = p * q
    e = 65537
    phi = (p-1)*(q-1)
    d = pow(e, -1, phi)
    m = encode_msg(msg)
    if m >= n:
        print(f"{C.ERR}  [!] Message too long for this n{C.RST}")
        return
    c = encrypt(m, e, n)
    
    m_check = pow(c, d, n)
    h = hex(m_check)[2:]
    if len(h) % 2: h = '0' + h
    sanity_check = bytes.fromhex(h).decode(errors='replace')

    Win.top("GENERATED OUTPUT")
    Win.text(f"[*] q (next prime) = {q}")
    Win.text(f"[*] Difference p-q = {abs(p-q)}")
    Win.text(f"[*] Sanity decrypt = {sanity_check}")
    Win.div()
    Win.text(f"n = {n}")
    Win.text(f"e = {e}")
    Win.text(f"c = {c}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.text(" ")
    Win.text(f"{C.CYN}RsaCtfTool command:{C.RST}")
    Win.text(f"RsaCtfTool -n {n} -e {e} --decrypt {c} --attack all")
    Win.bot()

def scenario_wiener():
    Win.top("WIENER'S ATTACK")
    Win.text("d is exceptionally small, which forces e to be huge.")
    Win.text(f"{C.WRN}Provide p, q, and a small d (< (1/3) * n^0.25).{C.RST}")
    Win.bot()
    
    p = get_int("p = ")
    q = get_int("q = ")
    if not is_prime(p) or not is_prime(q):
        print(f"{C.ERR}  [!] Warning: p or q may not be prime{C.RST}")
    if p == q:
        print(f"{C.ERR}  [!] p and q must be different primes{C.RST}")
        return

    n = p * q
    phi = (p-1)*(q-1)

    d = get_int("d (small value, e.g. 3, 5, 7, 11) = ")
    if math.gcd(d, phi) != 1:
        print(f"{C.ERR}  [!] gcd(d, phi) != 1, d={d} won't work, try another{C.RST}")
        return

    e = pow(d, -1, phi)
    threshold = math.isqrt(math.isqrt(n)) // 3
    
    msg = get_msg()
    m = encode_msg(msg)
    if m >= n:
        print(f"{C.ERR}  [!] Message too long for this n{C.RST}")
        return
    c = encrypt(m, e, n)
    
    Win.top("GENERATED OUTPUT")
    Win.text(f"[*] e = {e}")
    Win.text(f"[*] Wiener threshold: d < {threshold}")
    if d < threshold:
        Win.text(f"{C.GRN}[+] d={d} is below threshold, Wiener should work{C.RST}")
    else:
        Win.text(f"{C.ERR}[!] d={d} is above threshold, Wiener may NOT work{C.RST}")
    Win.div()
    Win.text(f"n = {n}")
    Win.text(f"e = {e}")
    Win.text(f"c = {c}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.text(" ")
    Win.text(f"{C.CYN}RsaCtfTool command:{C.RST}")
    Win.text(f"RsaCtfTool -n {n} -e {e} --decrypt {c} --attack all")
    Win.bot()

def scenario_gcd_multi():
    Win.top("GCD MULTI-N")
    Win.text("Two different n values inadvertently share a common prime.")
    Win.text(f"{C.WRN}Provide a shared prime p, then unique q1 and q2.{C.RST}")
    Win.bot()
    
    p  = get_int("Shared p = ")
    q1 = get_int("q1 (unique to n1) = ")
    q2 = get_int("q2 (unique to n2) = ")

    n1 = p * q1
    n2 = p * q2
    g  = math.gcd(n1, n2)
    
    e = 65537
    msg = get_msg()
    m = encode_msg(msg)

    phi1 = (p-1)*(q1-1)
    if m >= n1:
        print(f"{C.ERR}  [!] Message too long for n1{C.RST}")
        return
    c1 = encrypt(m, e, n1)
    c2 = encrypt(m, e, n2)

    Win.top("GENERATED OUTPUT")
    Win.text(f"[*] gcd(n1, n2) = {g}")
    if g == p:
        Win.text(f"{C.GRN}[+] GCD correctly reveals shared prime p={p}{C.RST}")
    else:
        Win.text(f"{C.ERR}[!] GCD={g} doesn't match p={p}, check inputs{C.RST}")
    Win.div()
    Win.text(f"n1 = {n1}")
    Win.text(f"c1 = {c1}")
    Win.text(" ")
    Win.text(f"n2 = {n2}")
    Win.text(f"c2 = {c2}")
    Win.text(" ")
    Win.text(f"e  = {e}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.text(" ")
    Win.text(f"{C.CYN}RsaCtfTool commands:{C.RST}")
    Win.text(f"RsaCtfTool -n {n1} -e {e} --decrypt {c1} --attack comfact_cn")
    Win.text(f"RsaCtfTool -n {n2} -e {e} --decrypt {c2} --attack comfact_cn")
    Win.bot()

def scenario_hastads():
    Win.top("HASTADS BROADCAST")
    Win.text("Same message encrypted under e=3 with 3 different n values.")
    Win.text(f"{C.WRN}Provide 3 pairs of (p, q).{C.RST}")
    Win.bot()

    pairs = []
    for i in range(1, 4):
        print(f"\n  {C.CYN}Key pair {i}:{C.RST}")
        p = get_int(f"  p{i} = ")
        q = get_int(f"  q{i} = ")
        pairs.append((p, q))

    msg = get_msg()
    e = 3
    m = encode_msg(msg)

    ns, cs = [], []
    for i, (p, q) in enumerate(pairs):
        n = p * q
        phi = (p-1)*(q-1)
        if math.gcd(e, phi) != 1:
            print(f"{C.ERR}  [!] gcd(e, phi) != 1 for pair {i+1}, try again{C.RST}")
            return
        if m >= n:
            print(f"{C.ERR}  [!] Message too long for n{i+1}{C.RST}")
            return
        c = encrypt(m, e, n)
        ns.append(n)
        cs.append(c)

    Win.top("GENERATED OUTPUT")
    for i in range(3):
        Win.text(f"n{i+1} = {ns[i]}")
        Win.text(f"c{i+1} = {cs[i]}")
        Win.text(" ")
    Win.text(f"e  = {e}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.text(" ")
    Win.text(f"{C.CYN}RsaCtfTool command:{C.RST}")
    Win.text(f"RsaCtfTool -n {ns[0]},{ns[1]},{ns[2]} -e {e} --decrypt {cs[0]},{cs[1]},{cs[2]} --attack hastads")
    Win.bot()

def scenario_common_modulus():
    Win.top("COMMON MODULUS")
    Win.text("Same n and message, encrypted with two different e values.")
    Win.text(f"{C.WRN}Provide p, q, and two different e values.{C.RST}")
    Win.bot()
    
    p  = get_int("p = ")
    q  = get_int("q = ")
    e1 = get_int("e1 = ")
    e2 = get_int("e2 = ")

    if math.gcd(e1, e2) != 1:
        print(f"{C.ERR}  [!] gcd(e1, e2) must be 1 for attack to work{C.RST}")
        return

    msg = get_msg()
    n = p * q
    m = encode_msg(msg)
    if m >= n:
        print(f"{C.ERR}  [!] Message too long for this n{C.RST}")
        return

    c1 = encrypt(m, e1, n)
    c2 = encrypt(m, e2, n)

    Win.top("GENERATED OUTPUT")
    Win.text(f"n  = {n}")
    Win.text(" ")
    Win.text(f"e1 = {e1}")
    Win.text(f"c1 = {c1}")
    Win.text(" ")
    Win.text(f"e2 = {e2}")
    Win.text(f"c2 = {c2}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.text(" ")
    Win.text(f"{C.CYN}RsaCtfTool command:{C.RST}")
    Win.text(f"RsaCtfTool -n {n} -e {e1},{e2} --decrypt {c1},{c2} --attack common_modulus_related_message")
    Win.bot()

# ============================== CLASSICAL SCENARIOS ==============================

def scenario_caesar():
    Win.top("CAESAR / ROT")
    Win.text("Each letter is shifted by a fixed number of positions.")
    Win.text(f"{C.WRN}Provide a message and a shift value (1-25).{C.RST}")
    Win.bot()

    msg = get_alpha_msg()
    shift = get_int("Shift (1-25) = ") % 26

    ct = ""
    for char in msg:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            ct += chr((ord(char) - base + shift) % 26 + base)
        else:
            ct += char

    print_output(
        "Caesar",
        {"Plaintext": msg, "Shift": shift},
        ct,
        msg,
        notes=[f"Shift = {shift}  |  ROT-{shift}"]
    )

def scenario_vigenere():
    Win.top("VIGENÈRE CIPHER")
    Win.text("Each letter shifted by corresponding key letter.")
    Win.text(f"{C.WRN}Provide a message and a keyword (letters only).{C.RST}")
    Win.bot()

    msg = get_alpha_msg()
    key = input(f"{C.BLU}▶{C.RST} Key (letters only, e.g. KEY): ").strip().upper()
    key = ''.join(c for c in key if c.isalpha())
    if not key:
        print(f"{C.ERR}  [!] Key must contain letters{C.RST}")
        return

    ct, key_idx = "", 0
    for char in msg:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shift = ord(key[key_idx % len(key)]) - ord('A')
            ct += chr((ord(char) - base + shift) % 26 + base)
            key_idx += 1
        else:
            ct += char

    print_output(
        "Vigenere",
        {"Plaintext": msg, "Key": key},
        ct,
        msg,
        notes=[f"Key length = {len(key)}"]
    )

def scenario_atbash():
    Win.top("ATBASH CIPHER")
    Win.text("A=Z, B=Y, C=X ... Z=A. No key needed.")
    Win.bot()

    msg = get_alpha_msg()
    ct = "".join(
        chr(ord('A') + (25 - (ord(c.upper()) - ord('A')))) if c.isalpha() else c
        for c in msg
    )

    print_output("Atbash", {"Plaintext": msg}, ct, msg)

def scenario_affine():
    Win.top("AFFINE CIPHER")
    Win.text("C = (a*P + b) mod 26. Key is two numbers: a and b.")
    Win.text(f"{C.WRN}a must be coprime with 26. Valid values: 1,3,5,7,9,11,15,17,19,21,23,25{C.RST}")
    Win.bot()

    msg = get_alpha_msg()
    a = get_int("a (multiplicative key) = ")
    b = get_int("b (additive key) = ")

    if math.gcd(a, 26) != 1:
        print(f"{C.ERR}  [!] a={a} is not coprime with 26. Choose from: 1,3,5,7,9,11,15,17,19,21,23,25{C.RST}")
        return

    ct = ""
    for char in msg:
        if char.isalpha():
            p = ord(char.upper()) - ord('A')
            ct += chr((a * p + b) % 26 + ord('A'))
        else:
            ct += char

    print_output(
        "Affine",
        {"Plaintext": msg, "a": a, "b": b},
        ct,
        msg,
        notes=[f"Formula: C = ({a}*P + {b}) mod 26"]
    )

def scenario_playfair():
    Win.top("PLAYFAIR CIPHER")
    Win.text("Encrypts digraphs (letter pairs) using a 5x5 key matrix.")
    Win.text(f"{C.WRN}J is treated as I. Message length must be even after padding.{C.RST}")
    Win.bot()

    msg = get_alpha_msg().replace('J', 'I')
    key = input(f"{C.BLU}▶{C.RST} Key word (e.g. KEYWORD): ").strip().upper().replace('J', 'I')
    key = ''.join(c for c in key if c.isalpha())

    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    m_str = "".join(collections.OrderedDict.fromkeys(key + alphabet))
    matrix = [list(m_str[i:i+5]) for i in range(0, 25, 5)]

    def get_pos(char):
        for r in range(5):
            for c in range(5):
                if matrix[r][c] == char:
                    return r, c


    prepared = ""
    i = 0
    while i < len(msg):
        prepared += msg[i]
        if i + 1 < len(msg):
            if msg[i] == msg[i+1]:
                prepared += 'X'
            else:
                prepared += msg[i+1]
                i += 1
        i += 1
    if len(prepared) % 2 != 0:
        prepared += 'X'

    ct = ""
    for i in range(0, len(prepared), 2):
        r1, c1 = get_pos(prepared[i])
        r2, c2 = get_pos(prepared[i+1])
        if r1 == r2:
            ct += matrix[r1][(c1+1)%5] + matrix[r2][(c2+1)%5]
        elif c1 == c2:
            ct += matrix[(r1+1)%5][c1] + matrix[(r2+1)%5][c2]
        else:
            ct += matrix[r1][c2] + matrix[r2][c1]

    Win.top("GENERATED OUTPUT")
    Win.text(f"[*] Key matrix built from: {key}")
    Win.text(f"[*] Prepared plaintext:    {prepared}")
    Win.div()
    Win.text(f"Key       = {key}")
    Win.text(f"Plaintext = {prepared}")
    Win.text(f"Ciphertext = {C.GRN}{ct}{C.RST}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{prepared}{C.RST}")
    Win.bot()

def scenario_hill_2x2():
    Win.top("HILL CIPHER (2x2)")
    Win.text("Matrix multiplication mod 26. Key is a 2x2 invertible matrix.")
    Win.text(f"{C.WRN}det(key) must be coprime with 26. Message length must be even.{C.RST}")
    Win.bot()

    msg = get_alpha_msg()
    if len(msg) % 2 != 0:
        msg += 'X'
        print(f"{C.WRN}  [*] Padded with X to make even length: {msg}{C.RST}")

    print(f"\n  {C.CYN}Enter 2x2 key matrix:{C.RST}")
    a = get_int("M[0,0] = ")
    b = get_int("M[0,1] = ")
    c = get_int("M[1,0] = ")
    d = get_int("M[1,1] = ")

    det = (a * d - b * c) % 26
    if math.gcd(det, 26) != 1:
        print(f"{C.ERR}  [!] Determinant {det} is not coprime with 26. Choose different matrix.{C.RST}")
        return

    ct = ""
    for i in range(0, len(msg), 2):
        v1 = ord(msg[i]) - ord('A')
        v2 = ord(msg[i+1]) - ord('A')
        ct += chr((a * v1 + b * v2) % 26 + ord('A'))
        ct += chr((c * v1 + d * v2) % 26 + ord('A'))

    Win.top("GENERATED OUTPUT")
    Win.text(f"[*] Key matrix: [{a} {b}] [{c} {d}]")
    Win.text(f"[*] det mod 26 = {det} (coprime, valid)")
    Win.div()
    Win.text(f"Key matrix = [[{a},{b}],[{c},{d}]]")
    Win.text(f"Plaintext  = {msg}")
    Win.text(f"Ciphertext = {C.GRN}{ct}{C.RST}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.bot()

def scenario_hill_3x3():
    Win.top("HILL CIPHER (3x3)")
    Win.text("3x3 matrix multiplication mod 26. Message length must be multiple of 3.")
    Win.text(f"{C.WRN}det(key) must be coprime with 26.{C.RST}")
    Win.bot()

    msg = get_alpha_msg()
    while len(msg) % 3 != 0:
        msg += 'X'
    if msg != msg.rstrip('X'):
        print(f"{C.WRN}  [*] Padded with X: {msg}{C.RST}")

    print(f"\n  {C.CYN}Enter 3x3 key matrix row by row:{C.RST}")
    m = [[get_int(f"M[{i},{j}] = ") for j in range(3)] for i in range(3)]

    det = (
        m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) -
        m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0]) +
        m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
    ) % 26

    if math.gcd(det, 26) != 1:
        print(f"{C.ERR}  [!] Determinant {det} is not coprime with 26. Choose different matrix.{C.RST}")
        return

    ct = ""
    for i in range(0, len(msg), 3):
        v = [ord(msg[i+j]) - ord('A') for j in range(3)]
        for r in range(3):
            ct += chr(sum(m[r][k] * v[k] for k in range(3)) % 26 + ord('A'))

    Win.top("GENERATED OUTPUT")
    Win.text(f"[*] det mod 26 = {det} (coprime, valid)")
    Win.div()
    Win.text(f"Key matrix = {m}")
    Win.text(f"Plaintext  = {msg}")
    Win.text(f"Ciphertext = {C.GRN}{ct}{C.RST}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.bot()

def scenario_railfence():
    Win.top("RAIL FENCE CIPHER")
    Win.text("Message is written in zigzag across N rails, then read row by row.")
    Win.text(f"{C.WRN}Provide a message and number of rails.{C.RST}")
    Win.bot()

    msg = input(f"{C.BLU}▶{C.RST} Message (default: FLAGTEST): ").strip() or "FLAGTEST"
    rails = get_int("Number of rails = ")
    if rails < 2:
        print(f"{C.ERR}  [!] Need at least 2 rails{C.RST}")
        return

    fence = [[] for _ in range(rails)]
    rail, direction = 0, 1
    for char in msg:
        fence[rail].append(char)
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1

    ct = "".join("".join(row) for row in fence)

    Win.top("GENERATED OUTPUT")
    Win.text(f"[*] Rail pattern:")
    rail, direction = 0, 1
    pattern = [[] for _ in range(rails)]
    for i, char in enumerate(msg):
        pattern[rail].append(char)
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1
    for i, row in enumerate(pattern):
        Win.text(f"  Rail {i+1}: {''.join(row)}")
    Win.div()
    Win.text(f"Rails      = {rails}")
    Win.text(f"Plaintext  = {msg}")
    Win.text(f"Ciphertext = {C.GRN}{ct}{C.RST}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.bot()

def scenario_columnar():
    Win.top("COLUMNAR TRANSPOSITION")
    Win.text("Columns are rearranged based on alphabetical order of key letters.")
    Win.text(f"{C.WRN}Provide a message and a keyword.{C.RST}")
    Win.bot()

    msg = input(f"{C.BLU}▶{C.RST} Message (default: ATTACKATDAWN): ").strip() or "ATTACKATDAWN"
    key = input(f"{C.BLU}▶{C.RST} Key (e.g. ZEBRA): ").strip().upper()
    if not key:
        print(f"{C.ERR}  [!] Key required{C.RST}")
        return

    col_len = len(key)
    row_len = math.ceil(len(msg) / col_len)
    padded = msg.ljust(row_len * col_len, 'X')

    matrix = [list(padded[i:i+col_len]) for i in range(0, len(padded), col_len)]

    key_order = sorted(range(col_len), key=lambda k: key[k])
    ct = ""
    for col in key_order:
        for row in matrix:
            ct += row[col]

    Win.top("GENERATED OUTPUT")
    Win.text(f"[*] Key order: {' '.join(str(k+1) for k in key_order)}")
    Win.text(f"[*] Grid:")
    Win.text(f"  Key: {' '.join(key)}")
    for row in matrix:
        Win.text(f"       {'  '.join(row)}")
    Win.div()
    Win.text(f"Key        = {key}")
    Win.text(f"Plaintext  = {msg}")
    Win.text(f"Ciphertext = {C.GRN}{ct}{C.RST}")
    Win.div("VERIFICATION")
    Win.text(f"Answer should decrypt to: {C.GRN}{msg}{C.RST}")
    Win.bot()

# ============================== MAIN MENU ==============================

RSA_MENU = {
    "1": ("Even prime (p=2)",                scenario_even_prime),
    "2": ("Small e (e=3, cube root)",        scenario_small_e),
    "3": ("Fermat (p and q close)",          scenario_fermat),
    "4": ("Wiener (small d, huge e)",        scenario_wiener),
    "5": ("GCD multi-N (shared prime)",      scenario_gcd_multi),
    "6": ("Hastads broadcast (e=3, 3 keys)", scenario_hastads),
    "7": ("Common modulus (same n, diff e)", scenario_common_modulus),
}

CLASSICAL_MENU = {
    "1": ("Caesar / ROT",                   scenario_caesar),
    "2": ("Vigenère (known key)",           scenario_vigenere),
    "3": ("Atbash",                         scenario_atbash),
    "4": ("Affine",                         scenario_affine),
    "5": ("Playfair",                       scenario_playfair),
    "6": ("Hill 2x2",                       scenario_hill_2x2),
    "7": ("Hill 3x3",                       scenario_hill_3x3),
    "8": ("Rail Fence",                     scenario_railfence),
    "9": ("Columnar Transposition",         scenario_columnar),
}

def show_submenu(title, menu):
    while True:
        clear_screen()
        Win.top("")
        print_rainbow_banner(FORGE_BANNER)
        Win.div(title)
        for k, (label, _) in menu.items():
            Win.text(f"  {C.CYN}{k}.{C.RST} {label}")
        Win.text(f"  {C.CYN}q.{C.RST} Back")
        Win.bot()

        choice = input(f"\n{C.BLD}Choice:{C.RST} ").strip().lower()
        if choice == "q":
            break
        elif choice in menu:
            clear_screen()
            menu[choice][1]()
        else:
            print(f"{C.ERR}  [!] Invalid choice{C.RST}")

        input(f"\n{C.CYN}Press Enter to return to menu...{C.RST}")

def main():
    while True:
        clear_screen()
        Win.top("")
        print_rainbow_banner(FORGE_BANNER)
        Win.div("DOMAINS")
        Win.text(f"  {C.CYN}1.{C.RST} RSA / Asymmetric")
        Win.text(f"  {C.CYN}2.{C.RST} Classical Ciphers")
        Win.text(f"  {C.CYN}q.{C.RST} Quit")
        Win.bot()

        choice = input(f"\n{C.BLD}Choice:{C.RST} ").strip().lower()
        if choice == "q":
            break
        elif choice == "1":
            show_submenu("RSA TEST CASE GENERATOR", RSA_MENU)
        elif choice == "2":
            show_submenu("CLASSICAL CIPHER GENERATOR", CLASSICAL_MENU)
        else:
            print(f"{C.ERR}  [!] Invalid choice{C.RST}")

if __name__ == "__main__":
    main()