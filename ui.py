import time
import os
import engine
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_FILE = os.path.join(BASE_DIR, "interface.ui")
MAX_DIM = 10
MAX_STEPS_SHOWN = 1000

class SorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.n = 0
        self.configurer_widgets()
        self.connecter()
        self.appliquer_dimension()
        self.afficher("Ready. Fill A and b, choose ω, then press Calculate.", "info")

    def configurer_widgets(self):
        self.dim.setRange(1, MAX_DIM)
        self.dim.setValue(3)
        self.dim.setToolTip(f"Matrix dimension (1 to {MAX_DIM})")

        self.omega.setRange(0.01, 1.99)
        self.omega.setDecimals(2)
        self.omega.setSingleStep(0.05)
        self.omega.setValue(1.25)
        self.omega.setToolTip("Relaxation factor, strictly between 0 and 2")

        if not self.epsilon.text().strip():
            self.epsilon.setText("1e-6")
        self.epsilon.setToolTip("Stopping tolerance on ||X_k - X_(k-1)||, e.g. 1e-6")

        self.nmax.setRange(1, 1_000_000_000)
        if self.nmax.value() < 2:
            self.nmax.setValue(1000000)
        self.nmax.setToolTip("Maximum number of iterations")

        for table in (self.matrix_A, self.vect_b, self.vect_x0, self.vect_sol, self.table_steps):
            if table is None:
                continue
            table.setAlternatingRowColors(True)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for table in (self.matrix_A, self.vect_b, self.vect_x0, self.vect_sol):
            if table is not None:
                table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        if self.table_steps is not None:
            self.table_steps.setEditTriggers(self.table_steps.EditTrigger.NoEditTriggers)
        if self.result_box is not None:
            self.result_box.setReadOnly(True)
        self.vect_sol.setEditTriggers(self.vect_sol.EditTrigger.NoEditTriggers)

    def connecter(self):
        self.set_dim.clicked.connect(self.appliquer_dimension)
        self.calculate.clicked.connect(self.calculer)
        if self.btn_reset is not None:
            self.btn_reset.clicked.connect(self.reinitialiser)
        if self.btn_example is not None:
            self.btn_example.clicked.connect(self.charger_exemple)
        if self.btn_best_omega is not None:
            self.btn_best_omega.clicked.connect(self.proposer_omega)
        for table in self.tables_saisie():
            table.itemChanged.connect(self.nettoyer_item)

    def tables_saisie(self):
        return [t for t in (self.matrix_A, self.vect_b, self.vect_x0) if t is not None]

    def afficher(self, texte, etat="info"):
        if self.label_status is not None:
            self.label_status.setText(texte)
            self.label_status.setProperty("state", etat)
            self.label_status.style().unpolish(self.label_status)
            self.label_status.style().polish(self.label_status)
        else:
            self.statusBar().showMessage(texte, 10000)

    def ecrire_rapport(self, texte):
        if self.result_box is not None:
            self.result_box.setPlainText(texte)

    def nettoyer_item(self, item):
        if item.background().style() != Qt.BrushStyle.NoBrush:
            table = item.tableWidget()
            table.blockSignals(True)
            item.setBackground(QBrush())
            table.blockSignals(False)

    def reinit_couleurs(self):
        for table in self.tables_saisie():
            table.blockSignals(True)
            for i in range(table.rowCount()):
                for j in range(table.columnCount()):
                    item = table.item(i, j)
                    if item is not None:
                        item.setBackground(QBrush())
            table.blockSignals(False)

    def marquer_invalides(self, mauvaises):
        brosse = QBrush(QColor(255, 82, 82, 110))
        for table, i, j in mauvaises:
            table.blockSignals(True)
            item = table.item(i, j)
            if item is None:
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(i, j, item)
            item.setBackground(brosse)
            table.blockSignals(False)
        premier = mauvaises[0]
        premier[0].setCurrentCell(premier[1], premier[2])
        premier[0].setFocus()

    def effacer_resultats(self):
        for i in range(self.vect_sol.rowCount()):
            for j in range(self.vect_sol.columnCount()):
                item = self.vect_sol.item(i, j)
                if item is not None:
                    item.setText("")
        if self.table_steps is not None:
            self.table_steps.setRowCount(0)
        if self.result_box is not None:
            self.result_box.clear()

    def appliquer_dimension(self):
        n = self.dim.value()
        self.n = n
        configs = [
            (self.matrix_A, n, [f"x{j + 1}" for j in range(n)], "0", True),
            (self.vect_b, 1, ["b"], "0", True),
            (self.vect_x0, 1, ["X0"], "0", True),
            (self.vect_sol, 1, ["X"], "", False),
        ]
        for table, cols, entetes, defaut, editable in configs:
            if table is None:
                continue
            table.blockSignals(True)
            table.setRowCount(n)
            table.setColumnCount(cols)
            table.setHorizontalHeaderLabels(entetes)
            table.setVerticalHeaderLabels([f"eq {i + 1}" if table is self.matrix_A else str(i + 1) for i in range(n)])
            for i in range(n):
                for j in range(cols):
                    if table.item(i, j) is None:
                        item = QTableWidgetItem(defaut)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        if not editable:
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        table.setItem(i, j, item)
            table.blockSignals(False)
        self.effacer_resultats()
        self.afficher(f"Dimension set to {n}×{n}. Fill your matrix.", "info")

    def reinitialiser(self):
        for table in self.tables_saisie():
            table.blockSignals(True)
            for i in range(table.rowCount()):
                for j in range(table.columnCount()):
                    item = table.item(i, j)
                    if item is not None:
                        item.setText("0")
                        item.setBackground(QBrush())
            table.blockSignals(False)
        self.effacer_resultats()
        self.omega.setValue(1.25)
        self.epsilon.setText("1e-6")
        self.nmax.setValue(1000)
        self.afficher("Everything has been reset.", "info")

    def charger_exemple(self):
        self.dim.setValue(3)
        self.appliquer_dimension()
        A = [[4, -1, 0], [-1, 4, -1], [0, -1, 4]]
        b = [2, 6, 2]
        for table in self.tables_saisie():
            table.blockSignals(True)
        for i in range(3):
            for j in range(3):
                self.matrix_A.item(i, j).setText(str(A[i][j]))
            self.vect_b.item(i, 0).setText(str(b[i]))
            if self.vect_x0 is not None:
                self.vect_x0.item(i, 0).setText("0")
        for table in self.tables_saisie():
            table.blockSignals(False)
        self.reinit_couleurs()
        self.omega.setValue(1.1)
        self.afficher("Example loaded (exact solution: X = [1, 2, 1]). Press Calculate.", "info")

    def dimension_coherente(self):
        if self.dim.value() != self.n:
            self.afficher("The dimension changed: press Set before calculating.", "warn")
            self.set_dim.setFocus()
            return False
        return True

    def lire_A(self):
        mauvaises = []
        A = engine.lire_table(self.matrix_A, self.n, self.n, mauvaises)
        return A, mauvaises

    def proposer_omega(self):
        if not self.dimension_coherente():
            return
        self.reinit_couleurs()
        A, mauvaises = self.lire_A()
        if mauvaises:
            self.marquer_invalides(mauvaises)
            self.afficher(f"{len(mauvaises)} invalid cell(s) in A (highlighted in red).", "error")
            return
        probleme = engine.analyser_systeme(A, engine.np.zeros(self.n))
        if probleme:
            self.afficher(probleme[0], "error")
            self.ecrire_rapport(probleme[1])
            return
        w, rho = engine.meilleur_omega(A)
        if w is None or rho >= 1:
            self.afficher("No ω in (0, 2) makes SOR converge for this matrix.", "error")
            return
        self.omega.setValue(w)
        self.afficher(f"Best ω found: {w:.2f}  (ρ = {rho:.4f}).", "ok")

    def calculer(self):
        if not self.dimension_coherente():
            return
        self.effacer_resultats()
        self.reinit_couleurs()
        n = self.n

        mauvaises = []
        A = engine.lire_table(self.matrix_A, n, n, mauvaises)
        b = engine.lire_table(self.vect_b, n, 1, mauvaises).ravel()
        if self.vect_x0 is not None:
            X0 = engine.lire_table(self.vect_x0, n, 1, mauvaises).ravel()
        else:
            X0 = engine.np.zeros(n)
        if mauvaises:
            self.marquer_invalides(mauvaises)
            self.afficher(
                f"{len(mauvaises)} invalid or empty cell(s), highlighted in red. "
                "Use numbers like 2, -1.5 or 1/3.",
                "error",
            )
            return

        try:
            epsilon = float(self.epsilon.text().strip().replace(",", "."))
            if not (0 < epsilon < 1):
                raise ValueError
        except ValueError:
            self.afficher("Precision ε must be a number between 0 and 1 (e.g. 1e-6).", "error")
            self.epsilon.setFocus()
            self.epsilon.selectAll()
            return

        omega = float(self.omega.value())
        Nmax = int(self.nmax.value())

        probleme = engine.analyser_systeme(A, b)
        if probleme:
            self.afficher(probleme[0], "error")
            self.ecrire_rapport(probleme[1])
            return

        D, L, U = engine.decomposer(A)
        try:
            B, M, rho_B = engine.verifier_convergence(D, L, U, omega)
        except engine.np.linalg.LinAlgError:
            self.afficher("Numerical failure while building the SOR matrix.", "error")
            return

        if rho_B >= 1 - 1e-12:
            w, rho_w = engine.meilleur_omega(A)
            conseil = (
                f"Try ω = {w:.2f} (ρ = {rho_w:.4f}), or press the best-ω button."
                if w is not None and rho_w < 1
                else "No ω in (0, 2) makes SOR converge for this matrix."
            )
            self.afficher(f"SOR does not converge: ρ(B) = {rho_B:.4f} ≥ 1. {conseil}", "error")
            self.ecrire_rapport(
                f"ρ(B) = {rho_B:.6f} ≥ 1\n"
                "The iteration matrix has a spectral radius that is too large,\n"
                "so the method diverges for most starting vectors.\n\n" + conseil
            )
            return

        C = omega * engine.np.linalg.solve(M, b)

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        t0 = time.perf_counter()
        try:
            X, k, erreur, residu, statut, historique = engine.calculer_iteration(
                A, b, B, C, X0, epsilon, Nmax
            )
        finally:
            QApplication.restoreOverrideCursor()
        duree = (time.perf_counter() - t0) * 1000

        for i in range(n):
            self.vect_sol.item(i, 0).setText(engine.fmt(X[i]))
        self.remplir_pas(historique)

        sym, spd, dominante, cond = engine.diagnostics(A)
        X_exact = engine.np.linalg.solve(A, b)
        ecart = float(engine.np.linalg.norm(X - X_exact))
        estimation = (
            int(engine.np.ceil(engine.np.log(epsilon) / engine.np.log(rho_B))) if 0 < rho_B < 1 else 1
        )

        lignes = [
            f"ω = {omega:.2f}    ε = {epsilon:g}    Nmax = {Nmax}",
            f"ρ(B) = {rho_B:.6f}  →  convergence guaranteed",
            f"Estimated iterations needed ≈ {estimation}",
            "",
            f"Iterations performed : {k}",
            f"Final error ||X_k − X_(k−1)|| : {erreur:.3e}",
            f"Residual ||AX − b|| : {residu:.3e}",
            f"Time : {duree:.2f} ms",
            "",
            "Solution X = [" + ", ".join(engine.fmt(v) for v in X) + "]",
            "Direct solve = [" + ", ".join(engine.fmt(v) for v in X_exact) + "]",
            f"||X − X_direct|| = {ecart:.3e}",
            "",
            "Matrix: "
            + ", ".join(
                [
                    "symmetric positive definite" if spd else ("symmetric" if sym else "not symmetric"),
                    "strictly diagonally dominant" if dominante else "not diagonally dominant",
                    f"cond(A) = {cond:.3e}",
                ]
            ),
        ]
        if cond > 1e12:
            lignes.append("Warning: A is very ill-conditioned, results may be inaccurate.")
        self.ecrire_rapport("\n".join(lignes))

        if statut == "converge":
            self.afficher(f"Converged in {k} iteration(s), residual {residu:.2e}.", "ok")
        elif statut == "nmax":
            self.afficher(
                f"Nmax = {Nmax} reached before ε was met (error {erreur:.2e}). "
                "Increase Nmax, relax ε or adjust ω.",
                "warn",
            )
        else:
            self.afficher(f"Divergence detected at iteration {k}. Try another ω.", "error")

    def remplir_pas(self, historique):
        table = self.table_steps
        if table is None:
            return
        n = self.n
        total = len(historique)
        if total <= MAX_STEPS_SHOWN:
            indices = list(range(total))
        else:
            indices = list(range(MAX_STEPS_SHOWN - 1)) + [total - 1]

        table.setUpdatesEnabled(False)
        table.setColumnCount(n + 3)
        table.setHorizontalHeaderLabels(
            ["k"] + [f"x{i + 1}" for i in range(n)] + ["||ΔX||", "||AX−b||"]
        )
        table.setRowCount(len(indices))
        for r, idx in enumerate(indices):
            k, X, erreur, residu = historique[idx]
            valeurs = (
                [str(k)]
                + [engine.fmt(v) for v in X]
                + ["—" if erreur is None else f"{erreur:.3e}", f"{residu:.3e}"]
            )
            for c, texte in enumerate(valeurs):
                item = QTableWidgetItem(texte)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(r, c, item)
        table.setUpdatesEnabled(True)
        table.scrollToBottom()

