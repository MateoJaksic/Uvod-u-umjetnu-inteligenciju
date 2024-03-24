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
    start_state = Node(start_state, None)  # Čvor u sebi ima informaciju o trenutnom stanju i njegovom parentu
    end_state = Node(end_state, None)
    open = []  # Open je lista otvorenih stanja koja se sastoji od čvorova
    closed = []  # Closed je lista zatvorenih stanja koja se sastoji od naziva stanja, ako bi ju punili čvorovima, onda bi razlikovalo ista stanja kao više različitih zbog parenta
    total_cost = 0 
        
    # Dodajemo početno stanje u listu otvorenih
    open.append(start_state)
    # Dok je lista otvorenih neprazna, prolazimo kroz nju
    while len(open) != 0:
        # Uzimamo prvo stanje iz liste otvorenih koje postaje trenutno stanje
        current_state = open.pop(0)
        # Ako taj čvor nije u listi zatvorenih, dodajemo ga 
        if current_state.name not in closed:
            closed.append(current_state.name)
            
        # Provjeravamo je li trenutno stanje konačno stanje
        if current_state.name == end_state.name:
            # Stvaramo putanju iz konačnog stanja do početnog stanja
            path = []
            while current_state.name != start_state.name:
                path.append(current_state.name)
                temp = current_state.name  # Spremamo ime trenutnog stanja
                current_state = current_state.parent  # Dohvaćamo parenta trenutnog stanja
                total_cost += successors[current_state.name][temp]  # Zbrajamo trošak putavanja iz parenta u trenutno stanje
            path.append(start_state.name)

            # Vraćamo potvrdu uspješnosti, broj prođenih stanja, duljinu putanje, totalnu cijenu putanje te putanju 
            return "yes", len(closed), len(path), float(total_cost), " => ".join(list(reversed(path)))

        # Ako trenutno stanje nije konačno stanje, ekspandiramo njegovu djecu i dodajemo u listu otvorenih po abecednom redoslijedu 
        for state in sorted(successors[current_state.name].keys()):
            open.append(Node(state, current_state))

    # Ukoliko je pretraživanje bilo neuspješno vraćamo potvrdu neuspješnosti
    return "no", None, None, None, None



# Funkcija za pretraživanje s jednolikom cijenom (UCS)
def ucs(start_state, end_state, successors):
    start_state = Node(start_state, None)
    end_state = Node(end_state, None)
    open = []  # Open je lista otvorenih stanja koja se sastoji od dictionarya, koji sadrži vrijednosti čvora i cijene puta, po kojoj onda sortiramo listu
    closed = []
    total_cost = 0
        
    # Dodajemo početno stanje u listu otvorenih
    open.append({"node": start_state, "price": 0})
    # Dok je lista otvorenih neprazna, prolazimo kroz nju
    while len(open) != 0:
        # Uzimamo prvo stanje iz liste otvorenih koje postaje trenutno stanje
        current_state = open.pop(0)
        # Ako taj čvor nije u listi zatvorenih, dodajemo ga 
        if current_state["node"].name not in closed:
            closed.append(current_state["node"].name)
            
        # Provjeravamo je li trenutno stanje konačno stanje
        if current_state["node"].name == end_state.name:
            path = []
            while current_state["node"].name != start_state.name:
                path.append(current_state["node"].name)
                temp = current_state["node"].name  # Spremamo ime trenutnog stanja
                current_state = {"node": current_state["node"].parent}  # Dohvaćamo parenta trenutnog stanja
                total_cost += successors[current_state["node"].name][temp]  # Zbrajamo trošak putavanja iz parenta u trenutno stanje
            path.append(start_state.name)

            # Vraćamo potvrdu uspješnosti, broj prođenih stanja, duljinu putanje, totalnu cijenu putanje te putanju 
            return "yes", len(closed), len(path), float(total_cost), " => ".join(list(reversed(path)))

        # Ako trenutno stanje nije konačno stanje, ekspandiramo njegovu djecu i dodajemo u listu otvorenih  
        for state in successors[current_state["node"].name].keys():
            open.append({"node": Node(state, current_state["node"]), "price": current_state["price"] + (successors[current_state["node"].name])[state]})
            # Sortiramo listu otvorenih po cijeni, u slučaju više stanja s istom cijenom sortiramo ih abecedno
            open = sorted(open, key=lambda x: (x["price"], x["node"].name))

    # Ukoliko je pretraživanje bilo neuspješno vraćamo potvrdu neuspješnosti
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