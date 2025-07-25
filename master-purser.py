import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import math

GOODS = [
    "Round shot", "Grapeshot", "Chainshot", "Bombs", "Food",
    "Sailcloth", "Planks", "Bricks", "Wheat", "Clothes",
    "Fruits", "Coffee", "Cocoa", "Tobacco", "Sugar",
    "Cotton", "Leather", "Ebony", "Mahogany", "Vanilla",
    "Copra", "Paprika", "Gunpowder", "Weapon", "Medicine",
    "Wine", "Rum", "Ale", "Shipsilk", "Ropes",
    "Ironwood", "Resin", "Slaves", "Gold", "Silver"
]
DEMAND_TYPES = {
    "Colonial Good": 1,
    "Normal Good": 2,
    "Imported Good": 3,
    "Aggressively Demanded": 4,
    "Contraband": 5
}
# Reverse mapping for display
DEMAND_DISPLAY = {v: k for k, v in DEMAND_TYPES.items()}

# Goods properties including pack size and weight
GOODS_PROPERTIES = {
    "Bombs": {"pack": 20, "pack_weight": 3},
    "Bricks": {"pack": 10, "pack_weight": 6},
    # Default values for other goods
    "Round shot": {"pack": 1, "pack_weight": 1},
    "Grapeshot": {"pack": 1, "pack_weight": 1},
    "Chainshot": {"pack": 1, "pack_weight": 1},
    "Food": {"pack": 1, "pack_weight": 1},
    "Sailcloth": {"pack": 1, "pack_weight": 1},
    "Planks": {"pack": 1, "pack_weight": 1},
    "Wheat": {"pack": 1, "pack_weight": 1},
    "Clothes": {"pack": 1, "pack_weight": 1},
    "Fruits": {"pack": 1, "pack_weight": 1},
    "Coffee": {"pack": 1, "pack_weight": 1},
    "Cocoa": {"pack": 1, "pack_weight": 1},
    "Tobacco": {"pack": 1, "pack_weight": 1},
    "Sugar": {"pack": 1, "pack_weight": 1},
    "Cotton": {"pack": 1, "pack_weight": 1},
    "Leather": {"pack": 1, "pack_weight": 1},
    "Ebony": {"pack": 1, "pack_weight": 1},
    "Mahogany": {"pack": 1, "pack_weight": 1},
    "Vanilla": {"pack": 1, "pack_weight": 1},
    "Copra": {"pack": 1, "pack_weight": 1},
    "Paprika": {"pack": 1, "pack_weight": 1},
    "Gunpowder": {"pack": 1, "pack_weight": 1},
    "Weapon": {"pack": 1, "pack_weight": 1},
    "Medicine": {"pack": 1, "pack_weight": 1},
    "Wine": {"pack": 1, "pack_weight": 1},
    "Rum": {"pack": 1, "pack_weight": 1},
    "Ale": {"pack": 1, "pack_weight": 1},
    "Shipsilk": {"pack": 1, "pack_weight": 1},
    "Ropes": {"pack": 1, "pack_weight": 1},
    "Ironwood": {"pack": 1, "pack_weight": 1},
    "Resin": {"pack": 1, "pack_weight": 1},
    "Slaves": {"pack": 1, "pack_weight": 1},
    "Gold": {"pack": 1, "pack_weight": 1},
    "Silver": {"pack": 1, "pack_weight": 1}
}

