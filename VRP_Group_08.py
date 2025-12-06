import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

# --- VRP PARAMETERS (Fixed GA Settings) ---
GENERATIONS = 500
POPULATION_SIZE = 100
ELITE_SIZE = 10
MUTATION_RATE = 0.05
DEPOT_INDEX = 0

# ==============================================================================
# VRP CORE FUNCTIONS (Adapted to be reusable within the GUI structure)
# ==============================================================================

def calculate_distance_matrix(coords):
    """Calculates the Euclidean distance matrix between all nodes."""
    n = len(coords)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist = np.linalg.norm(coords[i] - coords[j])
            matrix[i, j] = dist
    return matrix

def create_individual(num_customers):
    """Creates a single chromosome (a random permutation of customer indices)."""
    customers = list(range(1, num_customers + 1))
    random.shuffle(customers)
    return customers

def create_initial_population(size, num_customers):
    """Creates the initial population of random individuals."""
    return [create_individual(num_customers) for _ in range(size)]

def split_route(individual, capacity, demand):
    """Decodes the customer permutation into valid vehicle routes."""
    routes = []
    current_route = [DEPOT_INDEX]
    current_load = 0

    for customer_index in individual:
        cust_demand = demand[customer_index]

        if current_load + cust_demand <= capacity:
            current_route.append(customer_index)
            current_load += cust_demand
        else:
            current_route.append(DEPOT_INDEX)
            routes.append(current_route)

            current_route = [DEPOT_INDEX, customer_index]
            current_load = cust_demand

    if len(current_route) > 1:
        current_route.append(DEPOT_INDEX)
        routes.append(current_route)

    return routes

def calculate_route_distance(route, matrix):
    """Calculates the total distance of a single closed route."""
    distance = 0
    for i in range(len(route) - 1):
        distance += matrix[route[i], route[i+1]]
    return distance

def fitness(individual, matrix, capacity, demand):
    """Calculates the fitness (total distance) of an individual."""
    routes = split_route(individual, capacity, demand)
    total_distance = sum(calculate_route_distance(r, matrix) for r in routes)
    return total_distance, routes

# --- GA OPERATORS (Selection, Crossover, Mutation) ---

def tournament_selection(population, matrix, capacity, demand, k=5):
    """Selects the best individual from a small tournament group."""
    tournament = random.choices(population, k=k)
    winner = min(tournament, key=lambda x: fitness(x, matrix, capacity, demand)[0])
    return winner

def order_crossover(parent1, parent2):
    """Implements the Order Crossover (OX) for permutation encoding."""
    size = len(parent1)
    child = [None] * size
    
    start, end = sorted(random.sample(range(size), 2))
    child[start:end+1] = parent1[start:end+1]
    
    parent1_segment = set(parent1[start:end+1])
    parent2_pool = [gene for gene in parent2 if gene not in parent1_segment]
    
    p2_index = 0
    for i in range(size):
        if child[i] is None:
            child[i] = parent2_pool[p2_index]
            p2_index += 1
            
    return child

def swap_mutation(individual, rate):
    """Randomly swaps two genes (customers) in the permutation."""
    individual_copy = list(individual)
    if random.random() < rate:
        idx1, idx2 = random.sample(range(len(individual_copy)), 2)
        individual_copy[idx1], individual_copy[idx2] = individual_copy[idx2], individual_copy[idx1]
    return individual_copy

# --- PLOTTING FUNCTIONS  ---

