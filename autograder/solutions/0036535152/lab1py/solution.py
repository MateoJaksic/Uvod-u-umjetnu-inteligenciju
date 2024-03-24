import sys

class Node: 
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

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
                city, transitions = line[0], line[1].split(" ")
                successors[city] = { key: int(value) for (key, value) in [successor.split(",") for successor in transitions] }

    return start_state, end_state, successors

def get_heuristics_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = f.readlines()

    heuristics = {}
    for i in range(len(data)):
        if data[i][0] != "#":
            heuristics.update({ key: int(value) for (key, value) in [data[i].rstrip("\n").split(": ")] })
    return heuristics


def bfs(start_state, end_state, successors):
    start_state = Node(start_state, None)
    end_state = Node(end_state, None)
    open = []
    closed = []
    total_cost = 0
        
    open.append(start_state)
    total_cost += 1
    while len(open) != 0:
        current_city = open.pop(0)
        if current_city.name not in closed:
            closed.append(current_city.name)
            
        if current_city.name == end_state.name:
            path = []
            while current_city.name != start_state.name:
                path.append(current_city.name)
                current_city = current_city.parent
            path.append(start_state.name)

            return "yes", len(closed), len(path), float(total_cost), ' => '.join(list(reversed(path)))

        for city in sorted(successors[current_city.name].keys()):
            open.append(Node(city, current_city))
            total_cost += 1

    return "no", None, None, None, None


def ucs(start_state, end_state, successors):
    start_state = Node(start_state, None)
    end_state = Node(end_state, None)
    open = []
    closed = []
    total_cost = 0
        
    open.append({"node": start_state, "distance": 0})
    total_cost += 1
    while len(open) != 0:
        current_city = open.pop(0)
        if current_city["node"].name not in closed:
            closed.append(current_city["node"].name)
            
        if current_city["node"].name == end_state.name:
            path = []
            while current_city["node"].name != start_state.name:
                path.append(current_city["node"].name)
                current_city = {"node": current_city["node"].parent}
            path.append(start_state.name)

            return "yes", len(closed), len(path), float(total_cost), ' => '.join(list(reversed(path)))

        for city in dict(sorted(successors[current_city["node"].name].items(), key=lambda item: item[1])).keys():
            open.append({"node": Node(city, current_city["node"]), "distance": (successors[current_city['node'].name])[city]})
            total_cost += 1

    return "no", None, None, None, None

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

       start_state, end_state, transitions = get_data(path_state)

       found_solution, states_visited, path_length, total_cost, path = bfs(start_state, end_state, transitions)

       print(f"[FOUND_SOLUTION]: {found_solution}")
       if found_solution:
           print(f"[STATES_VISITED]: {states_visited}")
           print(f"[PATH_LENGTH]: {path_length}")
           print(f"[TOTAL_COST]: {total_cost}")
           print(f"[PATH]: {path}")

    elif algorithm == "ucs":
       print("# UCS")

       start_state, end_state, successors = get_data(path_state)

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

       start_state, end_state, successors = get_data(path_state)
       heuristics = get_heuristics_data(path_heuristic)

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