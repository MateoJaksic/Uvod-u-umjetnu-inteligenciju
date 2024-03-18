import sys

def dohvati_podatke(file): 
    with open(file, 'r', encoding='utf-8') as f:
        data = f.readlines()

    start_state, end_state, transitions = None, None, []
    for i in range(len(data)):
        if data[i][0] != '#':
            if end_state == None and start_state != None:
                end_state = data[i].rstrip("\n")            
            elif start_state == None:
                start_state = data[i].rstrip("\n")
            else: 
                transitions.append(data[i].rstrip("\n"))

    return start_state, end_state, transitions

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

        # algorithm

        print(f"[FOUND_SOLUTION]: {found_solution}")
        print(f"[STATES_VISITED]: {states_visited}")
        print(f"[PATH_LENGTH]: {path_length}")
        print(f"[TOTAL_COST]: {total_cost}")
        print(f"[PATH]: {path}")

    elif algorithm == "ucs":
        print("# UCS")

        # algorithm

        print(f"[FOUND_SOLUTION]: {found_solution}")
        print(f"[STATES_VISITED]: {states_visited}")
        print(f"[PATH_LENGTH]: {path_length}")
        print(f"[TOTAL_COST]: {total_cost}")
        print(f"[PATH]: {path}")

    elif algorithm == "astar":
        print(f"# A-STAR {path_heuristic}")

        # algorithm

        print(f"[FOUND_SOLUTION]: {found_solution}")
        print(f"[STATES_VISITED]: {states_visited}")
        print(f"[PATH_LENGTH]: {path_length}")
        print(f"[TOTAL_COST]: {total_cost}")
        print(f"[PATH]: {path}")



if __name__ == "__main__":
    main()