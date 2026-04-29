import numpy as np
import random

class GeneticAlgTSP:
    def __init__(self, filename):
        # init cities
            self.cities = self.read_tsp_file(filename)
            self.num_cities = len(self.cities)
        # set hyper_params
            self.pop_size = 50
            self.mutation_rate = 0.01
        # init population
            self.population = []
            for _ in range(self.pop_size):
                individual =  list(range(self.num_cities))
                random.shuffle(individual)
                self.population.append(individual)
    
    def read_tsp_file(self, filename):
        cities = []
        with open(filename, 'r') as f:
            lines = f.readlines()
            is_cities = False
            for line in lines:
                line = line.strip()
                if line == "NODE_COORD_SECTION":
                    is_cities = True
                if line == "EOF" or not line:
                    break
                if is_cities:
                    location =  line.split()
                    cities.append([float(location[1]),float(location[2])])
        return np.array(cities)
