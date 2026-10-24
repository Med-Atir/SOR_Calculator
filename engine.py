from fractions import Fraction
import numpy as np


TOL_ZERO = 1e-12


def decomposer(A):
    D = np.diag(np.diag(A))
    L = -np.tril(A, -1)
    U = -np.triu(A, 1)
    return D, L, U


def verifier_convergence_sor(D, L, U, omega):
    M_sor = D - omega * L
    N_sor = (1 - omega) * D + omega * U
    B_sor = np.linalg.solve(M_sor, N_sor)
    rho_B = float(np.max(np.abs(np.linalg.eigvals(B_sor))))
    return B_sor, M_sor, rho_B


def calculer_iteration_sor(A, b, B_sor, C_sor, X0, epsilon, Nmax):
    X = X0.copy()
    historique = [(0, X0.copy(), None, float(np.linalg.norm(A @ X0 - b)))]
    erreur = np.inf
    residu = historique[0][3]

    for k in range(1, Nmax + 1):
        X_nouveau = B_sor @ X + C_sor
        erreur = float(np.linalg.norm(X_nouveau - X))
        residu = float(np.linalg.norm(A @ X_nouveau - b))
        historique.append((k, X_nouveau.copy(), erreur, residu))
        X = X_nouveau

        if not np.isfinite(erreur) or erreur > 1e100:
            return X, k, erreur, residu, "diverge", historique
        if erreur < epsilon:
            return X, k, erreur, residu, "converge", historique

    return X, Nmax, erreur, residu, "nmax", historique


def analyser_systeme(A, b):
    n = len(b)
    rang = np.linalg.matrix_rank(A)
    if rang < n:
        rang_aug = np.linalg.matrix_rank(np.column_stack((A, b)))
        if rang_aug > rang:
            return (
                "No solution: the system is inconsistent.",
                f"rank(A) = {rang} but rank([A | b]) = {rang_aug}.\n"
                "At least two equations contradict each other.",
            )
        return (
            "No unique solution: A is singular (det(A) = 0).",
            f"rank(A) = {rang} < {n}. The system has infinitely many solutions,\n"
            "so SOR cannot converge to a single answer.",
        )

    zeros = np.where(np.abs(np.diag(A)) < TOL_ZERO)[0]
    if zeros.size:
        i = int(zeros[0]) + 1
        return (
            f"Zero on the diagonal at A[{i}][{i}]: SOR cannot be applied.",
            "SOR divides by every diagonal entry. Since A is invertible, reorder\n"
            "the equations (swap rows) so that no diagonal entry is zero.",
        )
    return None


def diagnostics(A):
    sym = bool(np.allclose(A, A.T))
    spd = False
    if sym:
        try:
            np.linalg.cholesky(A)
            spd = True
        except np.linalg.LinAlgError:
            spd = False
    diag = np.abs(np.diag(A))
    hors_diag = np.sum(np.abs(A), axis=1) - diag
    dominante = bool(np.all(diag > hors_diag))
    cond = float(np.linalg.cond(A))
    return sym, spd, dominante, cond


def meilleur_omega(A):
    D, L, U = decomposer(A)
    meilleur = (None, np.inf)
    for w in np.arange(0.05, 2.0, 0.01):
        w = float(np.round(w, 2))
        try:
            _, _, rho = verifier_convergence_sor(D, L, U, w)
        except np.linalg.LinAlgError:
            continue
        if rho < meilleur[1]:
            meilleur = (w, rho)
    return meilleur


def valeur_cellule(item):
    if item is None:
        raise ValueError
    texte = item.text().strip().replace(",", ".")
    if not texte:
        raise ValueError
    try:
        v = float(texte)
    except ValueError:
        v = float(Fraction(texte))
    if not np.isfinite(v):
        raise ValueError
    return v


def lire_table(table, lignes, colonnes, mauvaises):
    M = np.zeros((lignes, colonnes), dtype=float)
    for i in range(lignes):
        for j in range(colonnes):
            try:
                M[i, j] = valeur_cellule(table.item(i, j))
            except (ValueError, ZeroDivisionError, OverflowError):
                mauvaises.append((table, i, j))
    return M


def fmt(v):
    return f"{v:.10g}"