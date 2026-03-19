import math
import random

def get_int(prompt):
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("  [!] Enter a valid integer")

def get_msg():
    return input("Enter message to encrypt (default: flag{test}): ").strip() or "flag{test}"

def encode_msg(msg):
    return int.from_bytes(msg.encode(), "big")

def encrypt(m, e, n):
    return pow(m, e, n)

def print_output(n, e, c, msg, extra=None):
    print(f"\n=== OUTPUT ===")
    print(f"n = {n}")
    print(f"e = {e}")
    print(f"c = {c}")
    if extra:
        for k, v in extra.items():
            print(f"{k} = {v}")
    print(f"\n(answer should decrypt to: {msg})")
    print(f"\nRsaCtfTool command:")
    print(f"RsaCtfTool -n {n} -e {e} --decrypt {c} --attack all")

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
    print("\n[Even Prime] — p=2, n is even")
    print("  You provide q (any prime number, try something like 104723)")
    q = get_int("  q = ")
    if not is_prime(q):
        print(f"  [!] Warning: {q} is not prime, results may be wrong")
    msg = get_msg()

    p = 2
    n = p * q
    e = 65537
    phi = (p-1)*(q-1)
    d = pow(e, -1, phi)
    m = encode_msg(msg)
    if m >= n:
        print("  [!] Message too long for this n, use shorter message")
        return
    c = encrypt(m, e, n)
    print_output(n, e, c, msg)

# ============================== SMALL E ==============================

def scenario_small_e():
    print("\n[Small e] — e=3, message is tiny so c = m^3 < n")
    print("  You provide p and q (large primes)")
    print("  Note: message must be small enough that m^3 < n, otherwise this attack fails")
    p = get_int("  p = ")
    q = get_int("  q = ")
    if not is_prime(p) or not is_prime(q):
        print("  [!] Warning: p or q may not be prime")
    msg = get_msg()

    n = p * q
    e = 3
    phi = (p-1)*(q-1)
    try:
        d = pow(e, -1, phi)
    except Exception:
        print("  [!] gcd(e, phi) != 1, choose different p/q")
        return
    m = encode_msg(msg)
    if m >= n:
        print("  [!] Message too long for this n")
        return
    c = encrypt(m, e, n)

    if c == pow(m, 3):
        print("  [+] m^3 < n, cube root attack will work directly")
    else:
        print("  [!] m^3 >= n (wraps around modulus), cube root attack may not work — message too long")

    print_output(n, e, c, msg)

# ============================== FERMAT ==============================

def scenario_fermat():
    print("\n[Fermat] — p and q are very close together")
    print("  You provide a starting prime p, q will be the next prime after p")
    p = get_int("  p = ")
    if not is_prime(p):
        p = next_prime(p)
        print(f"  [*] Adjusted to nearest prime: p = {p}")
    msg = get_msg()

    q = next_prime(p)
    print(f"  [*] q = next prime after p = {q}")
    print(f"  [*] difference p-q = {abs(p-q)}")

    n = p * q
    e = 65537
    phi = (p-1)*(q-1)
    d = pow(e, -1, phi)
    m = encode_msg(msg)
    if m >= n:
        print("  [!] Message too long for this n")
        return
    c = encrypt(m, e, n)
    print_output(n, e, c, msg)

    m_check = pow(c, d, n)
    h = hex(m_check)[2:]
    if len(h) % 2: h = '0' + h
    print(f"  [*] Sanity check decrypt: {bytes.fromhex(h).decode(errors='replace')}")

# ============================== WIENER ==============================

def scenario_wiener():
    print("\n[Wiener] — d is small, which forces e to be huge")
    print("  You provide p and q and a small d")
    print("  Rule: d must be < (1/3) * n^0.25 for Wiener to work")
    p = get_int("  p = ")
    q = get_int("  q = ")
    if not is_prime(p) or not is_prime(q):
        print("  [!] Warning: p or q may not be prime")
    if p == q:
        print("  [!] p and q must be different primes")
        return

    n = p * q
    phi = (p-1)*(q-1)

    d = get_int("  d (small value, e.g. 3, 5, 7, 11): ")
    if math.gcd(d, phi) != 1:
        print(f"  [!] gcd(d, phi) != 1, d={d} won't work, try another")
        return

    e = pow(d, -1, phi)
    threshold = math.isqrt(math.isqrt(n)) // 3
    print(f"  [*] e = {e}")
    print(f"  [*] Wiener threshold: d < {threshold}")
    if d < threshold:
        print(f"  [+] d={d} is below threshold, Wiener should work")
    else:
        print(f"  [!] d={d} is above threshold, Wiener may NOT work — use smaller d or larger n")

    msg = get_msg()
    m = encode_msg(msg)
    if m >= n:
        print("  [!] Message too long for this n")
        return
    c = encrypt(m, e, n)
    print_output(n, e, c, msg)

# ============================== GCD MULTI-N ==============================