class MasterPurser:
    def __init__(self, root):
        self.root = root
        self.root.title("Master Purser - Ye Olde Trading Mate")
        self.root.geometry("1000x900")
        
        # Create settlements directory if missing
        self.settlements_dir = "settlements"
        os.makedirs(self.settlements_dir, exist_ok=True)
        
        # Setup notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_city_comparison_tab()
        self.create_selling_opportunities_tab()
        self.create_price_book_tab()
        self.create_profit_calculator_tab()
        
    def create_city_comparison_tab(self):
        """Tab for comparing trade opportunities between two cities"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="City Comparison")
        
        # Configure grid weights for scaling
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        
        # City selection
        ttk.Label(frame, text="Origin City:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.origin_var = tk.StringVar()
        self.origin_cb = ttk.Combobox(frame, textvariable=self.origin_var, state="readonly")
        self.origin_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.origin_var.trace_add("write", self.compare_cities)
        
        ttk.Label(frame, text="Destination City:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.dest_var = tk.StringVar()
        self.dest_cb = ttk.Combobox(frame, textvariable=self.dest_var, state="readonly")
        self.dest_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.dest_var.trace_add("write", self.compare_cities)
        
        # Refresh city list button
        ttk.Button(frame, text="Refresh City List", command=self.populate_city_list).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Hide Contrabands checkbox
        self.hide_contraband_cc = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame, 
            text="Hide Contrabands", 
            variable=self.hide_contraband_cc,
            command=self.compare_cities
        ).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(frame, text="Profitable Trade Opportunities")
        results_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview for results
        columns = ("Good", "Origin Demand", "Destination Demand", "Profit", "Profit/Pack")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=15
        )
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Configure columns
        self.results_tree.heading("Good", text="Good")
        self.results_tree.heading("Origin Demand", text="Origin Demand")
        self.results_tree.heading("Destination Demand", text="Destination Demand")
        self.results_tree.heading("Profit", text="Profit Potential")
        self.results_tree.heading("Profit/Pack", text="Profit/Pack")
        
        self.results_tree.column("Good", width=120, anchor="w")
        self.results_tree.column("Origin Demand", width=120, anchor="center")
        self.results_tree.column("Destination Demand", width=120, anchor="center")
        self.results_tree.column("Profit", width=100, anchor="center")
        self.results_tree.column("Profit/Pack", width=100, anchor="center")
        
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Color coding for different demand types
        self.results_tree.tag_configure('colonial', background='#ccffcc')  # Light green
        self.results_tree.tag_configure('normal', background='white')      # White
        self.results_tree.tag_configure('imported', background='#cce6ff') # Light blue
        self.results_tree.tag_configure('aggressive', background='#ffcc99') # Light peach
        self.results_tree.tag_configure('contraband', background='#ffcccc') # Light red
        
        # Populate city list initially
        self.populate_city_list()
    
    def create_selling_opportunities_tab(self):
        """Tab for finding selling opportunities for specific goods"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Selling Opportunities")
        
        # Configure grid weights for scaling
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        
        # City selection
        ttk.Label(frame, text="Origin City:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.selling_origin_var = tk.StringVar()
        self.selling_origin_cb = ttk.Combobox(frame, textvariable=self.selling_origin_var, state="readonly")
        self.selling_origin_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.selling_origin_var.trace_add("write", self.update_selling_opportunities)
        
        # Good selection
        ttk.Label(frame, text="Select Good:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.selected_good_var = tk.StringVar()
        self.good_cb = ttk.Combobox(frame, textvariable=self.selected_good_var, values=GOODS, state="readonly")
        self.good_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.selected_good_var.trace_add("write", self.update_selling_opportunities)
        
        # Refresh city list button
        ttk.Button(frame, text="Refresh City List", command=self.populate_selling_city_list).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Hide Contrabands checkbox
        self.hide_contraband_so = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame, 
            text="Hide Contrabands", 
            variable=self.hide_contraband_so,
            command=self.update_selling_opportunities
        ).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(frame, text="Profitable Selling Cities")
        results_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview for results
        columns = ("City", "Demand", "Profit", "Profit/Pack")
        self.selling_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=15
        )
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.selling_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.selling_tree.xview)
        self.selling_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Configure columns
        self.selling_tree.heading("City", text="City")
        self.selling_tree.heading("Demand", text="Demand Type")
        self.selling_tree.heading("Profit", text="Profit Potential")
        self.selling_tree.heading("Profit/Pack", text="Profit/Pack")
        
        self.selling_tree.column("City", width=150, anchor="w")
        self.selling_tree.column("Demand", width=120, anchor="center")
        self.selling_tree.column("Profit", width=100, anchor="center")
        self.selling_tree.column("Profit/Pack", width=100, anchor="center")
        
        self.selling_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Color coding for different demand types
        self.selling_tree.tag_configure('colonial', background='#ccffcc')  # Light green
        self.selling_tree.tag_configure('normal', background='white')      # White
        self.selling_tree.tag_configure('imported', background='#cce6ff') # Light blue
        self.selling_tree.tag_configure('aggressive', background='#ffcc99') # Light peach
        self.selling_tree.tag_configure('contraband', background='#ffcccc') # Light red
        
        # Populate city list initially
        self.populate_selling_city_list()
    
    def create_price_book_tab(self):
        """Tab for creating/editing city price books"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Price Book")
        
        # Configure grid weights for scaling
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # City name input
        city_frame = ttk.Frame(frame)
        city_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ttk.Label(city_frame, text="City Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.city_name = tk.StringVar()
        ttk.Entry(city_frame, textvariable=self.city_name, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Goods price book frame
        goods_frame = ttk.LabelFrame(frame, text="Goods Price Book")
        goods_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        goods_frame.columnconfigure(0, weight=1)
        goods_frame.rowconfigure(0, weight=1)
        
        # Create scrollable canvas
        canvas = tk.Canvas(goods_frame)
        scrollbar = ttk.Scrollbar(goods_frame, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)
        
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create headers
        headers = ["Good", "Demand Type", "Purchase Price", "Sell Price", "Amount Available"]
        for col, header in enumerate(headers):
            ttk.Label(self.scroll_frame, text=header, font=("TkDefaultFont", 9, "bold")).grid(
                row=0, column=col, padx=5, pady=2, sticky="w")
        
        # Create demand and price entries
        self.demand_vars = {}
        self.purchase_price_vars = {}
        self.sell_price_vars = {}
        self.amount_vars = {}
        
        for row, good in enumerate(GOODS, start=1):
            # Good name
            ttk.Label(self.scroll_frame, text=good).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # Demand type
            demand_var = tk.StringVar(value="Normal Good")
            self.demand_vars[good] = demand_var
            demand_cb = ttk.Combobox(
                self.scroll_frame,
                textvariable=demand_var,
                values=list(DEMAND_TYPES.keys()),
                width=15,
                state="readonly"
            )
            demand_cb.grid(row=row, column=1, padx=5, pady=2)
            demand_var.trace_add("write", lambda *args, g=good: self.update_sell_price_state(g))
            
            # Purchase price
            purchase_price_var = tk.DoubleVar(value=0.0)
            self.purchase_price_vars[good] = purchase_price_var
            ttk.Entry(self.scroll_frame, textvariable=purchase_price_var, width=10).grid(
                row=row, column=2, padx=5, pady=2)
            
            # Sell price
            sell_price_var = tk.DoubleVar(value=0.0)
            self.sell_price_vars[good] = sell_price_var
            sell_price_entry = ttk.Entry(self.scroll_frame, textvariable=sell_price_var, width=10)
            sell_price_entry.grid(row=row, column=3, padx=5, pady=2)
            
            # Amount available
            amount_var = tk.IntVar(value=0)
            self.amount_vars[good] = amount_var
            ttk.Entry(self.scroll_frame, textvariable=amount_var, width=10).grid(
                row=row, column=4, padx=5, pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Load Price Book", command=self.load_price_book).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Price Book", command=self.save_price_book).pack(side="left", padx=5)
    
    def update_sell_price_state(self, good):
        """Update sell price state based on demand type"""
        demand = self.demand_vars[good].get()
        if demand == "Contraband":
            self.sell_price_vars[good].set(-1)
            for child in self.scroll_frame.winfo_children():
                if child.grid_info() and child.grid_info()["row"] == GOODS.index(good)+1 and child.grid_info()["column"] == 3:
                    child.configure(state="disabled")
        else:
            if self.sell_price_vars[good].get() == -1:
                self.sell_price_vars[good].set(0.0)
            for child in self.scroll_frame.winfo_children():
                if child.grid_info() and child.grid_info()["row"] == GOODS.index(good)+1 and child.grid_info()["column"] == 3:
                    child.configure(state="normal")
    
    def create_profit_calculator_tab(self):
        """Tab for calculating profit for specific trades"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Profit Calculator")
        
        # Configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        
        # Input fields
        input_frame = ttk.LabelFrame(frame, text="Trade Parameters")
        input_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        
        # Origin selection
        ttk.Label(input_frame, text="Origin City:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.calc_origin_var = tk.StringVar()
        self.calc_origin_cb = ttk.Combobox(input_frame, textvariable=self.calc_origin_var, state="readonly")
        self.calc_origin_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Destination selection
        ttk.Label(input_frame, text="Destination City:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.calc_dest_var = tk.StringVar()
        self.calc_dest_cb = ttk.Combobox(input_frame, textvariable=self.calc_dest_var, state="readonly")
        self.calc_dest_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Good selection
        ttk.Label(input_frame, text="Good:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.calc_good_var = tk.StringVar()
        self.calc_good_cb = ttk.Combobox(input_frame, textvariable=self.calc_good_var, values=GOODS, state="readonly")
        self.calc_good_cb.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Units to buy
        ttk.Label(input_frame, text="Units to Buy:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.units_var = tk.IntVar(value=0)
        ttk.Entry(input_frame, textvariable=self.units_var).grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Total centners available
        ttk.Label(input_frame, text="Total Centners Available:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.total_centners_available_var = tk.DoubleVar(value=0.0)
        ttk.Entry(input_frame, textvariable=self.total_centners_available_var).grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        # Add to purchase list button
        ttk.Button(input_frame, text="Add to Purchase List", command=self.add_to_purchase_list).grid(
            row=5, column=0, columnspan=2, pady=10
        )
        
        # Best plan button
        ttk.Button(input_frame, text="Best Profit Plan", command=self.calculate_best_plan).grid(
            row=6, column=0, columnspan=2, pady=5
        )
        
        # Purchase list
        list_frame = ttk.LabelFrame(frame, text="Purchase List")
        list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ("Good", "Units", "Packs", "Centners", "Cost", "Revenue", "Profit")
        self.purchase_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=5
        )
        
        # Configure columns
        for col in columns:
            self.purchase_tree.heading(col, text=col)
            self.purchase_tree.column(col, width=80, anchor="center")
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.purchase_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.purchase_tree.xview)
        self.purchase_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.purchase_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Remove button
        ttk.Button(frame, text="Remove Selected", command=self.remove_selected_purchase).grid(
            row=2, column=0, columnspan=2, pady=5
        )
        
        # Summary frame
        summary_frame = ttk.LabelFrame(frame, text="Summary")
        summary_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(3, weight=1)
        
        # Total cost
        ttk.Label(summary_frame, text="Total Cost:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.total_cost_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_cost_var).grid(row=0, column=1, padx=5, pady=5, sticky="e")
        
        # Total revenue
        ttk.Label(summary_frame, text="Total Revenue:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.total_revenue_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_revenue_var).grid(row=1, column=1, padx=5, pady=5, sticky="e")
        
        # Total profit
        ttk.Label(summary_frame, text="Total Profit:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.total_profit_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_profit_var).grid(row=2, column=1, padx=5, pady=5, sticky="e")
        
        # Total centners used
        ttk.Label(summary_frame, text="Total Centners Used:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.total_centners_used_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_centners_used_var).grid(row=0, column=3, padx=5, pady=5, sticky="e")
        
        # Remaining centners
        ttk.Label(summary_frame, text="Remaining Centners:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.remaining_centners_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.remaining_centners_var).grid(row=1, column=3, padx=5, pady=5, sticky="e")
        
        # Profit per centner
        ttk.Label(summary_frame, text="Profit/Centner:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.profit_per_centner_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.profit_per_centner_var).grid(row=2, column=3, padx=5, pady=5, sticky="e")
        
        # Initialize purchase list
        self.purchase_list = []
        
        # Populate city lists
        self.populate_profit_city_lists()
    
    def load_city_data(self, city_name):
        """Load city data with backward compatibility for old format"""
        try:
            with open(os.path.join(self.settlements_dir, f"{city_name}.json")) as f:
                data = json.load(f)
            
            # Check if it's old format (good: demand_value)
            if any(isinstance(v, int) for v in data.values()):
                # Convert old format to new format
                new_data = {}
                for good, value in data.items():
                    if isinstance(value, int):
                        # This is an old format entry
                        new_data[good] = {
                            "demand": value,
                            "purchase_price": 0.0,
                            "sell_price": -1 if value == 5 else 0.0,
                            "amount": 0
                        }
                    else:
                        # This is a new format entry
                        new_data[good] = value
                return new_data
            return data
        except:
            return None
    
    def populate_city_list(self):
        """Load saved city configurations into dropdowns for City Comparison"""
        cities = [f[:-5] for f in os.listdir(self.settlements_dir) if f.endswith(".json")]
        self.origin_cb["values"] = cities
        self.dest_cb["values"] = cities
        
        if cities:
            self.origin_var.set(cities[0])
            if len(cities) > 1:
                self.dest_var.set(cities[1])
    
    def populate_selling_city_list(self):
        """Load saved city configurations into dropdowns for Selling Opportunities"""
        cities = [f[:-5] for f in os.listdir(self.settlements_dir) if f.endswith(".json")]
        cities.insert(0, "At Sea")
        self.selling_origin_cb["values"] = cities
        
        if cities:
            self.selling_origin_var.set(cities[0])
    
    def populate_profit_city_lists(self):
        """Load saved city configurations into dropdowns for Profit Calculator (only real cities)"""
        cities = [f[:-5] for f in os.listdir(self.settlements_dir) if f.endswith(".json")]
        self.calc_origin_cb["values"] = cities
        self.calc_dest_cb["values"] = cities
        
        if cities:
            self.calc_origin_var.set(cities[0])
            if len(cities) > 1:
                self.calc_dest_var.set(cities[1])
    
    def save_price_book(self):
        """Save current city price book to file"""
        city_name = self.city_name.get().strip()
        if not city_name:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        price_book = {}
        for good in GOODS:
            demand_text = self.demand_vars[good].get()
            demand_value = DEMAND_TYPES.get(demand_text, 2)  # Default to Normal Good
            
            purchase_price = self.purchase_price_vars[good].get()
            sell_price = self.sell_price_vars[good].get()
            amount = self.amount_vars[good].get()
            
            # If contraband, set sell_price to -1
            if demand_value == 5:  # Contraband
                sell_price = -1
            
            price_book[good] = {
                "demand": demand_value,
                "purchase_price": purchase_price,
                "sell_price": sell_price,
                "amount": amount
            }
        
        filename = os.path.join(self.settlements_dir, f"{city_name}.json")
        with open(filename, "w") as f:
            json.dump(price_book, f, indent=2)
        
        # Reset UI after save
        self.city_name.set("")
        for good in GOODS:
            self.demand_vars[good].set("Normal Good")
            self.purchase_price_vars[good].set(0.0)
            self.sell_price_vars[good].set(0.0)
            self.amount_vars[good].set(0)
        
        messagebox.showinfo("Success", f"Price book saved for {city_name}")
        self.populate_city_list()
        self.populate_selling_city_list()
        self.populate_profit_city_lists()
    
    def load_price_book(self):
        """Load city price book from file"""
        filename = filedialog.askopenfilename(
            initialdir=self.settlements_dir,
            filetypes=[("JSON files", "*.json")]
        )
        if not filename:
            return
        
        try:
            with open(filename) as f:
                price_book = json.load(f)
            
            city_name = os.path.basename(filename)[:-5]
            self.city_name.set(city_name)
            
            for good in GOODS:
                if good in price_book:
                    good_data = price_book[good]
                    
                    # Handle both old and new formats
                    if isinstance(good_data, dict):
                        # New format
                        demand_value = good_data.get("demand", 2)
                        purchase_price = good_data.get("purchase_price", 0.0)
                        sell_price = good_data.get("sell_price", 0.0)
                        amount = good_data.get("amount", 0)
                    else:
                        # Old format (int)
                        demand_value = good_data
                        purchase_price = 0.0
                        sell_price = -1 if demand_value == 5 else 0.0
                        amount = 0
                    
                    # Convert demand value to display text
                    demand_text = DEMAND_DISPLAY.get(demand_value, "Normal Good")
                    self.demand_vars[good].set(demand_text)
                    
                    # Update prices and amount
                    self.purchase_price_vars[good].set(purchase_price)
                    self.sell_price_vars[good].set(sell_price)
                    self.amount_vars[good].set(amount)
                    
                    # Update sell price state
                    if demand_value == 5:  # Contraband
                        for child in self.scroll_frame.winfo_children():
                            if child.grid_info() and child.grid_info()["row"] == GOODS.index(good)+1 and child.grid_info()["column"] == 3:
                                child.configure(state="disabled")
                    else:
                        for child in self.scroll_frame.winfo_children():
                            if child.grid_info() and child.grid_info()["row"] == GOODS.index(good)+1 and child.grid_info()["column"] == 3:
                                child.configure(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load price book:\n{str(e)}")
    
    def compare_cities(self, *args):
        """Compare origin and destination for profitable trades"""
        origin = self.origin_var.get()
        dest = self.dest_var.get()
        
        # Skip if either city is not selected
        if not origin or not dest:
            return
        
        if origin == dest:
            # Clear results if same city is selected
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            return
        
        try:
            # Load configurations
            origin_config = self.load_city_data(origin)
            dest_config = self.load_city_data(dest)
            
            if origin_config is None or dest_config is None:
                messagebox.showerror("Error", "Failed to load city data")
                return
            
            # Clear previous results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Find profitable goods
            profitable_goods = []
            for good in GOODS:
                # Get origin data
                origin_good_data = origin_config.get(good, {})
                origin_demand = origin_good_data.get("demand", 2)
                origin_sell_price = origin_good_data.get("sell_price", 0.0)
                
                # Get destination data
                dest_good_data = dest_config.get(good, {})
                dest_demand = dest_good_data.get("demand", 2)
                dest_purchase_price = dest_good_data.get("purchase_price", 0.0)
                
                # Skip if hiding contrabands and destination demand is contraband
                if self.hide_contraband_cc.get() and dest_demand == 5:
                    continue
                
                if dest_demand > origin_demand:
                    profit = dest_demand - origin_demand
                    origin_text = DEMAND_DISPLAY.get(origin_demand, "Unknown")
                    dest_text = DEMAND_DISPLAY.get(dest_demand, "Unknown")
                    
                    # Calculate profit per pack
                    if origin_sell_price > 0 and dest_purchase_price > 0 and dest_demand != 5:
                        profit_per_pack = dest_purchase_price - origin_sell_price
                        profit_per_pack_str = f"{profit_per_pack:.2f}"
                    else:
                        profit_per_pack_str = "???"
                    
                    profitable_goods.append((good, origin_text, dest_text, profit, dest_demand, profit_per_pack_str))
            
            # Sort by profit (descending)
            profitable_goods.sort(key=lambda x: x[3], reverse=True)
            
            # Add to results tree
            for good, origin_disp, dest_disp, profit, dest_value, profit_per_pack in profitable_goods:
                # Color coding based on destination demand type
                if dest_value == 1:  # Colonial Good
                    tag = 'colonial'
                elif dest_value == 2:  # Normal Good
                    tag = 'normal'
                elif dest_value == 3:  # Imported Good
                    tag = 'imported'
                elif dest_value == 4:  # Aggressively Demanded
                    tag = 'aggressive'
                elif dest_value == 5:  # Contraband
                    tag = 'contraband'
                else:
                    tag = ''  # Default no color
                
                self.results_tree.insert("", "end", values=(
                    good,
                    origin_disp,
                    dest_disp,
                    f"+{profit}",
                    profit_per_pack
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare cities:\n{str(e)}")
    
    def update_selling_opportunities(self, *args):
        """Update selling opportunities for selected good"""
        origin = self.selling_origin_var.get()
        good = self.selected_good_var.get()
        
        # Skip if origin city or good is not selected
        if not origin or not good:
            return
        
        try:
            # Handle "At Sea" origin
            if origin == "At Sea":
                origin_demand = 0
                origin_text = "At Sea (Free)"
                origin_sell_price = 0  # Free to acquire
            else:
                # Load origin configuration
                origin_config = self.load_city_data(origin)
                if origin_config is None:
                    messagebox.showerror("Error", f"Could not load data for {origin}")
                    return
                    
                origin_good_data = origin_config.get(good, {})
                origin_demand = origin_good_data.get("demand", 2)
                origin_text = DEMAND_DISPLAY.get(origin_demand, "Unknown")
                origin_sell_price = origin_good_data.get("sell_price", 0.0)
            
            # Clear previous results
            for item in self.selling_tree.get_children():
                self.selling_tree.delete(item)
            
            # Find profitable cities
            profitable_cities = []
            for city_file in os.listdir(self.settlements_dir):
                if city_file.endswith(".json"):
                    city_name = city_file[:-5]
                    # Skip if origin is a real city and we're comparing to itself
                    if origin != "At Sea" and city_name == origin:
                        continue
                    
                    city_config = self.load_city_data(city_name)
                    if city_config is None:
                        continue
                    
                    city_good_data = city_config.get(good, {})
                    city_demand = city_good_data.get("demand", 2)
                    city_purchase_price = city_good_data.get("purchase_price", 0.0)
                    
                    # Skip if hiding contrabands and city demand is contraband
                    if self.hide_contraband_so.get() and city_demand == 5:
                        continue
                    
                    # Always show cities when origin is "At Sea"
                    if origin == "At Sea" or city_demand > origin_demand:
                        profit = city_demand - origin_demand
                        demand_text = DEMAND_DISPLAY.get(city_demand, "Unknown")
                        
                        # Calculate profit per pack
                        if origin_sell_price >= 0 and city_purchase_price > 0 and city_demand != 5:
                            profit_per_pack = city_purchase_price - origin_sell_price
                            profit_per_pack_str = f"{profit_per_pack:.2f}"
                        else:
                            profit_per_pack_str = "???"
                        
                        profitable_cities.append((city_name, demand_text, profit, city_demand, profit_per_pack_str))
            
            # Sort by profit (descending)
            profitable_cities.sort(key=lambda x: x[2], reverse=True)
            
            # Add to results tree
            for city, demand_text, profit, demand_value, profit_per_pack in profitable_cities:
                # Color coding based on destination demand type
                if demand_value == 1:  # Colonial Good
                    tag = 'colonial'
                elif demand_value == 2:  # Normal Good
                    tag = 'normal'
                elif demand_value == 3:  # Imported Good
                    tag = 'imported'
                elif demand_value == 4:  # Aggressively Demanded
                    tag = 'aggressive'
                elif demand_value == 5:  # Contraband
                    tag = 'contraband'
                else:
                    tag = ''  # Default no color
                
                self.selling_tree.insert("", "end", values=(
                    city,
                    demand_text,
                    f"+{profit}",
                    profit_per_pack
                ), tags=(tag,))
            
            if not profitable_cities:
                self.selling_tree.insert("", "end", values=(
                    "No profitable cities found", 
                    f"Current demand: {origin_text}",
                    "",
                    ""
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find selling opportunities:\n{str(e)}")
    
    def add_to_purchase_list(self):
        """Add the current trade to the purchase list"""
        good = self.calc_good_var.get()
        units = self.units_var.get()
        total_available = self.total_centners_available_var.get()
        
        if not good:
            messagebox.showerror("Error", "Please select a good")
            return
        if units <= 0:
            messagebox.showerror("Error", "Units must be greater than zero")
            return
        if total_available <= 0:
            messagebox.showerror("Error", "Total centners available must be positive")
            return
        
        # Get pack properties
        pack_size = GOODS_PROPERTIES[good]["pack"]
        pack_weight = GOODS_PROPERTIES[good]["pack_weight"]
        
        # Calculate packs (rounded up)
        packs = math.ceil(units / pack_size)
        # Calculate centners occupied (packs * pack weight)
        item_centners = packs * pack_weight
        
        # Calculate current total centners used
        current_total_used = self.get_total_centners_used()
        
        # Check if adding this item would exceed available centners
        if current_total_used + item_centners > total_available:
            messagebox.showerror("Error", "Not enough centners available")
            return
        
        # Calculate costs
        origin = self.calc_origin_var.get()
        destination = self.calc_dest_var.get()
        
        # Get purchase price
        if origin == "At Sea":
            purchase_price = 0.0  # Free at sea
        else:
            origin_config = self.load_city_data(origin)
            origin_good_data = origin_config.get(good, {}) if origin_config else {}
            purchase_price = origin_good_data.get("purchase_price", 0.0)
        
        # Get selling price
        dest_config = self.load_city_data(destination)
        dest_good_data = dest_config.get(good, {}) if dest_config else {}
        dest_demand = dest_good_data.get("demand", 2)
        sell_price = dest_good_data.get("purchase_price", 0.0)  # Destination's purchase price is what they pay when buying
        
        # If contraband at destination, cannot sell
        if dest_demand == 5:
            sell_price = 0.0
        
        cost = packs * purchase_price
        revenue = packs * sell_price
        profit = revenue - cost
        
        # Add to purchase list
        item = {
            "good": good,
            "units": units,
            "packs": packs,
            "centners": item_centners,
            "purchase_price": purchase_price,
            "selling_price": sell_price,
            "cost": cost,
            "revenue": revenue,
            "profit": profit
        }
        self.purchase_list.append(item)
        
        # Add to treeview
        self.purchase_tree.insert("", "end", values=(
            good,
            units,
            packs,
            item_centners,
            f"{cost:.2f}",
            f"{revenue:.2f}",
            f"{profit:.2f}"
        ))
        
        # Update summary
        self.update_summary()
    
    def get_total_centners_used(self):
        """Calculate total centners used from purchase list"""
        return sum(item['centners'] for item in self.purchase_list)
    
    def remove_selected_purchase(self):
        """Remove selected item from purchase list"""
        selected = self.purchase_tree.selection()
        if not selected:
            return
        
        # Get index of selected item
        index = self.purchase_tree.index(selected[0])
        
        # Remove from treeview
        self.purchase_tree.delete(selected[0])
        
        # Remove from purchase list
        self.purchase_list.pop(index)
        
        # Update summary
        self.update_summary()
    
    def update_summary(self):
        """Update the summary information"""
        total_cost = 0
        total_revenue = 0
        total_centners_used = self.get_total_centners_used()
        total_available = self.total_centners_available_var.get()
        
        for item in self.purchase_list:
            total_cost += item["cost"]
            total_revenue += item["revenue"]
        
        total_profit = total_revenue - total_cost
        remaining_centners = total_available - total_centners_used
        
        if total_centners_used > 0:
            profit_per_centner = total_profit / total_centners_used
        else:
            profit_per_centner = 0
        
        # Update variables
        self.total_cost_var.set(f"{total_cost:.2f}")
        self.total_revenue_var.set(f"{total_revenue:.2f}")
        self.total_profit_var.set(f"{total_profit:.2f}")
        self.total_centners_used_var.set(f"{total_centners_used}")
        self.remaining_centners_var.set(f"{remaining_centners:.1f}")
        self.profit_per_centner_var.set(f"{profit_per_centner:.2f}")
    
    def calculate_best_plan(self):
        """Calculate the best profit plan based on known prices and availability"""
        origin = self.calc_origin_var.get()
        destination = self.calc_dest_var.get()
        total_centners = self.total_centners_available_var.get()
        
        if not origin or not destination:
            messagebox.showerror("Error", "Please select both origin and destination cities")
            return
        if total_centners <= 0:
            messagebox.showerror("Error", "Total centners available must be positive")
            return
        
        # Load origin city data
        origin_data = self.load_city_data(origin)
        if origin_data is None:
            messagebox.showerror("Error", f"Could not load data for {origin}")
            return
        
        # Load destination city data
        dest_data = self.load_city_data(destination)
        if dest_data is None:
            messagebox.showerror("Error", f"Could not load data for {destination}")
            return
        
        # Clear current purchase list
        self.purchase_list = []
        for item in self.purchase_tree.get_children():
            self.purchase_tree.delete(item)
        
        # Find profitable goods
        profitable_goods = []
        for good in GOODS:
            # Get destination demand
            dest_good_data = dest_data.get(good, {})
            dest_demand = dest_good_data.get("demand", 2)
            
            # Skip if contraband at destination
            if dest_demand == 5:
                continue
            
            # Get origin price and availability
            origin_good_data = origin_data.get(good, {})
            purchase_price = origin_good_data.get("purchase_price", 0.0)
            available_units = origin_good_data.get("amount", 0)
                
            # Skip if price unknown or no availability
            if purchase_price <= 0 or available_units <= 0:
                continue
            
            # Get destination selling price
            sell_price = dest_good_data.get("purchase_price", 0.0)
            if sell_price <= 0:
                continue
            
            # Calculate profit per pack
            profit_per_pack = sell_price - purchase_price
            if profit_per_pack <= 0:
                continue
            
            # Get pack properties
            pack_size = GOODS_PROPERTIES[good]["pack"]
            pack_weight = GOODS_PROPERTIES[good]["pack_weight"]
            
            # Calculate max packs available
            max_packs = min(available_units // pack_size, 
                            total_centners // pack_weight)
            
            if max_packs > 0:
                # Calculate profit per centner for sorting
                profit_per_centner = profit_per_pack / pack_weight
                profitable_goods.append({
                    "good": good,
                    "profit_per_centner": profit_per_centner,
                    "profit_per_pack": profit_per_pack,
                    "pack_size": pack_size,
                    "pack_weight": pack_weight,
                    "max_packs": max_packs,
                    "purchase_price": purchase_price,
                    "sell_price": sell_price
                })
        
        # Sort by profit per centner (descending)
        profitable_goods.sort(key=lambda x: x["profit_per_centner"], reverse=True)
        
        # Allocate centners
        remaining_centners = total_centners
        purchase_plan = []
        
        for item in profitable_goods:
            if remaining_centners <= 0:
                break
            
            # Calculate how many packs we can take
            packs = min(item["max_packs"], remaining_centners // item["pack_weight"])
            if packs > 0:
                # Calculate details
                units = packs * item["pack_size"]
                centners = packs * item["pack_weight"]
                cost = packs * item["purchase_price"]
                revenue = packs * item["sell_price"]
                profit = revenue - cost
                
                # Add to purchase plan
                purchase_plan.append({
                    "good": item["good"],
                    "units": units,
                    "packs": packs,
                    "centners": centners,
                    "purchase_price": item["purchase_price"],
                    "selling_price": item["sell_price"],
                    "cost": cost,
                    "revenue": revenue,
                    "profit": profit
                })
                
                remaining_centners -= centners
        
        # Add to purchase list
        for item in purchase_plan:
            self.purchase_list.append(item)
            self.purchase_tree.insert("", "end", values=(
                item["good"],
                item["units"],
                item["packs"],
                item["centners"],
                f"{item['cost']:.2f}",
                f"{item['revenue']:.2f}",
                f"{item['profit']:.2f}"
            ))
        
        # Update summary
        self.update_summary()
        
        if not purchase_plan:
            messagebox.showinfo("Best Plan", "No profitable trade plan found")
        else:
            messagebox.showinfo("Best Plan", "Optimal profit plan calculated")

if __name__ == "__main__":
    root = tk.Tk()
    app = MasterPurser(root)
    root.mainloop()