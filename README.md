This is a robust Python application that uses a **Genetic Algorithm (GA)** to solve the **Vehicle Routing Problem (VRP)**, complete with a graphical user interface built with Tkinter and plotting via Matplotlib.

Here is a comprehensive README.md file:


# 🚚 Genetic Algorithm Vehicle Routing Problem (VRP) Solver

A Python application featuring a **Graphical User Interface (GUI)** for solving the **Capacitated Vehicle Routing Problem (CVRP)** using a **Genetic Algorithm (GA)**. The application allows users to input customer coordinates, demands, and vehicle capacity, then visualizes the optimal routes and provides a summary of the solution.

# Screenshots:

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/4994c3d8-b9fe-42f3-9248-3b1b25bf4124" />

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/1eeefb02-8c03-4822-83d2-ee870b472b1c" />

---

## ✨ Features

* **GUI Interface (Tkinter):** Easy-to-use desktop application for inputting parameters and viewing results.
* **VRP Solver:** Implements a Genetic Algorithm for finding a near-optimal solution to the Capacitated Vehicle Routing Problem.
* **Permutation Encoding:** Uses customer sequence encoding (chromosome) and a separate `split_route` function to ensure valid vehicle loads.
* **GA Operators:** Utilizes **Tournament Selection**, **Order Crossover (OX)**, and **Swap Mutation**.
* **Visualization (Matplotlib):**
    * **Route Map:** Displays the optimal routes on a 2D coordinate plane, clearly marking the depot and customer locations.
    * **Summary Bar Chart:** Provides a summary of the distance and load for each vehicle used.

---

## 🚀 Installation and Setup

### Prerequisites

You need Python 3.x installed on your system.

### Dependencies

This project requires the following libraries. They can be installed using `pip`:

```bash
pip install numpy matplotlib tk


*(Note: `tkinter` is usually included with standard Python installations.)*

### How to Run

1.  Save the code as a Python file (e.g., `vrp_ga_gui.py`).
2.  Run the file from your terminal:

<!-- end list -->

```bash
python vrp_ga_gui.py
```

-----

## 🖥️ Usage

1.  **Input Parameters:**
      * **Customers (N):** Enter the total number of customers to visit (excluding the depot).
      * **Capacity (C):** Enter the maximum carrying capacity of a single vehicle.
2.  **Node Data Input:**
      * Enter the coordinates (`X Y`) and `Demand` for each node, separated by spaces, with one node per line.
      * **Crucial:** The **first line (Line 1)** *must* be the **Depot** coordinates with a demand of **0**.
      * The remaining lines should be the customers (C1, C2, etc.).
3.  **Run Solver:** Click the **"Run VRP Solver"** button.
4.  **View Results:** The application will display the **Total Distance**, **Vehicles Used**, and the detailed route sequence in the left panel, while the right panel updates with the two graphical plots.

### ⚙️ Fixed GA Settings

The following Genetic Algorithm parameters are currently fixed in the code:

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **GENERATIONS** | 500 | Number of iterations for the algorithm. |
| **POPULATION\_SIZE** | 100 | Number of individuals (potential solutions) in each generation. |
| **ELITE\_SIZE** | 10 | Number of best individuals carried directly to the next generation. |
| **MUTATION\_RATE**| 0.05 (5%) | Probability of swapping two customers in a child chromosome. |

-----

## 🔍 Core Algorithm Logic

The solution is based on the following key functions:

1.  **`fitness()`:** The **objective function**. It uses `split_route()` to decode the customer permutation into valid vehicle routes and calculates the **Total Distance** (the value the GA minimizes).
2.  **`split_route()`:** This is the VRP-specific constraint handler. It iterates through the customer sequence (individual) and assigns customers to a vehicle until the **Capacity (C)** is exceeded, at which point it closes the current route (returns to the Depot) and starts a new one.
3.  **`order_crossover()`:** Ensures that all customers appear exactly once in the child's sequence (maintaining feasibility for the VRP).

-----

## 📝 Future Enhancements

  * Implementing more advanced VRP initial solutions like the **Savings Heuristic** for better starting populations.
  * Adding support for time windows (VRP-TW).
  * Allowing users to customize GA parameters (e.g., `GENERATIONS`, `POPULATION_SIZE`) via the GUI.

<!-- end list -->

```
```
