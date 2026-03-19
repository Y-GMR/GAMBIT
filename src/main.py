import math

def get_int(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            return int(val)
        except ValueError:
            print("  [!] Enter a valid integer")

def decrypt(p, q, e, c, N, label=""):
    try:
        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        m = pow(c, d, N)
        h = hex(m)[2:]
        if len(h) % 2: h = '0' + h
        print(f"[*] Raw hex: {h}")
        result = bytes.fromhex(h).decode(errors='replace')
        print(f"[+] DECRYPTED ({label}): {result}")
        return result
    except Exception as ex:
        print(f"[-] Decrypt failed ({label}): {ex}")
        return None

def int_cbrt(n):
    if n < 0:
        return -int_cbrt(-n)
    if n == 0:
        return 0
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
        if x1 >= x:
            break
        x = x1
    for i in [x-1, x, x+1]:
        if i > 0 and i**3 == n:
            return i
    return None

def isqrt_check(n):
    s = math.isqrt(n)
    return s if s*s == n else None

# ============================== ATTACKS ==============================

def attack_even_prime(N, e, c):
    print("\n[*] Trying: Even prime (p=2)")
    if N % 2 == 0:
        print("[!] N is even! p=2")
        p, q = 2, N // 2
        return decrypt(p, q, e, c, N, "even prime")
    else:
        print("[-] N is odd, skip")
    return None

def attack_gcd_multi(Ns, e, c, target_N):
    print("\n[*] Trying: GCD between multiple N values")
    if len(Ns) < 2:
        print("[-] Need at least 2 N values, skip")
        return None
    for i in range(len(Ns)):
        for j in range(i+1, len(Ns)):
            g = math.gcd(Ns[i], Ns[j])
            if g > 2:
                print(f"[!] GCD(N{i+1}, N{j+1}) = {g}")
                for k, Nk in enumerate(Ns):
                    if Nk % g == 0:
                        p = g
                        q = Nk // g
                        print(f"    Factored N{k+1}: p={p}, q={q}")
                        if Nk == target_N:
                            return decrypt(p, q, e, c, target_N, "GCD multi-N")
            elif g == 2:
                print(f"[!] GCD(N{i+1}, N{j+1}) = 2 — all N values are even (p=2 attack applies)")
    return None

def attack_fermat(N, e, c, max_iter=1_000_000):
    print(f"\n[*] Trying: Fermat factorization (max {max_iter} iterations)")
    a = math.isqrt(N) + 1
    b2 = a*a - N
    for i in range(max_iter):
        b = isqrt_check(b2)
        if b is not None:
            p, q = a - b, a + b
            if p * q == N and p > 1 and q > 1:
                print(f"[!] Fermat worked after {i} iterations")
                return decrypt(p, q, e, c, N, "Fermat")
        a += 1
        b2 = a*a - N
    print("[-] Fermat did not find factors within iteration limit, skip")
    return None

def attack_small_e(N, e, c):
    print("\n[*] Trying: Small e cube root (e=3)")
    if e != 3:
        print(f"[-] e={e}, not 3, skip")
        return None
    root = int_cbrt(c)
    if root is not None and pow(root, 3) == c:
        try:
            h = hex(root)[2:]
            if len(h) % 2: h = '0' + h
            result = bytes.fromhex(h).decode(errors='replace')
            print(f"[!] Cube root worked (message was tiny)")
            print(f"[+] DECRYPTED (small e): {result}")
            return result
        except:
            pass
    print("[-] Cube root didn't yield plaintext, skip")
    return None

def hint_factordb(N):
    print(f"\n[*] Manual step: paste this N into https://factordb.com")
    print(f"    N = {N}")
    print(f"    If it returns p and q, use option 2 (known p and q)")

def attack_wiener(N, e, c):
    print("\n[*] Trying: Wiener's attack (large e)")
    if e < math.isqrt(math.isqrt(N)):
        print("[-] e is not large enough for Wiener, skip")
        return None
    try:
        from gmpy2 import isqrt as gmpy_isqrt, mpz
    except ImportError:
        print("[-] gmpy2 not installed, skipping Wiener (pip install gmpy2)")
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
            if i == 0:
                convs.append((cf[0], 1))
            elif i == 1:
                convs.append((cf[1]*cf[0]+1, cf[1]))
            else:
                h_prev, k_prev = convs[-1]
                h_pprev, k_pprev = convs[-2]
                convs.append((cf[i]*h_prev + h_pprev, cf[i]*k_prev + k_pprev))
        return convs

    cf = continued_fraction(e, N)
    for k, d in convergents(cf):
        if k == 0:
            continue
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        b = N - phi + 1
        disc = b*b - 4*N
        if disc < 0:
            continue
        sq = isqrt_check(disc)
        if sq is None:
            continue
        p = (b + sq) // 2
        q = (b - sq) // 2
        if p * q == N:
            print(f"[!] Wiener worked: d={d}")
            m = pow(c, d, N)
            h = hex(m)[2:]
            if len(h) % 2: h = '0' + h
            try:
                result = bytes.fromhex(h).decode(errors='replace')
                print(f"[+] DECRYPTED (Wiener): {result}")
                return result
            except Exception as ex:
                print(f"[-] Decrypt failed (Wiener): {ex}")
                return None
    print("[-] Wiener failed, skip")
    return None

def decrypt_known(e, c, N):
    print("\n[*] Decrypt with known p and q")
    p = get_int("  p = ")
    q = get_int("  q = ")
    return decrypt(p, q, e, c, N, "known factors")

# ============================== INPUT MENU ==============================

def get_inputs():
    print("\n=== INPUT ===")
    N = get_int("N = ")
    e = get_int("e (default 65537) = ", default=65537)
    c = get_int("c = ")

    MULTI_N = [N]
    print("\nDo you have multiple N values for GCD attack? (y/n)")
    if input("  > ").strip().lower() == "y":
        print("  Enter additional N values one per line, blank line when done:")
        while True:
            line = input("  N = ").strip()
            if line == "":
                break
            try:
                MULTI_N.append(int(line))
            except ValueError:
                print("  [!] Invalid, skipping")

    return N, e, c, MULTI_N

# ============================== MAIN MENU ==============================

def main():
    while True:
        print("\n" + "=" * 50)
        print("GAMBIT")
        print("=" * 50)
        print("1. Run all attacks")
        print("2. Decrypt with known p and q")
        print("3. Hint: look up N on factordb")
        print("q. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "q":
            break

        elif choice in ("1", "2", "3"):
            N, e, c, MULTI_N = get_inputs()

            print("\n" + "=" * 50)
            print("RESULTS")
            print("=" * 50)

            if choice == "1":
                result = (
                    attack_even_prime(N, e, c) or
                    attack_small_e(N, e, c) or
                    attack_gcd_multi(MULTI_N, e, c, N) or
                    attack_fermat(N, e, c) or
                    attack_wiener(N, e, c)
                )
                if not result:
                    print("\n[-] No automatic attack worked.")
                    hint_factordb(N)

            elif choice == "2":
                decrypt_known(e, c, N)

            elif choice == "3":
                hint_factordb(N)

        else:
            print("  [!] Invalid choice")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()