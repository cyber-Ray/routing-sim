import time
import tkinter as tk
from tkinter import filedialog

class Node:
    def __init__(self, id):
        self.id = id
        self.neighbors = {}
        self.routing_table = {}
        self.stable = False
        #This section initializes each node with ID, neighbors, routing_table, and stable status

    def add_neighbor(self, neighbor, cost):
        self.neighbors[neighbor] = cost
        #This adds a neighbor to the node with a cost

    def initialize_routing_table(self, all_nodes):
        for node in all_nodes:
            if node == self.id:
                self.routing_table[node] = 0
            elif node in self.neighbors:
                self.routing_table[node] = self.neighbors[node]
            else:
                self.routing_table[node] = float('inf')
        #This initializes the routing table with 0, if it is itself, the neighbor cost, or infinity if unknown. 

    def update_routing_table(self, all_nodes):
        updated_table = self.routing_table.copy()
        for dest_node in all_nodes:
            if dest_node != self.id:
                min_cost = min(self.routing_table[neighbor] + all_nodes[neighbor].routing_table[dest_node]
                               for neighbor in self.neighbors)
                updated_table[dest_node] = min_cost if min_cost < self.routing_table[dest_node] else self.routing_table[dest_node]
        self.stable = updated_table == self.routing_table
        self.routing_table = updated_table
        #This section will update the table based on what the current state of the network currently is

    def send_routing_table(self):
        return self.routing_table
        #This section will return the routing table of the current node

    def receive_routing_table(self, neighbor_routing_table):
        for node, cost in neighbor_routing_table.items():
            if node != self.id and cost != 'inf':
                total_cost = self.neighbors[node] + cost
                if node not in self.routing_table or total_cost < self.routing_table[node]:
                    self.routing_table[node] = total_cost
        #This section receives a routing table from a neighbor

class NodeGUI:
    def __init__(self, master, node, row, column):
        self.master = master
        self.node = node
        self.frame = tk.Frame(master)
        self.frame.grid(row=row, column=column)
        
        self.label = tk.Label(self.frame, text=f"Routing table for Node {self.node.id}:")
        self.label.grid(row=0, column=0)
        
        self.routing_table_text = tk.Text(self.frame, width=30, height=10)
        self.routing_table_text.grid(row=1, column=0)

        self.time_label = tk.Label(self.frame, text="")
        self.time_label.grid(row=2, column=0)
        
        self.update_routing_table()

        #This section initializes the GUI

    def set_time(self, time_ms):
        self.time_label.config(text=f"Time to reach stable state: {time_ms:.2f} milliseconds")
        #This is the label used for displaying time

    def update_routing_table(self):
        self.routing_table_text.delete('1.0', tk.END)
        for node, cost in self.node.routing_table.items():
            self.routing_table_text.insert(tk.END, f"Node {node}: Cost {cost}\n")
        #This section is used to update a each GUI window with the current node information

def read_network_from_file(filename):
    network = []
    with open(filename, 'r') as file:
        for line in file:
            network.append(tuple(map(int, line.strip().split())))
    return network
    #This section opens up the file selected, and reads the input from it. It uses that input to initialize everything

def initialize_routing(nodes, all_nodes):
    for link in network:
        node_id1, node_id2, cost = link
        nodes[node_id2].add_neighbor(node_id1, cost)
    for node in nodes.values():
        node.initialize_routing_table(all_nodes)
    update_node_gui()
    #This section is used as the first communication between nodes, so that each node now knows the links coming from their direct neighbors.

def simulate_routing(nodes, all_nodes, num_cycles, num_cycles_label, next_step_button):
    initialize_routing(nodes, all_nodes)
    num_cycles_list = [num_cycles]
    num_cycles_list[0] += 1
    num_cycles_label.config(text=f"Number of cycles: {num_cycles_list[0]}")
    next_step_button.config(command=lambda: next_step_iteration(nodes, num_cycles_list, num_cycles_label))
    #This calls the initialize_router function to start off the process. That increases the cycles by 1, then configures the button to a new function. So pressing the next step
    #button will now trigger the next_step_iteration, rather than reinitializing the table


