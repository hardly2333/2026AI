import numpy as np
import random
import os
import sys
import time
import argparse

# GeneticAlgTSP 封装了 TSP 的遗传算法流程：数据读取、距离预计算、选择、交叉、变异和迭代优化。
class GeneticAlgTSP:

    # 初始化：读取 TSP 文件、构建距离矩阵、设置超参数并生成初始种群。
    def __init__(self, filename):
        # init cities
            self.cities = self.read_tsp_file(filename)
            self.num_cities = len(self.cities)
            self.distance_matrix = self.create_distance_matrix()
        # set hyper_params
            self.pop_size = 50
            self.mutation_rate = 0.2
        # init population
            self.population = []
            for _ in range(self.pop_size):
                individual =  list(range(self.num_cities))
                random.shuffle(individual)
                self.population.append(individual)
    

    # 预计算距离矩阵，避免在适应度评估中重复做欧氏距离计算。
    def create_distance_matrix(self):
        matrix = np.zeros((self.num_cities, self.num_cities))
        for i in range(self.num_cities):
            for j in range(self.num_cities):
                dist = np.linalg.norm(self.cities[i] - self.cities[j])
                matrix[i,j] = dist
        return matrix

    # 读取 TSP 文件中的节点坐标，只保留 NODE_COORD_SECTION 之后的数据。
    def read_tsp_file(self, filename):
        cities = []
        with open(filename, 'r') as f:
            lines = f.readlines()
            is_cities = False
            for line in lines:
                line = line.strip()
                if line == "NODE_COORD_SECTION":
                    is_cities = True
                    continue
                if line == "EOF" or not line:
                    break
                if is_cities:
                    location =  line.split()
                    if len(location) < 3:
                        continue
                    cities.append([float(location[1]),float(location[2])])
        return np.array(cities)

    # 目标函数：计算一条回路的总长度，最后会回到起点。
    def objective(self, route):
        total_distance = 0
        for i in range(len(route) - 1):
            u = route[i]
            v = route[i+1]
            total_distance += self.distance_matrix[u,v]

        last_city = route[-1]
        first_city = route[0]
        total_distance += self.distance_matrix[last_city,first_city]

        return total_distance
    
    # 适应度函数：路径越短，适应度越高。
    def fitness(self, route):
        return 1.0/ self.objective(route)
    

#######################################################
#  选择：轮盘赌选择和锦标赛选择两种方法，默认使用轮盘赌选择
#######################################################
    def tournament_selection(self, k=5):
        candidates_idx = random.sample(range(self.pop_size), k)
        candidates = [self.population[i] for i in candidates_idx]
        best_candidate = max(candidates, key=self.fitness)
        return best_candidate

    def roulette_wheel_selection(self):
        fitness_scores = np.array([self.fitness(route) for route in self.population])
        probs = fitness_scores / fitness_scores.sum()
        idx = np.random.choice(len(self.population),p = probs)
        return self.population[idx]

    def selection(self):
        return self.roulette_wheel_selection()
        # return self.tournament_selection()


######################################################
#  交叉：部分映射交叉（PMX）方法，保证子代仍然是合法的路径
########################################################
    def pmx_crossover(self, p1, p2):
        size = len(p1)
        child = p2.copy()
        start, end = sorted(random.sample(range(size),2))
        slice1 = p1[start:end]
        slice2 = p2[start:end]
        child[start:end] = slice1
        for i in range(size):
            if i < start or i >= end:
                while child[i] in slice1:
                    idx = slice1.index(child[i])
                    child[i] = slice2[idx]
        return child

    def crossover(self,p1,p2):
        return self.pmx_crossover(p1,p2)
    

####################################################
#  变异：反转变异方法，随机选择路径中的一个子段进行反转
####################################################
    def inversion_mutation(self, individual):
        if random.random() < self.mutation_rate:
            start, end = sorted(random.sample(range(self.num_cities),2))
            individual[start:end] = individual[start:end][::-1]
        return individual

    def mutation(self, individual):
        return self.inversion_mutation(individual)
    

####################################################
# 迭代：循环执行选择、交叉和变异，并保留最终种群中的最优路径。
###################################################
    def iterate(self, num_iterations):
        for gen in range(num_iterations):
            fitness_scores = [self.fitness(route) for route in self.population]
            new_population = []
            while len(new_population) < self.pop_size:
                p1 = self.tournament_selection()
                p2 = self.tournament_selection()
                child = self.crossover(p1,p2)
                child = self.mutation(child)
                new_population.append(child)

            self.population = new_population

            # 每 100 代打印一次当前种群的第一条路径长度，用于观察收敛趋势。
            if (gen + 1) % 100 == 0 :
                cur_best_dist = self.objective(self.population[0])
                print(f"Iteration {gen+1} : best distance = {cur_best_dist:.2f}")
        # 返回 1-based 编号格式，便于和题目描述保持一致。
        final_fitness = [self.fitness(route) for route in self.population]
        best_route = self.population[np.argmax(final_fitness)]
        return [city+1 for city in best_route]
                
####################################################

def main():
    # 命令行参数：数据集名称默认 dj38，迭代次数默认 100000。
    parser = argparse.ArgumentParser(description="Run GA on a TSP instance")
    parser.add_argument("dataset", nargs="?", default="dj38", help="TSP dataset name without extension, default: dj38")
    parser.add_argument("iterations", nargs="?", type=int, default=100000, help="Number of GA iterations, default: 100000")
    args = parser.parse_args()

    # 数据文件与当前脚本放在同一目录下，直接按文件名拼出路径。
    base = os.path.dirname(__file__)
    tsp_path = os.path.join(base, f"{args.dataset}.tsp")
    if not os.path.exists(tsp_path):
        raise FileNotFoundError(f"TSP file not found: {tsp_path}")

    # 输出运行信息，并统计总耗时。
    print(f"Loading TSP from {tsp_path}, iterations={args.iterations}")
    ga = GeneticAlgTSP(tsp_path)
    start = time.time()
    best_route = ga.iterate(args.iterations)
    elapsed = time.time() - start

    # 将结果转回 0-based 计算距离，再打印最终结果。
    best_route0 = [r-1 for r in best_route]
    best_distance = ga.objective(best_route0)

    print(f"Best route (1-based): {best_route}")
    print(f"Best distance: {best_distance:.2f}")
    print(f"Elapsed time: {elapsed:.2f}s")


if __name__ == "__main__":
    main()