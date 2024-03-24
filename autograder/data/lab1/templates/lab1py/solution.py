import sys
from collections import deque
import heapq


# Klasa za definiranje čvora
class Node: 
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    # Implementacija lees than metode koju koristi heap queue
    def __lt__(self, other):
        return self.name < other.name



# Funkcija za dohvaćanje podataka
def get_data(file): 
    with open(file, "r", encoding="utf-8") as f:
        data = f.readlines()

    start_state, end_state, successors = None, None, {}
    for i in range(len(data)):
        if data[i][0] != "#":
            if start_state != None and end_state == None:
                end_state = [state for state in data[i].rstrip("\n").split(" ")]  # Moguće je imati više konačnih stanja pa implementiramo kao listu konačnih stanja
            elif start_state == None:
                start_state = data[i].rstrip("\n")
            else: 
                line = data[i].rstrip("\n").split(": ")
                if len(line) == 2:  # Ako postoje prijelazi za stanje
                    state, transitions = line[0], line[1].split(" ")
                    successors[state] = { key: int(value) for (key, value) in [successor.split(",") for successor in transitions] }
                else:  # Ako ne postoje prijalazi za stanje
                    successors[line[0]] = None

    return start_state, end_state, successors



# Funkcija za dohvaćanje heurističkih podataka
def get_heuristics_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = f.readlines()

    heuristics = {}
    for line in data:
        if line[0] != "#":
            heuristics.update({ key: int(value) for (key, value) in [line.rstrip("\n").split(": ")] })
    return heuristics



# Funkcija za pretraživanje u širinu (BFS)
def bfs(start_state, end_state, successors):
    start_state = Node(start_state, None)  # Čvor u sebi ima informaciju o trenutnom stanju i njegovom parentu
    end_state = [state for state in end_state]  # Lista koja sadrži jedno ili više konačnih stanja
    open = deque()  # Open je lista otvorenih stanja koja se sastoji od čvorova i implementirana je kao deque kako bi smanjili vremensku složenost liste s O(n) prilikom pop() na O(1)
    closed = set()  # Closed je lista zatvorenih stanja koja se sastoji od naziva stanja, ako bi ju punili čvorovima, onda bi razlikovalo ista stanja kao više različitih zbog parenta, implementirana je kao set() zbog prednosti u brzini nad listom
    total_cost = 0 
        
    # Dodajemo početno stanje u listu otvorenih
    open.append(start_state)
    # Dok je lista otvorenih neprazna, prolazimo kroz nju
    while len(open) != 0:
        # Uzimamo prvo stanje iz liste otvorenih koje postaje trenutno stanje
        current_state = open.popleft()
        # Ako taj čvor nije u listi zatvorenih, dodajemo ga i obrađujemo, inaće zbog brzine preskačemo 
        if current_state.name not in closed:
            closed.add(current_state.name)
                
            # Provjeravamo je li trenutno stanje konačno stanje
            if current_state.name in end_state:
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
    end_state = [state for state in end_state]
    open = []  # Open je lista otvorenih stanja, implementirana je kao heap queue zbog njegovih sposobnosti ubrzati vremensku složenost jer vraća uvijek najmanji element, a taj element se određuje prema prvom parametru tuplea koji odgovara cijeni prijalaza između stanja, dok drugi parametar tuplea odgovara čvoru stanja
    heapq.heapify(open)  # Funkcija koja pretvara listu u heap queue
    closed = set()  # Closed je lista zatvorenih stanja koja se sastoji od naziva stanja, ako bi ju punili čvorovima, onda bi razlikovalo ista stanja kao više različitih zbog parenta, implementirana je kao set() zbog brzinske prednosti nad listom
    total_cost = 0
        
    # Dodajemo početno stanje u listu otvorenih
    heapq.heappush(open, (0, start_state))
    # Dok je lista otvorenih neprazna, prolazimo kroz nju
    while len(open) != 0:
        # Uzimamo prvo stanje iz liste otvorenih koje postaje trenutno stanje
        price, current_state = heapq.heappop(open)
        # Ako taj čvor nije u listi zatvorenih, dodajemo ga i obrađujemo, inaće zbog brzine preskačemo 
        if current_state.name not in closed:
            closed.add(current_state.name)
            
            # Provjeravamo je li trenutno stanje konačno stanje
            if current_state.name in end_state:
                path = []
                while current_state.name != start_state.name:
                    path.append(current_state.name)
                    temp = current_state.name  # Spremamo ime trenutnog stanja
                    current_state = current_state.parent  # Dohvaćamo parenta trenutnog stanja
                    total_cost += successors[current_state.name][temp]  # Zbrajamo trošak putavanja iz parenta u trenutno stanje
                path.append(start_state.name)

                # Vraćamo potvrdu uspješnosti, broj prođenih stanja, duljinu putanje, totalnu cijenu putanje te putanju 
                return "yes", len(closed), len(path), float(total_cost), " => ".join(list(reversed(path)))

            # Ako trenutno stanje nije konačno stanje, ekspandiramo njegovu djecu i dodajemo u listu otvorenih  
            for state in successors[current_state.name].keys():
                # Funkcijom dodajemo element u heap queue
                heapq.heappush(open, (price + (successors[current_state.name])[state], Node(state, current_state)))

    # Ukoliko je pretraživanje bilo neuspješno vraćamo potvrdu neuspješnosti
    return "no", None, None, None, None