def scenario_gcd_multi():
    print("\n[GCD Multi-N] — two different n values share a common prime")
    print("  You provide a shared prime p, then q1 and q2 (different)")
    p  = get_int("  shared p = ")
    q1 = get_int("  q1 (unique to n1) = ")
    q2 = get_int("  q2 (unique to n2) = ")

    n1 = p * q1
    n2 = p * q2
    g  = math.gcd(n1, n2)
    print(f"  [*] n1 = {n1}")
    print(f"  [*] n2 = {n2}")
    print(f"  [*] gcd(n1, n2) = {g}")
    if g == p:
        print(f"  [+] GCD correctly reveals shared prime p={p}")
    else:
        print(f"  [!] GCD={g} doesn't match p={p}, check your inputs")

    e = 65537
    msg = get_msg()
    m = encode_msg(msg)

    phi1 = (p-1)*(q1-1)
    d1 = pow(e, -1, phi1)
    if m >= n1:
        print("  [!] Message too long for n1")
        return
    c1 = encrypt(m, e, n1)

    phi2 = (p-1)*(q2-1)
    d2 = pow(e, -1, phi2)
    c2 = encrypt(m, e, n2)

    print(f"\n=== OUTPUT ===")
    print(f"n1 = {n1}")
    print(f"n2 = {n2}")
    print(f"e  = {e}")
    print(f"c1 = {c1}  (ciphertext for n1)")
    print(f"c2 = {c2}  (ciphertext for n2)")
    print(f"\n(answer should decrypt to: {msg})")
    print(f"\nRsaCtfTool commands:")
    print(f"RsaCtfTool -n {n1} -e {e} --decrypt {c1} --attack comfact_cn --attack all")
    print(f"RsaCtfTool -n {n2} -e {e} --decrypt {c2} --attack comfact_cn --attack all")

# ============================== HASTADS ==============================

def scenario_hastads():
    print("\n[Hastads Broadcast] — same message encrypted under e=3 with 3 different n values")
    print("  You provide 3 pairs of (p, q)")

    pairs = []
    for i in range(1, 4):
        print(f"\n  Key pair {i}:")
        p = get_int(f"    p{i} = ")
        q = get_int(f"    q{i} = ")
        pairs.append((p, q))

    msg = get_msg()
    e = 3
    m = encode_msg(msg)

    ns, cs = [], []
    for i, (p, q) in enumerate(pairs):
        n = p * q
        phi = (p-1)*(q-1)
        if math.gcd(e, phi) != 1:
            print(f"  [!] gcd(e, phi) != 1 for pair {i+1}, choose different primes")
            return
        if m >= n:
            print(f"  [!] Message too long for n{i+1}")
            return
        c = encrypt(m, e, n)
        ns.append(n)
        cs.append(c)

    print(f"\n=== OUTPUT ===")
    for i in range(3):
        print(f"n{i+1} = {ns[i]}")
        print(f"c{i+1} = {cs[i]}")
    print(f"e  = {e}")
    print(f"\n(answer should decrypt to: {msg})")
    print(f"\nRsaCtfTool command:")
    print(f"RsaCtfTool -n {ns[0]},{ns[1]},{ns[2]} -e {e} --decrypt {cs[0]},{cs[1]},{cs[2]} --attack hastads")

# ============================== COMMON MODULUS ==============================

def scenario_common_modulus():
    print("\n[Common Modulus] — same n and message, encrypted with two different e values")
    print("  You provide p, q, and two different e values")
    p  = get_int("  p = ")
    q  = get_int("  q = ")
    e1 = get_int("  e1 = ")
    e2 = get_int("  e2 = ")

    if math.gcd(e1, e2) != 1:
        print("  [!] gcd(e1, e2) must be 1 for common modulus attack to work")
        return

    msg = get_msg()
    n = p * q
    m = encode_msg(msg)
    if m >= n:
        print("  [!] Message too long for this n")
        return

    c1 = encrypt(m, e1, n)
    c2 = encrypt(m, e2, n)

    print(f"\n=== OUTPUT ===")
    print(f"n  = {n}")
    print(f"e1 = {e1}")
    print(f"e2 = {e2}")
    print(f"c1 = {c1}")
    print(f"c2 = {c2}")
    print(f"\n(answer should decrypt to: {msg})")
    print(f"\nRsaCtfTool command:")
    print(f"RsaCtfTool -n {n} -e {e1},{e2} --decrypt {c1},{c2} --attack common_modulus_related_message")

# ============================== MAIN MENU ==============================

MENU = {
    "1": ("Even prime (p=2)",              scenario_even_prime),
    "2": ("Small e (e=3, cube root)",       scenario_small_e),
    "3": ("Fermat (p and q close)",         scenario_fermat),
    "4": ("Wiener (small d, huge e)",       scenario_wiener),
    "5": ("GCD multi-N (shared prime)",     scenario_gcd_multi),
    "6": ("Hastads broadcast (e=3, 3 keys)",scenario_hastads),
    "7": ("Common modulus (same n, diff e)",scenario_common_modulus),
}

def main():
    while True:
        print("\n=== RSA CTF TEST CASE GENERATOR ===")
        for k, (label, _) in MENU.items():
            print(f"  {k}. {label}")
        print("  q. Quit")

        choice = input("\nChoice: ").strip().lower()
        if choice == "q":
            break
        elif choice in MENU:
            MENU[choice][1]()
        else:
            print("  [!] Invalid choice")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()