def next_step_iteration(nodes, num_cycles, num_cycles_label):
    stable_count = sum(node.stable for node in nodes.values())
    if stable_count == len(nodes):
        num_cycles_label.config(text=f"Number of cycles to reach stable state: {num_cycles[0]}")
        return
    else:
        for node in nodes.values():
            neighbor_routing_tables = {neighbor: nodes[neighbor].send_routing_table() for neighbor in node.neighbors}
            for neighbor in neighbor_routing_tables.items():
                if node.id in neighbor_routing_tables:
                    nodes[neighbor].receive_routing_table({**neighbor_routing_tables[node.id], node.id: node.neighbors[neighbor]})
            node.update_routing_table(nodes)
        num_cycles[0] += 1
        update_node_gui()
        num_cycles_label.config(text=f"Number of cycles: {num_cycles[0]}")
    #This section performs each subsequent cycle until the network stabilizes. If all nodes are stable, it returns total cycles. Otherwise, it has every node send and receive DVs, and
    #update the GUI. The cycel is incremented by 1, and the displayed tag in the GUI updates as well.



def update_node_gui():
    for node_gui in node_guis:
        node_gui.update_routing_table()
        node_window.update()
    #This iterates through every node window and updates it

def choose_file():
    filename = filedialog.askopenfilename(initialdir="", title="Select file", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if filename:
        print("Selected file:", filename)
        global network
        network = read_network_from_file(filename)
        display_routing_table(root)
    #This is how a file is chosen. Once the button is clicked, it opens a menu in the current directory. You are then able to move through your directory so you can select
    #whatever file you want to use. Although the program only works with the input type described in the lab. Putting in a random textfile would probably get gibberish.

def simulate_until_stable(nodes, all_nodes, num_cycles, num_cycles_label, run_until_stable_button):
    start_time = time.time()
    initialize_routing(nodes, all_nodes)
    num_cycles_list = [num_cycles]
    while sum(node.stable for node in nodes.values()) < len(nodes):
        next_step_iteration(nodes, num_cycles_list, num_cycles_label)
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    print("Time until stable state:", total_time, "milliseconds")
    num_cycles_label.config(text=f"Time to reach stable state: {total_time:.2f} milliseconds")
    run_until_stable_button.config(state=tk.DISABLED)
    #This starts a timer, then starts the process of cycling through everything. It performs the first cycle, then loops through all subsequent cycles until the network is stable.
    #Once the network is stable, the loop ends, the timer stops, and the time it took is displayed in milliseconds. Then the button is disabled, as attempting to run this
    #multiple times gets odd behavior I cannot understand

def display_routing_table(root):
    global nodes
    nodes = {}
    all_nodes = set()
    for link in network:
        node_id1, node_id2, cost = link
        all_nodes.add(node_id1)
        all_nodes.add(node_id2)
        if node_id1 not in nodes:
            nodes[node_id1] = Node(node_id1)
        if node_id2 not in nodes:
            nodes[node_id2] = Node(node_id2)
        nodes[node_id1].add_neighbor(node_id2, cost)
    #This adds all of the nodes in the input into the nodes dictionary. It then adds all of the initial links to the neighbor attribute of Node.

    for node in nodes.values():
        node.initialize_routing_table(all_nodes)
    #This initializes the routing table.

    global node_guis
    node_guis = []

    global node_window
    node_window = tk.Toplevel(root)
    #This is done to create the new window for the nodes

    num_nodes = len(nodes)
    num_columns = 2
    num_rows = (num_nodes + 1 ) // num_columns
    #This calculates how many rows will be needed to fit all of the nodes

    for i, (node_id, node) in enumerate(nodes.items()):
        row = i % num_rows
        column = i // num_rows
        node_gui = NodeGUI(node_window, node, row, column)
        node_guis.append(node_gui)
    #This code creates a new GUI window for each node, and adds it to the appropriate spot of the grid format

    num_cycles = 0
    num_cycles_label = tk.Label(node_window, text="Number of cycles: 0")
    num_cycles_label.grid(row=num_rows, columnspan=2)
    #This initializes num_cycles to 0, creates a cycles label, and adjusts the grid so it will fit

    next_step_button = tk.Button(node_window, text="Next Step", command=lambda: simulate_routing(nodes, all_nodes, num_cycles, num_cycles_label, next_step_button))
    next_step_button.grid(row=num_rows + 1, column=0)
    #This creates the next step button, connects it to simulate_routing, and formats it in the window

    run_until_stable_button = tk.Button(node_window, text="Run Until Stable", command=lambda: simulate_until_stable(nodes, all_nodes, num_cycles, num_cycles_label, run_until_stable_button))
    run_until_stable_button.grid(row=num_rows + 1, column=1)
    #This creates the run until stable button, connects it to simulate_until_stable, and formats it in the window


if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Selector")
    button = tk.Button(root, text="Select File", command=choose_file)
    button.pack()
    root.mainloop()
    #This creates the file selector window and button, and starts the main loop. This is why the program runs until you close the file selector window