def plot_routes(coordinates, routes):
    """Visualizes the routes and returns the Figure object."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot all customers (Nodes 1 to N)
    customer_coords = coordinates[1:]
    ax.scatter(customer_coords[:, 0], customer_coords[:, 1], c='gray', marker='o', s=100, label='Customer', edgecolors='black') 
    
    # Plot the depot (Node 0)
    depot_coord = coordinates[DEPOT_INDEX]
    ax.scatter(depot_coord[0], depot_coord[1], c='red', marker='s', s=200, label='Depot (0)', edgecolors='black')
    
    colors = plt.cm.get_cmap('viridis', len(routes))

    for i, route in enumerate(routes):
        route_coords = coordinates[route]
        
        # 1. Unique Route Identification (Color and Label)
        ax.plot(route_coords[:, 0], route_coords[:, 1], 
                 color=colors(i), linestyle='-', linewidth=2.5, 
                 alpha=0.8, label=f'Route {i+1}')

        # 2. Unique Customer Identification (C# Annotation)
        for node_idx in route:
            if node_idx != DEPOT_INDEX:
                ax.annotate(f'C{node_idx}', 
                             (coordinates[node_idx][0] + 1, coordinates[node_idx][1] + 1), 
                             fontsize=10, color='darkred', fontweight='bold')

    ax.set_title('Optimal VRP Route Map')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right')
    plt.tight_layout()
    return fig

def plot_route_summary(routes, matrix, demand):
    """Visualizes the route summary and returns the Figure object."""
    route_distances = []
    route_loads = []
    route_labels = []

    for i, route in enumerate(routes):
        dist = calculate_route_distance(route, matrix)
        load = sum(demand[c] for c in route if c != DEPOT_INDEX)
        route_distances.append(dist)
        route_loads.append(load)
        route_labels.append(f'V{i+1}')

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(route_labels, route_distances, color='skyblue', edgecolor='black')
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'Dist: {route_distances[i]:.2f}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax.text(bar.get_x() + bar.get_width()/2., height * 0.4,
                f'Load: {route_loads[i]}',
                ha='center', va='center', fontsize=8, color='darkblue')

    ax.set_ylabel('Total Route Distance')
    ax.set_xlabel('Vehicle Route')
    ax.set_title('Route Summary: Distance and Load')
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    return fig

# ==============================================================================
# TKINTER GUI CLASS
# ==============================================================================

class VRPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Genetic Algorithm VRP Solver")
        self.geometry("1400x800")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        """Set up basic theme styles."""
        style = ttk.Style(self)
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))

    def create_widgets(self):
        # --- Left Panel: Input Frame ---
        input_frame = ttk.Frame(self, padding="15", style='TFrame')
        input_frame.grid(row=0, column=0, sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="VRP Input Parameters", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        # 1. Num Customers
        ttk.Label(input_frame, text="Customers (N):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.num_customers_entry = ttk.Entry(input_frame, width=10)
        self.num_customers_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.num_customers_entry.insert(0, "6") # Default value

        # 2. Vehicle Capacity
        ttk.Label(input_frame, text="Capacity (C):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.capacity_entry = ttk.Entry(input_frame, width=10)
        self.capacity_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.capacity_entry.insert(0, "100") # Default value

        # 3. Dynamic Data Input (Coordinates and Demand)
        ttk.Label(input_frame, text="Nodes (X Y Demand) - One per line:", font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, pady=(15, 5), sticky='w')
        ttk.Label(input_frame, text="Line 1 MUST be Depot (Demand 0)").grid(row=4, column=0, columnspan=2, pady=(0, 5), sticky='w')
        
        self.data_input = tk.Text(input_frame, height=15, width=40, font=('Consolas', 10), relief=tk.SUNKEN, borderwidth=1)
        self.data_input.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        # Add sample data for easy testing
        sample_data = "0 0 0\n40 40 15\n60 30 20\n30 60 30\n70 55 10\n45 25 25\n55 70 12"
        self.data_input.insert("1.0", sample_data)
        
        # Solve Button
        ttk.Button(input_frame, text="Run VRP Solver", command=self.solve_vrp_gui, style='Accent.TButton').grid(row=6, column=0, columnspan=2, pady=20, sticky='ew')

        # Results Text Output
        ttk.Label(input_frame, text="Solution Summary:", font=('Arial', 12, 'bold')).grid(row=7, column=0, columnspan=2, pady=(10, 5), sticky='w')
        self.results_text = tk.Text(input_frame, height=10, width=40, font=('Consolas', 9), relief=tk.FLAT, background='#ffffff')
        self.results_text.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # Configure weights for resizing
        input_frame.grid_rowconfigure(5, weight=1)
        input_frame.grid_rowconfigure(8, weight=1)


        # --- Right Panel: Plot Frame ---
        plot_frame = ttk.Frame(self, padding="15", style='TFrame')
        plot_frame.grid(row=0, column=1, sticky="nsew")
        plot_frame.grid_rowconfigure(0, weight=6)  # Map plot
        plot_frame.grid_rowconfigure(1, weight=4)  # Bar chart
        plot_frame.grid_columnconfigure(0, weight=1)

        self.map_container = ttk.Frame(plot_frame, relief=tk.GROOVE, borderwidth=1)
        self.map_container.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        self.map_container.grid_columnconfigure(0, weight=1)
        self.map_container.grid_rowconfigure(0, weight=1)
        
        self.bar_container = ttk.Frame(plot_frame, relief=tk.GROOVE, borderwidth=1)
        self.bar_container.grid(row=1, column=0, sticky='nsew')
        self.bar_container.grid_columnconfigure(0, weight=1)
        self.bar_container.grid_rowconfigure(0, weight=1)
        
        # Placeholder for initial display
        self.display_placeholder()
        
    def display_placeholder(self):
        """Displays initial empty plot areas."""
        self.clear_plots()
        
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.text(0.5, 0.5, "Click 'Run VRP Solver' to generate maps.", 
                ha='center', va='center', fontsize=16, color='gray')
        ax.axis('off')
        
        self.embed_plot(fig, self.map_container)
        
    def clear_plots(self):
        """Clears existing matplotlib figures from containers."""
        for widget in self.map_container.winfo_children():
            widget.destroy()
        for widget in self.bar_container.winfo_children():
            widget.destroy()
            
    def embed_plot(self, fig, container):
        """Embeds a matplotlib figure into a Tkinter container."""
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky='nsew')
        canvas.draw()
        
    def parse_input_data(self):
        """Parses data from the Text widget and validates formats."""
        try:
            num_customers = int(self.num_customers_entry.get())
            capacity = int(self.capacity_entry.get())
            
            if num_customers < 1 or capacity <= 0:
                 raise ValueError("N and C must be positive integers.")

            lines = self.data_input.get("1.0", tk.END).strip().split('\n')
            
            # Check for correct number of nodes (Depot + Customers)
            if len(lines) != num_customers + 1:
                raise ValueError(f"Expected {num_customers + 1} lines of data (Depot + {num_customers} customers), found {len(lines)}.")

            coords = []
            demand = []
            
            for i, line in enumerate(lines):
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError(f"Line {i+1} must contain X, Y, and Demand (3 values). Found {len(parts)}.")
                
                x = float(parts[0])
                y = float(parts[1])
                d = int(parts[2])
                
                coords.append([x, y])
                demand.append(d)

            # Validate Depot demand
            if demand[0] != 0:
                raise ValueError("Depot (first line) demand must be 0.")

            # Recalculate N based on parsed data (should match the entry, but safety check)
            num_customers_actual = len(coords) - 1

            return num_customers_actual, capacity, np.array(coords), np.array(demand), calculate_distance_matrix(np.array(coords))
            
        except Exception as e:
            messagebox.showerror("Input Error", f"Failed to parse input: {e}")
            return None, None, None, None, None
            
    def solve_vrp_gui(self):
        """Handles the solve button click, runs GA, and updates GUI."""
        
        # 1. Parse Input
        N, C, COORDS, DEMAND, MATRIX = self.parse_input_data()
        if N is None:
            return

        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "STATUS: Running Genetic Algorithm...\n")
        self.update_idletasks() # Force GUI update

        try:
            # 2. Initialize Population and Run GA
            population = create_initial_population(POPULATION_SIZE, N)
            best_overall_distance = float('inf')
            best_overall_individual = None
            best_overall_routes = []

            for generation in range(GENERATIONS):
                evaluated_population = []
                for individual in population:
                    dist, routes = fitness(individual, MATRIX, C, DEMAND)
                    evaluated_population.append({'individual': individual, 'distance': dist, 'routes': routes})

                evaluated_population.sort(key=lambda x: x['distance'])
                
                current_best = evaluated_population[0]
                if current_best['distance'] < best_overall_distance:
                    best_overall_distance = current_best['distance']
                    best_overall_individual = current_best['individual']
                    best_overall_routes = current_best['routes']
                
                new_population = [item['individual'] for item in evaluated_population[:ELITE_SIZE]]
                
                while len(new_population) < POPULATION_SIZE:
                    parent1 = tournament_selection(population, MATRIX, C, DEMAND)
                    parent2 = tournament_selection(population, MATRIX, C, DEMAND)

                    child = order_crossover(parent1, parent2)
                    mutated_child = swap_mutation(child, MUTATION_RATE)
                    
                    new_population.append(mutated_child)

                population = new_population

            # 3. Display Results
            output = [
                "--- FINAL SOLUTION ---",
                f"Total Distance: {best_overall_distance:.2f}",
                f"Vehicles Used: {len(best_overall_routes)}",
                f"Sequence: {best_overall_individual}\n"
            ]
            
            for i, route in enumerate(best_overall_routes):
                dist = calculate_route_distance(route, MATRIX)
                load = sum(DEMAND[c] for c in route if c != DEPOT_INDEX)
                output.append(f"V{i+1}: Route = {route}, Load = {load}, Dist = {dist:.2f}")

            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", "\n".join(output))

            # 4. Generate and Embed Plots
            self.clear_plots()
            
            # Route Map Plot
            fig_map = plot_routes(COORDS, best_overall_routes)
            self.embed_plot(fig_map, self.map_container)
            
            # Bar Summary Plot
            fig_bar = plot_route_summary(best_overall_routes, MATRIX, DEMAND)
            self.embed_plot(fig_bar, self.bar_container)

        except Exception as e:
            messagebox.showerror("Execution Error", f"An error occurred during VRP calculation: {e}")
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", f"ERROR: {e}")


if __name__ == "__main__":
    # Hide the default Tkinter console on some systems
    if sys.platform.startswith('win'):
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
            
    app = VRPApp()
    app.mainloop()