def astar(start_state, end_state, successors, heuristics):
    start_state = Node(start_state, None)
    end_state = [state for state in end_state]
    open = []  # Open je lista otvorenih stanja, implementirana je kao heap queue zbog njegovih sposobnosti ubrzati vremensku složenost jer vraća uvijek najmanji element, a taj element se određuje prema prvom parametru tuplea koji odgovara cijeni prijalaza između stanja, dok drugi parametar tuplea odgovara čvoru stanja
    heapq.heapify(open)  # Funkcija koja pretvara listu u heap queue
    closed = set()  # Closed je lista zatvorenih stanja koja se sastoji od naziva stanja, ako bi ju punili čvorovima, onda bi razlikovalo ista stanja kao više različitih zbog parenta, implementirana je kao set() zbog brzinske prednosti nad listom
    total_cost = 0

    heapq.heappush(open, (0, start_state))
    while len(open) != 0:
        # Uzimamo prvo stanje iz liste otvorenih koje postaje trenutno stanje
        price, current_state = heapq.heappop(open)
        # Ako taj čvor nije u listi zatvorenih, dodajemo ga i obrađujemo, inaće zbog brzine preskačemo 
        if current_state.name not in closed:
            closed.add(current_state.name)

            # Provjeravamo je li trenutno stanje konačno stanje
            if current_state.name in end_state:
                path = []
                while current_state.name != start_state.name:
                    path.append(current_state.name)
                    temp = current_state.name  # Spremamo ime trenutnog stanja
                    current_state = current_state.parent  # Dohvaćamo parenta trenutnog stanja
                    total_cost += successors[current_state.name][temp]  # Zbrajamo trošak putavanja iz parenta u trenutno stanje
                path.append(start_state.name)

                # Vraćamo potvrdu uspješnosti, broj prođenih stanja, duljinu putanje, totalnu cijenu putanje te putanju 
                return "yes", len(closed), len(path), float(total_cost), " => ".join(list(reversed(path)))

            for state in successors[current_state.name].keys():
                state_value, state_key = None, None
                for (value, key) in open:
                    #print(f"{value} - {key.name}")
                    if (key.name == state):
                        state_value, state_key = value, key
                        if ((price + (successors[current_state.name])[state]) < state_value - heuristics[key.name]):
                            open.remove((state_value, state_key))
                            heapq.heapify(open)
                heapq.heappush(open, (price + (successors[current_state.name])[state] + heuristics[current_state.name], Node(state, current_state)))

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

        start_state, end_state, successors = get_data(path_state)
        heuristics = get_heuristics_data(path_heuristic)

        found_solution, states_visited, path_length, total_cost, path = astar(start_state, end_state, successors, heuristics)

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

# IZVORI
# https://www.geeksforgeeks.org/python-linked-list/ za Node()
# https://www.geeksforgeeks.org/deque-in-python/ za deque()
# https://www.geeksforgeeks.org/heap-queue-or-heapq-in-python/ za heapq()