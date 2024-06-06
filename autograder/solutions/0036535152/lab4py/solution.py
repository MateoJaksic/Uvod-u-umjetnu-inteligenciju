import sys
import numpy as np
 
# funkcija za obradu ulaznih podataka
def data_processing(path):
    with open(path, 'r', encoding='utf-8') as f:
        input = f.readlines()
    lines = np.array([line.rstrip().split(',') for line in input])
    header = lines[0]
    features = lines[1:]
    x = features[:, :-1].astype(float)
    y = features[:, -1].astype(float)
    return x, y

# klasa za neuronsku mrežu
class NeuralNetwork:
    # konstruktor klase
    def __init__(self, train_x, train_y, architecture):
        self.architecture_string = architecture
        self.architecture = self.setArchitecture(len(train_x[0]), architecture) # arhitektura mreže koja govori koliko je neurona u svakom sloju
        self.train_x = np.array(train_x) # x vrijednosti ulaznih vrijednosti
        self.train_y = np.array(train_y) # y vrijednosti ulaznih vrijednosti
        self.weights = self.getWeights() # matrica težina veza
        self.bias = self.getBias() # matrica vektora pristranosti
        
    # funkcija koja nam zadanu arhitekturu rastavlja na brojeve neurona u svakom sloju
    def setArchitecture(self, in_len, architecture):
        if architecture == "5s":
            return [in_len, 5, 1]
        elif architecture == "20s":
            return [in_len, 20, 1]
        elif architecture == "5s5s":
            return [in_len, 5, 5, 1]
    
    # funkcija za inicijaliziranje matrica težina 
    def getWeights(self):
        weights = []
        for index in range(1, len(self.architecture)):
            w = np.random.normal(0, 0.01, (self.architecture[index], self.architecture[index-1]))
            weights.append(w)
        return np.array(weights, dtype=object)
    
    # funkcija za inicijaliziranje matrice pristranosti
    def getBias(self):
        bias = []
        for index in range(1, len(self.architecture)):
            b = np.random.normal(0, 0.01, (self.architecture[index], 1))
            bias.append(b)
        return np.array(bias, dtype=object)        

    # funkcija za računanje kvadratnog odstupanaj
    def getError(self, x=None, y=None):
        if x is None and y is None:
            x = self.train_x
            y = self.train_y
        o = np.array([self.predict(x_i) for x_i in x])
        error = np.sum((y.reshape(-1, 1, 1) - o) ** 2)
        return error / len(x)

    # funkcija za aktivacijsku funkciju sigmoid
    def getSigmoid(self, net):
        sigmoid = 1 / (1 + np.exp(-net))
        return sigmoid
    
    # funkcija za stvaranje predikcija koja zapravo prolazi kroz mrežu i računa izlaznu vrijednost
    def predict(self, x):
        h_prev = x.reshape(x.shape[0], 1)
        for index in range(len(self.weights)-1):
            h = np.dot(self.weights[index], h_prev) + self.bias[index]
            h_prev = self.getSigmoid(h)
        h = np.dot(self.weights[-1], h_prev) + self.bias[-1]
        return h

# funkcija za kreiranje populacije
def getPopulation(population_size, train_x, train_y, architecture):
    return np.array([NeuralNetwork(train_x, train_y, architecture) for _ in range(population_size)])

# funkcija za odabir jedinki za elitizam
def getElitism(elitism, evaluations):
    if elitism == 0: # ukoliko nemamo elitizam
        return []
    sorted_evaluations = sorted(evaluations.items(), key=lambda eval: eval[1])
    reversed_evaluations = sorted_evaluations[::-1]
    best_evaluations = []
    for index in range(elitism):
        best_evaluations.append(reversed_evaluations[index][0])
    return np.array(best_evaluations)

# funkcija za dobivanje rulet vrijednosti
def getRoulette(evaluations):
    probabilities = np.array([evaluations[i]/sum(evaluations) for i in range(len(evaluations))])
    roullete = np.array([np.sum(probabilities[:i+1]) for i in range(len(probabilities))])
    return roullete

# funkcija za selekciju roditelja
def getParents(evaluations):
    roulette_values = getRoulette(evaluations)
    parent_1_index = np.searchsorted(roulette_values, np.random.rand())
    parent_2_index = np.searchsorted(roulette_values, np.random.rand())
    if parent_1_index == parent_2_index: # osiguravamo da dobijemo dva različita indexa jer će inaće dijete jedinka biti jednaka roditeljskim jedinkama
        while parent_1_index == parent_2_index:
            parent_2_index = np.searchsorted(roulette_values, np.random.rand())
    return parent_1_index, parent_2_index

