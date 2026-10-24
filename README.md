# Smart Equation Solver - SOR Method

A powerful, user-friendly desktop application designed to solve linear systems of equations using the **Successive Over-Relaxation (SOR)** iterative method. 

This project was developed as a practical assignment (*contrôle*) for the **Matrix Algebra** module in the **1st Year Engineering Cycle** at **ESI Rabat (École des Sciences de l'Information)**.

---

##  Academic Context

* **Institution:** ESI Rabat (École des Sciences de l'Information)
* **Level:** 1st Year Engineering Cycle (*1ère année Cycle Ingénieur*)
* **Course:** Matrix Algebra (*Algèbre Matricielle*)
* **Professor:** M.Cherif
* **Developed by:**
  * Atir Mohammed.
  * Bahssine Houssein.

---

##  Features

* **Interactive GUI:** Built with PyQt6 for a modern, responsive, and dark-themed user experience.
* **Dynamic Matrix Sizing:** Easily scale the matrix dimension $A$ (up to 10x10) directly from the interface.
* **Smart Diagnostics:** Automatically analyzes the system for singularities, zeroes on the diagonal, and ill-conditioning before running calculations.
* **Fraction Support:** Input values natively as fractions (e.g., `1/3`) or decimals (e.g., `-1.5`) without losing floating-point precision.
* **Optimal Relaxation Factor ($\omega$):** Includes an algorithm to estimate and propose the best $\omega$ parameter to guarantee or accelerate convergence.
* **Convergence Verification:** Strictly computes the spectral radius $\rho(B_{SOR})$ to ensure mathematical validity before iterating.
* **Detailed Step Tracking:** Displays an iteration-by-iteration history table and a comprehensive execution report (time, residual error, strict direct solve comparison).

---

##  Architecture

The application follows a clean separation of concerns:
* `engine.py`: The numerical core containing all mathematical logic (NumPy operations, SOR algorithm, matrix decomposition).
* `ui.py` & `interface.ui`: The graphical interface handler (PyQt6), strictly separated from mathematical processing.
* `main.py`: The application entry point.

---

##  Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed on your system. You will also need the following libraries:

```bash
pip install PyQt6 numpy
```

### Running the Application

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```
2. Launch the application:
   ```bash
   python main.py
   ```

---

##  How to Use

1. **Set Dimensions:** Choose the matrix size (1 to 10) and click **Set**.
2. **Input Data:** Fill in the matrix $A$ and the vector $b$. You can also optionally set a starting vector $X_0$.
3. *Set Parameters:** 
   * Adjust the relaxation factor $\omega$ (between 0 and 2).
   * *Tip: Click **Best w** to let the engine find the optimal parameter for your specific matrix.*
   * Define your target precision $\epsilon$ (e.g., `1e-6`) and the maximum number of iterations.
4. **Calculate:** Click **Calculate** to see the final solution $X$, the iteration steps, and a detailed performance report.

---

##  License

This project is created for educational purposes within the curriculum of ESI Rabat.
