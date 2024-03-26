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
                    successors[line[0][0:-1]] = None

    return start_state, end_state, successors



# Funkcija za dohvaćanje heurističkih podataka
def get_heuristics_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = f.readlines()

    heuristics = {}
    for line in data:
        if line[0] != "#":
            heuristics.update({ key: int(value) for (key, value) in [line.rstrip("\n").split(": ")] })

    # Sortiramo heuristike jer ulazi podaci imaju pojedine heuristike na krivim mjestima
    heuristics = dict(sorted(heuristics.items(), key=lambda x: x[0]))

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

            # Za slučaj da trenutno stanje nema moguće prijelaze
            if(successors[current_state.name] != None):
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

            # Za slučaj da trenutno stanje nema moguće prijelaze
            if(successors[current_state.name] != None):
                # Ako trenutno stanje nije konačno stanje, ekspandiramo njegovu djecu i dodajemo u listu otvorenih  
                for state in successors[current_state.name].keys():
                    # Funkcijom dodajemo element u heap queue
                    heapq.heappush(open, (price + (successors[current_state.name])[state], Node(state, current_state)))

    # Ukoliko je pretraživanje bilo neuspješno vraćamo potvrdu neuspješnosti
    return "no", None, None, None, None



# Funkcija za A* pretraživanje
def astar(start_state, end_state, successors, heuristics):
    start_state = Node(start_state, None)
    end_state = [state for state in end_state]
    open = []  # Open je lista otvorenih stanja, implementirana je kao heap queue zbog njegovih sposobnosti ubrzati vremensku složenost jer vraća uvijek najmanji element, a taj element se određuje prema prvom parametru tuplea koji odgovara zbroju prijeđenog i predviđenog puta, drugi parametar odgovara čvoru stanja te treći parametar koji odgovara prijeđenom putu
    heapq.heapify(open)  # Funkcija koja pretvara listu u heap queue
    closed = set()  # Closed je lista zatvorenih stanja koja se sastoji od tuplea stanja i prijeđenog puta, implementirana je kao set() zbog brzinske prednosti nad listom
    total_cost = 0

    heapq.heappush(open, (0, start_state, 0))
    while len(open) != 0:
        # Uzimamo prvo stanje iz liste otvorenih koje postaje trenutno stanje
        expected, current_state, price = heapq.heappop(open)
        # Ako taj čvor nije u listi zatvorenih, dodajemo ga i obrađujemo, inaće zbog brzine preskačemo 
        if (current_state, price) not in closed:
            closed.add((current_state, price))

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

            # Dohvaćamo listu susjednih čvorova trenutnog stanja
            for state in successors[current_state.name].keys():
                # Zastavica kojom reguliramo hoćemo li dodavati stanje u listu otvorenih
                flag = True
                # Provjeravamo je li susjedni čvor (njegovo stanje) u listi otvorenih
                for (temp_expected, temp_state, temp_price) in open:
                    # Ukoliko je onda ćemo pretpostaviti da ga ne moramo dodavati u listu otvorenih
                    if (temp_state.name == state):
                        flag = False
                        # Provjeravamo možemo li doći u spomenuto stanje brže nego što smo već zapisali u listu otvorenih
                        if ((price + (successors[current_state.name])[state]) < temp_price):
                            # Ukoliko možemo označavamo da ćemo dodavati stanje u listu otvorenih
                            flag = True
                            # Te uklanjamo neoptimalno rješenje iz liste otvorenih
                            open.remove((temp_expected, temp_state, temp_price))
                            heapq.heapify(open)
                            # heapq.heappush(open, (price + successors[current_state.name][state] + heuristics[state], Node(state, current_state), price + successors[current_state.name][state]))
                # Provjeravamo je li susjedni čvor (njegovo stanje) u listi zatvorenih
                for (temp_state, temp_price) in closed:
                    # Ukoliko je pretpostaviti ćemo da ga ne moramo dodati u listu zatvorenih
                    if (temp_state.name == state):
                        flag = False
                        # Provjeravamo možemo li ovaj put doći brže u spomenuto stanje, onda dodajemo stanje u listu otvorenih, a ovo izbacujemo iz liste zatvorenih 
                        if ((price + (successors[current_state.name])[state]) < temp_price):
                            flag = True
                            closed.pop((temp_state, temp_price))
                if flag == True:
                    heapq.heappush(open, (price + successors[current_state.name][state] + heuristics[state], Node(state, current_state), price + successors[current_state.name][state]))

    # Ukoliko je pretraživanje bilo neuspješno vraćamo potvrdu neuspješnosti
    return "no", None, None, None, None



