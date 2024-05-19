import sys
from itertools import chain


# Funkcija za dohvaćanje klauzula
def get_clauses(path_to_clauses):

    with open(path_to_clauses, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clauses = [(i+1, lines[i].rstrip().lower().split(" v "), (None, None)) for i in range(len(lines)) if lines[i][0] != "#"]
    return clauses


# Funkcija za dohvaćanje korisničkih komandi 
def get_commands(path_to_user_commands):

    with open(path_to_user_commands, "r", encoding="utf-8") as f:
        lines = f.readlines()

    commands = [(line.rstrip()[:-2].lower(), line.rsplit()[-1]) for line in lines if line[0] != "#"]
    return commands


# Funkcija za negiranje klauzule
def negate_clause(clause):
    if len(clause) == 1:
        if clause[0][0] == "~":
            return clause[0][1:]
        else:
            return [["~" + str(clause[0])]]
    else:
        negated_clause = []
        for literal in clause:
            if literal[0] == "~":
                negated_clause.append(literal[1:])
            else:
                negated_clause.append(["~" + str(literal)])
        return negated_clause


# Funkcija za negiranje literala
def negate_literal(literal):
    if literal[0] == "~":
        return literal[1:]
    else:
        return "~" + literal


# Funkcija za uklanjanje redundantnih klauzula
def coverage_check(clauses):
    for first_clause in clauses:
        if first_clause != None:
            for second_clause in clauses:
                # Osiguramo da nisu na istom indexu
                if second_clause != None and clauses.index(first_clause) != clauses.index(second_clause):
                    flag = False
                    for literal in first_clause[1]:
                        # Ako barem jedan literal nije isti breakat će se provjera i nećemo poništavati klauzulu zbog redundantnosti
                        if literal in second_clause[1]:
                            flag = True
                        else:
                            flag = False
                            break
                    if flag:
                        # Zašto second_clause? Jer potvrđujemo da se svaki literal iz first_clause nalazi u njoj, dakle second_clause je jednak ili dulji stoga njega trebamo poništiti!
                        clauses[clauses.index(second_clause)] = None
            
    return clauses


# Funkcija za uklanjanja klauzula koje su tautologija
def tautology_check(clause):
    for literal in clause:
        # Gledamo postoji li negacija literala u istoj klauzuli
        if negate_literal(literal) in clause:
            return True

    return False


# Funkcija za faktorizaciju
def factorization(clause):
    factorized_clause = []
    for literal in clause: 
        # Gledamo je li neki literal iz prvotne klauzule već u novokreiranoj, ukoliko nije dodajemo ga u nju, inaće preskaćemo
        if literal not in factorized_clause:
            factorized_clause.append(literal)

    return factorized_clause


# Funkcija za izgradnju klauzule
def clause_builder(first_clause, second_clause, literal, index_last):

    # List comprehension gdje iz liste nastale povezivanjem roditeljskih klauzula dobivam novu klauzulu, ignoriranjem literala i njegovog komplementa
    clause = [curr_literal for curr_literal in chain(first_clause[1], second_clause[1]) if (curr_literal != literal and curr_literal != negate_literal(literal))]

    return (index_last, factorization(clause), (second_clause[0], first_clause[0]))


# Funkcija za prvi podzadatak
def resolution(clauses):
    # Definiramo indeksnu poziciju gdje je cilj, važno za moju implementaciju SoS liste
    finish_index = len(clauses) - 1
    counter = len(clauses) - 1
    # Negiramo cilj
    for clause in negate_clause(clauses[-1][1]):
        if counter == finish_index:
            clauses[counter] = (clauses[counter][0], clause, (None, None))
            counter += 1
        else:
            clauses.append((clauses[-1][0] + 1, clause, (None, None)))
            counter += 1
    expanded_clauses = []
    used_clauses_pairs = []

    # Provjeravamo tautologiju
    for clause in clauses:
        if tautology_check(clause[1]):
            clauses[clauses.index(clause)] = None

    # Provjeravamo postoje li redundantne klauzule
    clauses = coverage_check(clauses)

    # Kroz naredni dio koda ću ostaviti pomoćne ispisne funkcije koje sam koristio prilikom testiranja
    found = False
    index = finish_index
    while index < len(clauses):
        # Počinjanjem na indexu, koji je u prvoj iteraciji na negiranom cilju, garantiramo da je jedan roditelj uvijek iz SoS liste 
        # SoS listu nisam implementirao kao zasebnu listu, nego već ovako zbog praktičnosti u mojoj implementaciji, a čuvam sve njene karakteristike
        first_clause = clauses[index]
        found = False
        #print(f"FIRST CLAUSE FOR PETLJA {first_clause}")
        if first_clause != None:
            for literal in first_clause[1]:
                #print(f"   LITERAL FOR PETLJA {literal}")
                if found == False:
                    for second_clause in clauses:
                        #print(f"      SECOND CLAUSE FOR PETLJA {second_clause}, A FIRST CLAUSE JE {first_clause}")
                        if second_clause != None and (first_clause[0], second_clause[0]) not in used_clauses_pairs:
                            # Ako postoji negirana vrijednost literala, za kojeg provjeravamo, u nekoj klauzuli, znaći da možemo poništiti i stvoriti novu klauzulu
                            if negate_literal(literal) in second_clause[1]:
                                #print(f"         PRONAĐENI KOMPLEMENTARNI LITERALI IF ZA {first_clause} - {second_clause} - {literal}")
                                found = True
                                # Dodajemo roditeljske klauzule u expanded_clauses, listu koju koristim za ispis
                                if first_clause not in expanded_clauses:
                                    expanded_clauses.append(first_clause)
                                if second_clause not in expanded_clauses:
                                    expanded_clauses.append(second_clause)
                                # Kreiramo novu klauzulu iz roditeljskih
                                new_clause = clause_builder(first_clause, second_clause, literal, len(clauses) + 1)
                                # Ukoliko prolazi provjeru tautulogije...
                                if tautology_check(new_clause[1]) == False:
                                    clauses.append(new_clause)
                                    # ...i redundantnosti, dodajemo ju u SoS listu, kao i listu za ispis
                                    clauses = coverage_check(clauses)
                                    if clauses[-1] != None:
                                        expanded_clauses.append(new_clause)
                                    #print(f"            NOVA KLAUZULA JE {expanded_clauses[-1]}")
                                    # Dodajemo par u listu dodanih parova, da ne ponavljamo radnje
                                    used_clauses_pairs.append((first_clause[0], second_clause[0]))
                                else:
                                    clauses.append(None)

                                # Ukoliko dobijemo praznu listu nakon spajanja roditeljskih klauzula, znaći da smo došli do kraja i dodajemo NIL u listu i završavamo zadatak
                                if expanded_clauses[-1][1] == []:
                                    expanded_clauses[-1] = (expanded_clauses[-1][0], ["NIL"], expanded_clauses[-1][2])
                                    return True, expanded_clauses

        index += 1

    return False, expanded_clauses


# Funkcija za drugi podzadatak 
def cooking(clauses, commands):
    knowledge_base = []
    
    # Ispisujemo bazu znanja
    print(f"Constructed with knowledge:")
    for clause in clauses:
        knowledge_base.append(clause[1])
        print(f"{' v '.join(clause[1])}")

    for command in commands:
        print()
        cooking_clauses = []
        # Ukoliko imamo upit
        if command[1] == "?":
            print(f"User's command: {command[0]} {command[1]}")
            counter = 1
            # Dodamo bazu znanja u listu koju ćemo plati funkciji iz prvog podzadatka
            for knowledge in knowledge_base:
                cooking_clauses.append((counter, knowledge, (None, None))) 
                counter += 1
            # Dodajemo ciljnu klauzulu istoj listi
            cooking_clauses.append((counter, [command[0]], (None, None)))
            finish_index = len(cooking_clauses)
            # Pozivamo funkciju iz prvog podzadatka
            successful, expanded_clauses = resolution(cooking_clauses)
            if successful:
                [print(f"{expanded_clause[0]}. {' v '.join(expanded_clause[1])}") for expanded_clause in sorted(expanded_clauses) if expanded_clause[1] in knowledge_base]
                print(f"{finish_index}. {negate_literal(command[0])}")
                print("===============")
                [print(f"{expanded_clause[0]}. {' v '.join(expanded_clause[1])} ({expanded_clause[2][0]}, {expanded_clause[2][1]})") for expanded_clause in sorted(expanded_clauses) if expanded_clause[1] not in chain(knowledge_base, [[negate_literal(command[0])]])]
                print("===============")
                print(f"[CONCLUSION]: {command[0]} is true")
            else:
                print(f"[CONCLUSION]: {command[0]} is unknown")

        # Ukoliko imamo dodavanje u bazu znanja
        elif command[1] == "+":
            print(f"User’s command: {command[0]} {command[1]}")
            # Ako klauzula ima više literala
            if len(command[0]) > 1:
                # Čistimo podatke
                splited_command = command[0].split(' v ')
                if splited_command not in knowledge_base:
                    # Dodajemo u bazu znanja
                    knowledge_base.append(splited_command)
                    print(f"Added {' v '.join(splited_command)}")
                else: 
                    print(f"{splited_command} already in knowledge base")
            else:
                if [command[0]] not in knowledge_base:
                    # Dodajemo u bazu znanja
                    knowledge_base.append([command[0]])
                    print(f"Added {command[0]}")
                else:
                    print(f"{command[0]} already in knowledge base")

        # Ukoliko imamo ukljanjanje iz baze znanja
        elif command[1] == "-":
            print(f"User’s command: {command[0]} {command[1]}")
            if len(command[0]) > 1:
                # Čistimo podatke
                splited_command = command[0].split(' v ')
                if splited_command in knowledge_base:
                    # Brišemo iz baze znanja
                    knowledge_base.pop(knowledge_base.index(splited_command))
                    print(f"Removed {' v '.join(splited_command)}")
                else: 
                    print(f"{splited_command} not in knowledge base")
            else:
                if [command[0]] in knowledge_base:
                    # Brišemo iz baze znanja
                    knowledge_base.pop(knowledge_base.index([command[0]]))
                    print(f"Removed {command[0]}")
                else: 
                    print(f"{command[0]} not in knowledge base")

    return True


# Glavna funkcija 
def main():

    # Dohvaćamo argumente navedene u komandnoj liniji
    if (len(sys.argv) == 3):
        flag = sys.argv[1]
        path_to_clauses = sys.argv[2]

        # Prvi podzadatak
        if flag == "resolution":
            clauses = get_clauses(path_to_clauses)
            finish_index = len(clauses) - 1
            finish_clause = clauses[finish_index]
            successful, expanded_clauses = resolution(clauses)

            [print(f"{expanded_clause[0]}. {' v '.join(expanded_clause[1])}") for expanded_clause in sorted(expanded_clauses) if expanded_clause[2] == (None, None)]
            print("===============")
            [print(f"{expanded_clause[0]}. {' v '.join(expanded_clause[1])} ({expanded_clause[2][0]}, {expanded_clause[2][1]})") for expanded_clause in sorted(expanded_clauses) if expanded_clause[2] != (None, None)]
            print("===============")
            if successful == True:
                print(f"[CONCLUSION]: {' v '.join(finish_clause[1])} is true")
            else:
                print(f"[CONCLUSION]: {' v '.join(finish_clause[1])} is unknown")


    elif (len(sys.argv) == 4):
        flag = sys.argv[1]
        path_to_clauses = sys.argv[2]
        path_to_user_commands = sys.argv[3]
        
        # Drugi podzadatak
        if flag == "cooking":
            clauses = get_clauses(path_to_clauses)
            commands = get_commands(path_to_user_commands)
            cooking(clauses, commands)


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
# https://youtu.be/RhWslFWaFzE?si=RZ-nCI_0HWj2q2w-