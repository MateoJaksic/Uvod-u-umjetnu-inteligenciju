import sys
from math import log2

class Leaf:
    def __init__(self, value):
        self.value = value

class Node:
    def __init__(self, name, subtrees):
        self.name = name
        self.subtrees = subtrees

class Dataset:
    def __init__(self, D, D_parent, X, Y):
        self.D = D
        self.D_parent = D_parent
        self.X = X
        self.Y = Y

def data_processing(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header = lines[0].rstrip().split(',')
    features = [line.rstrip().split(',') for line in lines[1:]]
    
    root = Dataset(None, None, None, None)
    
    root.D = {header[index]: [row[index] for row in features] for index in range(len(header))}
    root.D_parent = None
    root.X = header
    root.y = None
    
    return root

def IG(x, D, Y):
    E_D = entropy(None, D[x], Y)
    D_v = [] * len(set(D[x]))
    
    ig = E_D
    for feature in set(D[x]):
        ig -= (D[x].count(feature) / len(D[x])) * entropy(feature, D[x], Y)

    return ig

def entropy(x, D, Y):
    frequencies = [0 for solution in set(Y)]
    total, entropy = 0, 0
    
    for index_solution, solution in enumerate(set(Y)):
        for index_element, element in enumerate(D):
            if (x == element or x == None) and solution == Y[index_element]:
                total += 1
                frequencies[index_solution] += 1

    for frequency in frequencies:
        if frequency != 0:
            entropy += -1 * ((frequency/total) * log2(frequency/total))
        
    return entropy

def decide_max(ig):
    max_value = max(ig.values())
    max_ig = {k: v for k, v in ig.items() if v == max_value}
    
    return sorted(max_ig)[0]

def reduce_D(v, x, D, X):
    reduced_D = {}
    reduced_X = []
    
    indexes = []
    for index, element in enumerate(D[x]):
        if element == v:
            indexes.append(index)
            
    for element in X:        
        if element != x:
            reduced_D[element] = [feature for index, feature in enumerate(D[element]) if index in indexes]
            reduced_X.append(element)
    
    return reduced_D, reduced_X

def most_common(D):
    key = list(D.keys())[-1]
    frequencies = {solution: 0 for solution in set(D[key])}
    
    for solution in set(D[key]):
        for element in D[key]:
            if solution == element:
                frequencies[solution] += 1
            
    max_value = max(frequencies.values())
    max_frequency = {k: v for k, v in frequencies.items() if v == max_value}            
    
    return sorted(max_frequency)[0]

def id3(D, D_parent, X, y, d):

    if len(D) == 1:
        v = most_common(D_parent)
        return Leaf(v)
    
    v = most_common(D)
    
    if len(X) == 1 or D == D_parent or d == 0:
        return Leaf(v)
    
    ig = {}
    for x in X[:-1]:
        ig[x] = IG(x, D, D[X[-1]])
        print(f"IG({x})={ig[x]:.4f}", end=" ")
    print()
        
    x = decide_max(ig)
    subtrees = []
    
    for v in set(D[x]):
        new_D_parent = D
        new_D, new_X = reduce_D(v, x, D, X)
        if entropy(v, D[x], D[X[-1]]) == 0:
             subtrees.append((v, x, Leaf(new_D[new_X[-1]][0]), d))
        else:
            t = id3(new_D, new_D_parent, new_X, y, d-1)
            subtrees.append((v, x, t, d))
    
    return Node(x, subtrees)

def branches(nodes, index):   
    strings = [] 
    for node in nodes:
        if type(node[2]) == Node:
            extentions = branches(node[2].subtrees, index+1)
            
            for extention in extentions:
                strings.append(f"{index}:{node[1]}={node[0]} {extention}")
        elif type(node[2]) == Leaf:
            strings.append(f"{index}:{node[1]}={node[0]} {node[2].value}")
    
    return strings
        
def predict(D, index, node, knowledge, D_parent):
    possibilities = {feature_value[0]: feature_index for feature_index, feature_value in enumerate(knowledge)}
    
    if D[node][index] not in possibilities:
        return most_common(D)
    i = possibilities[D[node][index]]
    
    if type(knowledge[i][2]) == Leaf:
        return knowledge[i][2].value
    
    return predict(D, index, knowledge[i][2].subtrees[0][1], knowledge[i][2].subtrees, D_parent)

class ID3:
    def __init__(self, knowledge=None):
        self.knowledge = knowledge
        return None
    
    def fit(self, dataset, depth):
        self.knowledge = id3(dataset.D, dataset.D_parent, dataset.X, dataset.y, depth).subtrees
        
        print("[BRANCHES]:")
        strings = '\n'.join(branches(self.knowledge, 1))
        print(strings)
    
    def predict(self, dataset):
        total = len(dataset.D[dataset.X[-1]])
        root = self.knowledge[0][1]
        correct = 0
        possible = sorted(list(set(dataset.D[dataset.X[-1]])))
        confusion = [[0 for _ in range(len(possible))] for _ in range(len(possible))]

        print("[PREDICTIONS]: ", end="")
        for i in range(total):
            prediction = predict(dataset.D, i, root, self.knowledge, dataset.D_parent)
            print(prediction, end=" ")
            solution = dataset.D[dataset.X[-1]][i]
            if prediction == solution:
                correct += 1
            prediction_index = possible.index(prediction)
            solution_index = possible.index(solution)
            confusion[solution_index][prediction_index] += 1
            
        accuracy = correct / total
        
        print(f"\n[ACCURACY]: {accuracy:.5f}")
        
        print(f"[CONFUSION_MATRIX]:")
        for i in range(len(possible)):
            for j in range(len(possible)):
                print(confusion[i][j], end=" ")
            print() 
        

def main():
    if len(sys.argv) == 3:
        path_train = sys.argv[1]
        path_test = sys.argv[2]
        depth = -1
    else:
        path_train = sys.argv[1]
        path_test = sys.argv[2]
        depth = sys.argv[3]
    
    train_dataset = data_processing(path_train)
    test_dataset = data_processing(path_test)
    
    model = ID3()
    
    model.fit(train_dataset, int(depth))
    model.predict(test_dataset)

if __name__ == "__main__":
    main()
    
    
# UPUTE ZA POKRETANJE
#
# AKTIVIRAMO AUTOGRADER OKOLINU S PRAVOM VERZIJOM PYTHONA
# conda activate autograder_env
# 
# SMJESTIMO SE U PRAVI DIREKTORIJ ZA AUTOGRADER
# cd autograder
#
# POKRENEMO OCJENJIVANJE
# python autograder.py lab3
