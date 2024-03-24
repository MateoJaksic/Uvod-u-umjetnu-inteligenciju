import sys


# Klasa za definiranje čvora
class Node: 
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent



# Funkcija za dohvaćanje podataka
def get_data(file): 
    with open(file, "r", encoding="utf-8") as f:
        data = f.readlines()

    start_state, end_state, successors = None, None, {}
    for i in range(len(data)):
        if data[i][0] != "#":
            if start_state != None and end_state == None:
                end_state = data[i].rstrip("\n")
            elif start_state == None:
                start_state = data[i].rstrip("\n")
            else: 
                line = data[i].rstrip("\n").split(": ")
                state, transitions = line[0], line[1].split(" ")
                successors[state] = { key: int(value) for (key, value) in [successor.split(",") for successor in transitions] }

    return start_state, end_state, successors



# Funkcija za dohvaćanje heurističkih podataka
def get_heuristics_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = f.readlines()

    heuristics = {}
    for i in range(len(data)):
        if data[i][0] != "#":
            heuristics.update({ key: int(value) for (key, value) in [data[i].rstrip("\n").split(": ")] })
    return heuristics



# Funkcija za pretraživanje u širinu (BFS)
def bfs(start_state, end_state, successors):
    start_state = Node(start_state, None)
    end_state = Node(end_state, None)
    open = []
    closed = []
    total_cost = 0
        
    open.append({"node": start_state, "price": 0})
    while len(open) != 0:
        current_state = open.pop(0)
        if current_state["node"].name not in closed:
            closed.append(current_state["node"].name)
            
        if current_state["node"].name == end_state.name:
            path = []
            while current_state["node"].name != start_state.name:
                path.append(current_state["node"].name)
                temp = current_state["node"].name
                current_state = {"node": current_state["node"].parent}
                total_cost += successors[current_state["node"].name][temp]
            path.append(start_state.name)

            return "yes", len(closed), len(path), float(total_cost), " => ".join(list(reversed(path)))

        for state in sorted(successors[current_state["node"].name].keys()):
            open.append({"node": Node(state, current_state["node"]), "price": (successors[current_state["node"].name])[state]})

    return "no", None, None, None, None



# Funkcija za pretraživanje s jednolikom cijenom (UCS)
def ucs(start_state, end_state, successors):
    start_state = Node(start_state, None)
    end_state = Node(end_state, None)
    open = []
    closed = []
        
    open.append({"node": start_state, "price": 0})
    while len(open) != 0:
        current_state = open.pop(0)
        if current_state["node"].name not in closed:
            closed.append(current_state["node"].name)
            
        if current_state["node"].name == end_state.name:
            path = []
            while current_state["node"].name != start_state.name:
                path.append(current_state["node"].name)
                current_state = {"node": current_state["node"].parent}
            path.append(start_state.name)

            return "yes", len(closed), len(path), float(total_cost), " => ".join(list(reversed(path)))

        for state in dict(sorted(successors[current_state["node"].name].items(), key=lambda item: item[1])).keys():
            open.append({"node": Node(state, current_state["node"]), "price": (successors[current_state["node"].name])[state]})

    return "no", None, None, None, None



# Glavna funkcija 
def main():
    algorithm, path_state, path_heuristic, optimistic, consistent = None, None, None, None, None
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--alg":
            algorithm = sys.argv[i+1]
        elif sys.argv[i] == "--ss":
            path_state = sys.argv[i+1]
        elif sys.argv[i] == "--h":
            path_heuristic = sys.argv[i+1]
        elif sys.argv[i] == "--check-optimistic":
            optimistic = sys.argv[i+1]
        elif sys.argv[i] == "--check-consistent":
            consistent = sys.argv[i+1]

    if algorithm == "bfs":
       print("# BFS")

       start_state, end_state, transitions = get_data("ai.txt")

       found_solution, states_visited, path_length, total_cost, path = bfs(start_state, end_state, transitions)

       print(f"[FOUND_SOLUTION]: {found_solution}")
       if found_solution:
           print(f"[STATES_VISITED]: {states_visited}")
           print(f"[PATH_LENGTH]: {path_length}")
           print(f"[TOTAL_COST]: {total_cost}")
           print(f"[PATH]: {path}")

    elif algorithm == "ucs":
       print("# UCS")

       start_state, end_state, successors = get_data("ai.txt")

       found_solution, states_visited, path_length, total_cost, path = ucs(start_state, end_state, successors)

       print(f"[FOUND_SOLUTION]: {found_solution}")
       if found_solution:
           print(f"[STATES_VISITED]: {states_visited}")
           print(f"[PATH_LENGTH]: {path_length}")
           print(f"[TOTAL_COST]: {total_cost}")
           print(f"[PATH]: {path}")

    elif algorithm == "astar":
       print(f"# A-STAR {path_heuristic}")

       # algorithm

       start_state, end_state, successors = get_data("istra.txt")
       heuristics = get_heuristics_data("istra_pessimistic_heuristic.txt")

       print(f"[FOUND_SOLUTION]: {found_solution}")
       if found_solution:
           print(f"[STATES_VISITED]: {states_visited}")
           print(f"[PATH_LENGTH]: {path_length}")
           print(f"[TOTAL_COST]: {total_cost}")
           print(f"[PATH]: {path}")



if __name__ == "__main__":
    main()


# UPUTE ZA POKRETANJE
# 
# SMJESTIMO SE U PRAVI DIREKTORIJ
# cd autograder\data\lab1\templates\lab1py
#
# AKTIVIRAMO AUTOGRADER OKOLINU S PRAVOM VERZIJOM PYTHONA
# conda activate autograder_env
#
# POKRENEMO TESTNI PRIMJER
# python solution.py --alg astar --ss istra.txt --h istra_heuristic.txt

# TODO: dodati implementaciju više end_statea
# TODO: dodati implementaciju nepostojanja valuea za neke transitionse
# TODO: prepraviti kod da nije state based (možda)
# TODO: vidjeti vremenski prekid