# Funkcija za provjeru optimističnosti
def check_optimistics(heuristics, end_state, successors):
    # Zastavica koja mi govori ispravnost optimističnosti
    conclusion = True
    
    # Za svako stanje u heuristici
    for heuristic in heuristics:
        # Dohvaćamo stvarnu vrijednost putanje izračunatu UCS algoritmom tako da kao početno stanje uzimamo ono čiju heuristiku promatramo, kao konačno stanja predodređeno konačno stanje, kao i prijalaze 
        found_solution, states_visited, path_length, total_cost, path = ucs(heuristic, end_state, successors)

        # Ako zadovoljava uvjet za optimističnost
        if heuristics[heuristic] <= total_cost:
            print(f"[CONDITION]: [OK] h({heuristic}) <= h*: {float(heuristics[heuristic])} <= {float(total_cost)}")
        else:
            print(f"[CONDITION]: [ERR] h({heuristic}) <= h*: {float(heuristics[heuristic])} <= {float(total_cost)}")
            conclusion = False

    print(f"[CONCLUSION]: Heuristic is {'' if conclusion else 'not'} optimistic.")

    return None



# Funkcija za provjeru konzistentnosti
def check_consistents(heuristics, successors):
    # Zastavica koja mi govori ispravnost konzistentnosti
    conclusion = True

    # Za svako stanje u heuristici
    for heuristic in heuristics:
        # Ako postoji prijelaz iz trenutnog stanja
        if successors[heuristic] != None:
            # Za svako stanje u mogućim prijalazima, sortirano abecedno
            for state in (sorted(successors[heuristic])):
                # Ako zadovoljava uvjet za konzistentnost
                if heuristics[heuristic] <= heuristics[state] + successors[heuristic][state]:
                    print(f"[CONDITION]: [OK] h({heuristic}) <= h({state}) + c: {float(heuristics[heuristic])} <= {float(heuristics[state])} + {float(successors[heuristic][state])}")
                else:
                    print(f"[CONDITION]: [ERR] h({heuristic}) <= h({state}) + c: {float(heuristics[heuristic])} <= {float(heuristics[state])} + {float(successors[heuristic][state])}")
                    conclusion = False

    print(f"[CONCLUSION]: Heuristic is {'' if conclusion else 'not'} consistent.")

    return None



# Glavna funkcija 
def main():
    algorithm, path_state, path_heuristic, optimistic, consistent = None, None, None, None, None
    # Dohvaćamo argumente navedene u komandnoj liniji
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--alg":
            algorithm = sys.argv[i+1]
        elif sys.argv[i] == "--ss":
            path_state = sys.argv[i+1]
        elif sys.argv[i] == "--h":
            path_heuristic = sys.argv[i+1]
        elif sys.argv[i] == "--check-optimistic":
            optimistic = True
        elif sys.argv[i] == "--check-consistent":
            consistent = True

    # Ukoliko je riječ o BFS algoritmu
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

    # Ukoliko je riječ o UCS algoritmu
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

    # Ukoliko je riječ o A* algoritmu
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

    # Ukoliko je riječ o provjeri optimističnosti
    elif optimistic:
        print(f"# HEURISTIC-OPTIMISTIC {path_heuristic}")

        start_state, end_state, successors = get_data(path_state)
        heuristics = get_heuristics_data(path_heuristic)

        check_optimistics(heuristics, end_state, successors)
    
    # Ukoliko je riječ o provjeri konzistentnosti
    elif consistent:
        print(f"# HEURISTIC-CONSISTENT {path_heuristic}")

        start_state, end_state, successors = get_data(path_state)
        heuristics = get_heuristics_data(path_heuristic)

        check_consistents(heuristics, successors)


if __name__ == "__main__":
    main()


# UPUTE ZA POKRETANJE
# 
# SMJESTIMO SE U PRAVI DIREKTORIJ ZA SAMOSTALNO TESTIRANJE
# cd autograder\data\lab1\templates\lab1py
#
# AKTIVIRAMO AUTOGRADER OKOLINU S PRAVOM VERZIJOM PYTHONA
# conda activate autograder_env
# 
# SMJESTIMO SE U PRAVI DIREKTORIJ ZA AUTOGRADER
# 
# cd autograder
#
# python autograder.py lab1

# IZVORI
# https://www.geeksforgeeks.org/python-linked-list/ za Node()
# https://www.geeksforgeeks.org/deque-in-python/ za deque()
# https://www.geeksforgeeks.org/heap-queue-or-heapq-in-python/ za heapq()
# https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value za sortiranje dictionarya