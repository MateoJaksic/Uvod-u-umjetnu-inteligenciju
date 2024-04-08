import sys
from itertools import chain


# Funkcija za dohvaćanje klauzula
def get_clauses(path_to_clauses):

    with open(path_to_clauses, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clauses = [line.rstrip().lower() for line in lines if line[0] != "#"]
    return clauses


# Funkcija za dohvaćanje korisničkih komandi 
def get_commands(path_to_user_commands):

    with open(path_to_user_commands, "r", encoding="utf-8") as f:
        lines = f.readlines()

    commands = [(line.rstrip()[:-2], line.rsplit()[-1]) for line in lines if line[0] != "#"]
    return commands


# Funkcija za negiranje literala
def negate(clause):
    if type(clause) == list:
        if len(clause) == 1:
            if clause[0] == "~":
                return clause[1:]
            else:
                return ["~" + str(clause[0])]
        if len(clause) > 1:
            negated_clause = []
            for literal in clause:
                if literal[0] == "~":
                    negated_clause.append(literal[1:])
                else:
                    negated_clause.append(["~" + str(literal[0])])
            return negated_clause
    elif type(clause) == str:
        if clause[0] == "~":
            return clause[1:]
        else:
            return "~" + clause


# Funkcija za uklanjanje redundantnih klauzula
def coverage_check(clauses):
    for first_clause in clauses:
        if first_clause != None:
            for second_clause in clauses:
                if second_clause != None and clauses.index(first_clause) != clauses.index(second_clause):
                    flag = False
                    for literal in first_clause[1]:
                        if literal in second_clause[1]:
                            flag = True
                        else:
                            flag = False
                            break
                    if flag:
                        clauses[clauses.index(second_clause)] = None
            
    return clauses


# Funkcija za uklanjanja klauzula koje su tautologija
def tautology_check(clause):
    for first_literal in clause:
        for second_literal in clause:
            if clause.index(first_literal) != clause.index(second_literal):
                if negate(first_literal) in second_literal:
                    return True

    return False


# Funkcija za prvi podzadatak
def resolution(clauses):
    working_clauses = [(i+1, clauses[i].split(" v ")) for i in range(len(clauses)-1)]
    # Provjera tautologije za postojeće klauzule
    working_clauses = [None if tautology_check(working_clause[1]) else working_clause for working_clause in working_clauses]
    working_clauses = coverage_check(working_clauses)

    counter = len(working_clauses) 
    sos_clauses = []
    if len(clauses[-1].split(' v ')) == 1:
        [sos_clauses.append((len(working_clauses) + 1, negate(clauses[-1].split(" v "))))]
    else:
        for literal in negate(clauses[-1].split(" v ")):
            counter += 1
            sos_clauses.append((counter, literal))
            
    expanded_clauses = []
    for first_clause in sos_clauses:
        for literal in first_clause[1]:
            for second_clause in working_clauses:
                if second_clause != None:
                    if negate(literal) in second_clause[1]:
                        expanded_clauses.append((second_clause[0],  
                                                " v ".join(second_clause[1]),
                        ))
                        if len(first_clause) == 3:
                            expanded_clauses.append((first_clause[0],     
                                                    " v ".join(first_clause[1]),
                                                    first_clause[2]
                            ))
                        else:
                            expanded_clauses.append((first_clause[0],    
                                                    " v ".join(first_clause[1]),
                            ))

                        sos_clauses.append((sos_clauses[-1][0] + 1,
                                            [curr_literal for curr_literal in chain(first_clause[1], second_clause[1]) if (curr_literal != literal and curr_literal != negate(literal))],
                                            (second_clause[0], first_clause[0])
                        ))

                        working_clauses[working_clauses.index(second_clause)] = None

                        if sos_clauses[-1][1] == []:
                            expanded_clauses.append((sos_clauses[-1][0],
                                                    "NIL",
                                                    sos_clauses[-1][2]

                            ))
                            return True, expanded_clauses

    if len(expanded_clauses) == 0:
        for clause in working_clauses:
            if clause != None:  
                expanded_clauses.append(clause)
        for clause in sos_clauses:
            expanded_clauses.append(clause)
    
    # # Dodavanje postojećih klauzula u listu za ispis
    # working_clauses = [(i+1, clauses[i].split(" v ")) for i in range(len(clauses))]
    # expanded_clauses = [(i+1, clauses[i]) for i in range(len(clauses))]
 
    # # Prepravljanje ciljne klauzule u negiranu vrijednost
    # working_clauses[-1] = (working_clauses[-1][0], negate(working_clauses[-1][1]))
    # expanded_clauses[-1] = (expanded_clauses[-1][0], negate(expanded_clauses[-1][1]))

    # working_clauses = [None if tautology_check(working_clause[1]) else working_clause for working_clause in working_clauses]

    # working_clauses = coverage_check(working_clauses)
    # for first_clause in working_clauses:
    #     found = False
    #     if first_clause != None:
    #         #print(f"Istražujemo {first_clause[0]}. klauzulu {first_clause[1]}")
    #         for literal in first_clause[1]:
    #             #print(f"   Provjeravamo za literal {literal}")
    #             for second_clause in working_clauses:
    #                 if second_clause != None:
    #                     #print(f"      Provjeravamo u {second_clause[0]}. klauzuli {second_clause[1]}")
    #                     if working_clauses.index(first_clause) != working_clauses.index(second_clause):
    #                         #print(f"         Gledamo postoji li literal {negate(literal)} u klauzuli")
    #                         if negate(literal) in second_clause[1]:
    #                             #print(f"            Iz {first_clause[0]}. klauzule {first_clause[1]} uzimamo literal {literal} i pronalazimo komplementarni literal u {second_clause[0]}. klauzuli {second_clause[1]}")
    #                             if tautology_check([curr_literal for curr_literal in chain(first_clause[1], second_clause[1]) if (curr_literal != literal and curr_literal != negate(literal))]) == False:
    #                                 expanded_clauses.append((len(expanded_clauses) + 1, 
    #                                                         " v ".join([curr_literal for curr_literal in chain(first_clause[1], second_clause[1]) if (curr_literal != literal and curr_literal != negate(literal))]),
    #                                                         (working_clauses.index(first_clause) + 1, working_clauses.index(second_clause) + 1)))
    #                                 working_clauses.append((len(working_clauses) + 1,
    #                                                         [curr_literal for curr_literal in chain(first_clause[1], second_clause[1]) if (curr_literal != literal and curr_literal != negate(literal))]
    #                                 ))
    #                                 if working_clauses[-1][1] == []:
    #                                     expanded_clauses.append((expanded_clauses[-1][0], 
    #                                                             "NIL",
    #                                                             expanded_clauses[-1][2]))
    #                                     expanded_clauses.pop(-2)
    #                                     successful = True
    #                                     return successful, expanded_clauses
    #                                 working_clauses[working_clauses.index(first_clause)] = None
    #                                 working_clauses[working_clauses.index(second_clause)] = None
    #                                 found = True
    #                                 #print(f"            Expanded clauses je {expanded_clauses}")
    #                                 #print(f"            Working clauses je {working_clauses}")
    #                                 break
    #                     if found:
    #                         break
    #             if found:
    #                 break

    #print(f"Expanded clauses je {expanded_clauses}")
    #print(f"Working clauses je {working_clauses}")

    return False, expanded_clauses

# Glavna funkcija 
def main():

    # Dohvaćamo argumente navedene u komandnoj liniji
    if (len(sys.argv) == 3):
        flag = sys.argv[1]
        path_to_clauses = sys.argv[2]

        if flag == "resolution":
            clauses = get_clauses(path_to_clauses)
            successful, expanded_clauses = resolution(clauses)

            [print(f"{expanded_clause[0]}. {expanded_clause[1]}") for expanded_clause in sorted(expanded_clauses) if len(expanded_clause) == 2]
            print("===============")
            [print(f"{expanded_clause[0]}. {expanded_clause[1]} ({expanded_clause[2][0]}, {expanded_clause[2][1]})") for expanded_clause in sorted(expanded_clauses) if len(expanded_clause) == 3]
            print("===============")
            if successful == True:
                print(f"[CONCLUSION]: {clauses[-1]} is true")
            else:
                print(f"[CONCLUSION]: {clauses[-1]} is unknown")


    elif (len(sys.argv) == 4):
        flag = sys.argv[1]
        path_to_clauses = sys.argv[2]
        path_to_user_commands = sys.argv[3]
        
        if flag == "cooking":
            clauses = get_clauses(path_to_clauses)
            commands = get_commands(path_to_user_commands)




if __name__ == "__main__":
    main()


# UPUTE ZA POKRETANJE
# 
# SMJESTIMO SE U PRAVI DIREKTORIJ ZA SAMOSTALNO TESTIRANJE
# cd autograder\data\lab2\templates\lab2py
#
# AKTIVIRAMO AUTOGRADER OKOLINU S PRAVOM VERZIJOM PYTHONA
# conda activate autograder_env
# 
# SMJESTIMO SE U PRAVI DIREKTORIJ ZA AUTOGRADER
# cd autograder
#
# POKRENEMO OCJENJIVANJE
# python autograder.py lab2

# IZVORI
# prezentacije predmeta
# 