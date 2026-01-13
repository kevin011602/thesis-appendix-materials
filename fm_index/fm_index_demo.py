#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Counter
from typing import Dict, List, Tuple, Optional


def banner(title: str) -> None:
    line = "─" * 78
    print("\n" + line)
    print(title)
    print(line)


def wait_enter(prompt: str = "Premi INVIO per continuare ") -> None:
    input(prompt)


def suffix_array(text: str) -> List[int]:
    return sorted(range(len(text)), key=lambda i: text[i:])


def bwt_from_sa(text: str, sa: List[int]) -> str:
    return "".join(text[i - 1] if i > 0 else "$" for i in sa)


def rotations_sorted(text: str) -> List[str]:
    return sorted(text[i:] + text[:i] for i in range(len(text)))


def build_C(L: str) -> Dict[str, int]:
    counts = Counter(L)
    alphabet = sorted(counts.keys())
    C: Dict[str, int] = {}
    total = 0
    for c in alphabet:
        C[c] = total
        total += counts[c]
    return C


def build_Occ(L: str) -> Dict[str, List[int]]:
    n = len(L)
    alphabet = sorted(set(L))
    occ = {c: [0] * (n + 1) for c in alphabet}
    running = {c: 0 for c in alphabet}

    for i, ch in enumerate(L, start=1):
        running[ch] += 1
        for c in alphabet:
            occ[c][i] = running[c]
    return occ


def Occ(occ: Dict[str, List[int]], c: str, i: int) -> int:
    return occ[c][i]


def build_LF(L: str, C: Dict[str, int], occ: Dict[str, List[int]]) -> List[int]:
    return [C[ch] + Occ(occ, ch, i) for i, ch in enumerate(L)]


def invert_bwt(L: str, lf: List[int]) -> Tuple[str, List[Tuple[int, str, int]]]:
    n = len(L)
    row = L.index("$")
    out_rev: List[str] = []
    trace: List[Tuple[int, str, int]] = []

    for _ in range(n):
        ch = L[row]
        out_rev.append(ch)
        nxt = lf[row]
        trace.append((row, ch, nxt))
        row = nxt

    return "".join(reversed(out_rev)), trace


def backward_search_steps(
    pattern: str, L: str, C: Dict[str, int], occ: Dict[str, List[int]]
) -> Tuple[Optional[Tuple[int, int]], List[Tuple[str, int, int, int, int]]]:
    n = len(L)
    sp, ep = 0, n
    steps: List[Tuple[str, int, int, int, int]] = []

    for c in reversed(pattern):
        if c not in C:
            steps.append((c, sp, ep, -1, -1))
            return None, steps
        sp_new = C[c] + Occ(occ, c, sp)
        ep_new = C[c] + Occ(occ, c, ep)
        steps.append((c, sp, ep, sp_new, ep_new))
        sp, ep = sp_new, ep_new
        if sp >= ep:
            return None, steps

    return (sp, ep), steps


def print_sa_table(text: str, sa: List[int]) -> None:
    print("SA =", sa)
    print("\nIndice  SA[i]   suffisso")
    print("-----  -----   ----------------")
    for i, pos in enumerate(sa):
        print(f"{i:>5}  {pos:>5}   {text[pos:]}")


def print_C(C: Dict[str, int]) -> None:
    print("C[c] = # simboli in L strettamente minori di c (alfabeto ordinato)")
    for c in sorted(C.keys()):
        print(f"  C[{c!r}] = {C[c]}")


def print_Occ_compact(L: str, occ: Dict[str, List[int]]) -> None:
    n = len(L)
    alphabet = sorted(occ.keys())
    print("Occ(c,i) = # occorrenze di c nel prefisso L[0..i)")
    print("Indice i:     " + " ".join(f"{i:>2}" for i in range(n + 1)))
    print("L (BWT):      " + " ".join(["  "] + [f"{ch:>2}" for ch in L]))
    for c in alphabet:
        row = " ".join(f"{occ[c][i]:>2}" for i in range(n + 1))
        print(f"Occ({c!r},i): " + row)


def print_LF_table(text: str, sa: List[int], L: str, lf: List[int]) -> None:
    print("i   SA[i]   L[i]   LF(i)   suffisso")
    print("--  -----  -----  -----   ----------------")
    for i in range(len(L)):
        print(f"{i:>2}  {sa[i]:>5}  {L[i]:>5}  {lf[i]:>5}   {text[sa[i]:]}")