# funkcija za križanje
def crossing(neural_network_1, neural_network_2):
    new_neural_network = NeuralNetwork(neural_network_1.train_x, neural_network_1.train_y, neural_network_1.architecture_string)
    new_neural_network.weights = np.array([(neural_network_1.weights[layer_index] + neural_network_2.weights[layer_index]) / 2 for layer_index in range(len(neural_network_1.weights))], dtype=object)
    new_neural_network.bias = np.array([(neural_network_1.bias[layer_index] + neural_network_2.bias[layer_index]) / 2 for layer_index in range(len(neural_network_1.bias))], dtype=object)
    return new_neural_network

# funkcija za mutaciju
def mutation(neural_network, mutation_probability, standard_deviation_mutation):
    new_neural_network = NeuralNetwork(neural_network.train_x, neural_network.train_y, neural_network.architecture_string) 
    new_neural_network.weights = np.array([layer + np.random.normal(0, standard_deviation_mutation, layer.shape) * (np.random.rand(*layer.shape) < mutation_probability) for layer in neural_network.weights], dtype=object)
    new_neural_network.bias = np.array([layer + np.random.normal(0, standard_deviation_mutation, layer.shape) * (np.random.rand(*layer.shape) < mutation_probability) for layer in neural_network.bias], dtype=object)
    return new_neural_network
            
# funkcija za genetički algoritam
def genetic_algorithm(train_x, train_y, test_x, test_y, architecture, population_size, elitism, mutation_probability, standard_deviation_mutation, iterations):    
    population = getPopulation(population_size, train_x, train_y, architecture) # kreiranje populacije jedinki
    evaluations = {index: 1/population[index].getError() for index in range(population_size)} # računanje kvadratnog odstupanja
    best_evaluations = getElitism(elitism, evaluations) # određivanje koje jedinke spadaju u elitističke, ukoliko postoji elitizam
    
    # prolazimo kroz svaku iteraciju treniranja
    for index in range(iterations):
        new_population = [] # kreiramo praznu populaciju
        
        # ukoliko imamo elitizam, dodajemo elitističke jedinke u novu populaciju 
        for i in best_evaluations:
            new_population.append(population[i])   
        
        # nakon dodavanje elitističkih jedinku popunjavamo ostatak populacije 
        for i in range(len(new_population), population_size):
            parent_1_index, parent_2_index = getParents([evaluations[j] for j in range(population_size)]) # određujemo indekse za dva roditelja
            child = crossing(population[parent_1_index], population[parent_2_index]) # križamo roditelje
            child = mutation(child, mutation_probability, standard_deviation_mutation) # mutiramo neuronsku mrežu dobivenu križanjem
            new_population.append(child) # spremamo neuronsku mrežu dobivenu mutiranjem
        
        population = new_population # spremamo novu populaciju
        evaluations = {index: 1/population[index].getError() for index in range(population_size)}  # računamo kvadratno odstupanje za populaciju
        best_evaluations = getElitism(elitism, evaluations)  # određivanje koje jedinke spadaju u elitističke, ukoliko postoji elitizam
        
        # ispis kvadratnog odstupanja za svaku 2000. iteraciju
        if (index+1) % 2000 == 0: 
            print(f"[Train error @{index+1}]: {population[best_evaluations[0]].getError() if elitism > 0 else population[getElitism(1, evaluations)[0]].getError()}")
            
    # ispis kvadratnog odstupanja za testni skup
    print(f"[Test error]: {population[best_evaluations[0]].getError(test_x, test_y) if elitism > 0 else population[getElitism(1, evaluations)[0]].getError()}")

# glavna funkcija
def main():
    # učitavanje ulaznih podataka dobivenih iz komandne linije
    train_path = sys.argv[2]
    test_path = sys.argv[4]
    architecture = sys.argv[6]
    population_size = int(sys.argv[8])
    elitism = int(sys.argv[10])
    mutation_probability = float(sys.argv[12])
    standard_deviation_mutation = float(sys.argv[14])
    iterations = int(sys.argv[16])
    
    # dohvaćanje ulaznih podataka
    train_x, train_y = data_processing(train_path)
    test_x, test_y = data_processing(test_path)
    
    # pokretanje genetskog algoritma
    genetic_algorithm(train_x, train_y, test_x, test_y, architecture, population_size, elitism, mutation_probability, standard_deviation_mutation, iterations)
    
if __name__ == "__main__":
    main()
    
# UPUTE ZA POKRETANJE
# AKTIVIRAMO AUTOGRADER OKOLINU S PRAVOM VERZIJOM PYTHONA
# conda activate autograder_env
# SMJESTIMO SE U PRAVI DIREKTORIJ ZA AUTOGRADER
# cd autograder
# POKRENEMO OCJENJIVANJE
# python autograder.py lab4

# IZVORI:
# pseudokod i koncepti iz prezentacija