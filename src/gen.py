import math
import random
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

# ============================== EVEN PRIME ==============================

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

# ============================== SMALL E ==============================

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

# ============================== FERMAT ==============================

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

# ============================== WIENER ==============================

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

# ============================== GCD MULTI-N ==============================

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

# ============================== HASTADS ==============================

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

# ============================== COMMON MODULUS ==============================

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

# ============================== MAIN MENU ==============================

MENU = {
    "1": ("Even prime (p=2)",               scenario_even_prime),
    "2": ("Small e (e=3, cube root)",       scenario_small_e),
    "3": ("Fermat (p and q close)",         scenario_fermat),
    "4": ("Wiener (small d, huge e)",       scenario_wiener),
    "5": ("GCD multi-N (shared prime)",     scenario_gcd_multi),
    "6": ("Hastads broadcast (e=3, 3 keys)",scenario_hastads),
    "7": ("Common modulus (same n, diff e)",scenario_common_modulus),
}

def main():
    while True:
        clear_screen()
        Win.top("")
        print_rainbow_banner(FORGE_BANNER)
        Win.div("TEST CASE GENERATOR")
        for k, (label, _) in MENU.items():
            Win.text(f"  {C.CYN}{k}.{C.RST} {label}")
        Win.text(f"  {C.CYN}q.{C.RST} Quit")
        Win.bot()

        choice = input(f"\n{C.BLD}Choice:{C.RST} ").strip().lower()
        if choice == "q":
            break
        elif choice in MENU:
            clear_screen()
            MENU[choice][1]()
        else:
            print(f"{C.ERR}  [!] Invalid choice{C.RST}")

        input(f"\n{C.CYN}Press Enter to return to menu...{C.RST}")

if __name__ == "__main__":
    main()