def print_backward_search(
    pattern: str, text: str, sa: List[int], L: str, C: Dict[str, int], occ: Dict[str, List[int]]
) -> None:
    interval, steps = backward_search_steps(pattern, L, C, occ)

    print(f"Pattern P = {pattern!r} (ricerca da destra verso sinistra)")
    print("Update: sp' = C[c] + Occ(c, sp)   |   ep' = C[c] + Occ(c, ep)\n")
    print("passo  c   [sp,ep) -> [sp',ep')        calcoli")
    print("-----  -   ---------------------       ------------------------------")

    for t, (c, sp, ep, spn, epn) in enumerate(steps, start=1):
        if spn == -1:
            print(f"{t:>5}  {c!r}   [{sp},{ep}) -> (simbolo assente dall'alfabeto)")
            break
        calc = (
            f"sp'={C[c]}+Occ({c!r},{sp})={C[c]}+{Occ(occ,c,sp)}={spn};  "
            f"ep'={C[c]}+Occ({c!r},{ep})={C[c]}+{Occ(occ,c,ep)}={epn}"
        )
        print(f"{t:>5}  {c!r}   [{sp:>2},{ep:>2}) -> [{spn:>2},{epn:>2})       {calc}")

    if interval is None:
        print("\nRisultato: intervallo vuoto ⇒ P NON compare in T.")
        return

    sp, ep = interval
    positions = [sa[i] for i in range(sp, ep)]
    print(f"\nRisultato: intervallo finale [{sp},{ep}) ⇒ occorrenze = {ep - sp}")
    print("Posizioni nel testo (via SA[sp..ep-1]):", positions)
    print("Verifica in T:")
    for pos in positions:
        print(f"  T[{pos}:{pos+len(pattern)}] = {text[pos:pos+len(pattern)]!r}")


def main() -> None:
    banner("FM-index didattico (BWT / C / Occ / LF / Backward Search)")

    raw = input("Inserisci il testo T (NON inserire '$'): ").strip()
    while raw == "" or "$" in raw:
        raw = input("Testo non valido. Inserisci T senza '$': ").strip()

    text = raw + "$"

    banner("Input")
    print("T  =", repr(raw))
    print("T$ =", repr(text))
    print("n  =", len(text))
    wait_enter()

    banner("Matrice delle rotazioni (concettuale)")
    for i, r in enumerate(rotations_sorted(text)):
        print(f"{i:>2}: {r}")
    wait_enter()

    sa = suffix_array(text)
    banner("1) Suffix Array (SA)")
    print_sa_table(text, sa)
    wait_enter()

    L = bwt_from_sa(text, sa)
    F = "".join(sorted(L))
    banner("2) Burrows–Wheeler Transform")
    print("L (BWT) =", L)
    print("F       =", F)
    print("\nInterpretazione: L[i] è il carattere che precede il suffisso che inizia in SA[i].")
    wait_enter()

    C = build_C(L)
    banner("3) Array C")
    print_C(C)
    wait_enter()

    occ = build_Occ(L)
    banner("4) Operazione Occ (rank su prefissi semiaperti)")
    print_Occ_compact(L, occ)
    wait_enter()

    lf = build_LF(L, C, occ)
    banner("5) LF-mapping")
    print("Definizione: LF(i) = C[L[i]] + Occ(L[i], i)\n")
    print_LF_table(text, sa, L, lf)
    wait_enter()

    decoded, trace = invert_bwt(L, lf)
    banner("6) Invertibilità (ricostruzione da L via LF)")
    print("Testo ricostruito =", repr(decoded))
    print("\nTrace (row, L[row], LF(row)) a partire dalla riga con '$':")
    for step, (row, ch, nxt) in enumerate(trace):
        print(f"  step {step:>2}: row={row:>2}  L[row]={ch!r}  -> LF(row)={nxt:>2}")
    wait_enter()

    while True:
        banner("7) Backward Search (FM-index)")
        pat = input("Inserisci un pattern P (invio per terminare): ").strip()
        if pat == "":
            break
        if "$" in pat:
            print("Non inserire '$' nel pattern.")
            wait_enter()
            continue

        print_backward_search(pat, text, sa, L, C, occ)
        wait_enter()


if __name__ == "__main__":
    main()