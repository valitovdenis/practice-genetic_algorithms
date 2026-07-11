import random

MIN_SCALED_FITNESS = 0.5
MAX_SCALED_FITNESS = 1

class GeneticAlgorithm:
    def __init__(self, n, matrix, population_size = 50, cross_prob = 0.8, mutation_prob = 0.05, elite_size = 2):
        self.n = n
        self.matrix = matrix
        self.population_size = population_size
        self.cross_prob = cross_prob
        self.mutation_prob = mutation_prob
        self.elite_size = elite_size

    #инициализируем случайную популяцию
    def initPopulation(self):
        pop = []
        for _ in range(self.population_size):
            chromosome = list(range(self.n))
            random.shuffle(chromosome)
            pop.append(chromosome)
        return pop

    #вычисляем целевую функцию каждой хромосомы, возвращаем список значений функции, лучшее значение и лучшую хромосому
    def evaluate(self, population):
        costs = []
        for chromosome in population:
            cost = sum(self.matrix[i][chromosome[i]] for i in range(self.n))
            costs.append(cost)
        best_idx = min(range(len(costs)), key=lambda i: costs[i])
        return costs, costs[best_idx], population[best_idx]

    #масштабируем приспособленность для каждой хромосомы, возвращаем список вероятностей выбора каждой хромосомы
    def scaleFitness(self, costs):
        fitness = [1.0 / c for c in costs]
        f_min, f_max = min(fitness), max(fitness)
        if f_max == f_min:
            return [1.0 / len(costs)] * len(costs)
        scaled = [MIN_SCALED_FITNESS + (MAX_SCALED_FITNESS - MIN_SCALED_FITNESS) * (f - f_min) / (f_max - f_min) for f in fitness]
        total = sum(scaled)
        return [s / total for s in scaled]

    #выбор хромосомы рулеткой, возвращает ее индекс
    def rouletteSelect(self, probs):
        r = random.random()
        region = 0.0
        for i, p in enumerate(probs):
            region += p
            if r <= region:
                return i
        return len(probs) - 1

    #выбирает и возвращает 2 индекса родителей
    def selectParents(self, costs):
        probs = self.scaleFitness(costs)
        idx1 = self.rouletteSelect(probs)
        idx2 = self.rouletteSelect(probs)
        while idx2 == idx1:
            idx2 = self.rouletteSelect(probs)
        return idx1, idx2

    #скрещивание, возвращает двух потомков
    def orderCrossover(self, parent1, parent2):
        n = self.n
        l = random.randint(0, n - 2)
        r = random.randint(l + 1, n - 1)

        child1 = [None] * n
        child2 = [None] * n

        child1[l:r + 1] = parent1[l:r + 1]
        child2[l:r + 1] = parent2[l:r + 1]

        #заполнение оставшихся позиций
        def fillChild(child, other_parent):
            occupied = set(child[l:r + 1])
            fill_pos = (r + 1) % n
            for gene in other_parent:
                if gene not in occupied:
                    while child[fill_pos] is not None:
                        fill_pos = (fill_pos + 1) % n
                    child[fill_pos] = gene
                    fill_pos = (fill_pos + 1) % n
            return child

        child1 = fillChild(child1, parent2)
        child2 = fillChild(child2, parent1)
        return child1, child2

    #мутация, возвращает измененную хромосому
    def swapMutation(self, chromosome):
        i, j = random.sample(range(self.n), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
        return chromosome

    #шаг эволюции. возвращает список новых особей, список их стоимостей и словарь статистики
    def step(self, population, costs):
        new_population = []
        new_costs = []
        stats = {'num_crossovers': 0, 'num_mutations': 0, 'improvement': 0.0, 'mean_cost': 0.0}

        #элитизм
        sorted_indices = sorted(range(len(costs)), key=lambda i: costs[i])
        elite_indices = sorted_indices[:self.elite_size]
        for idx in elite_indices:
            new_population.append(population[idx].copy())
            new_costs.append(costs[idx])

        while len(new_population) < self.population_size:
            #выбор родителей
            parent1_idx, parent2_idx = self.selectParents(costs)
            parent1, parent2 = population[parent1_idx], population[parent2_idx]

            #скрещивание
            if random.random() < self.cross_prob:
                child1, child2 = self.orderCrossover(parent1, parent2)
                stats['num_crossovers'] += 1
            else:
                child1 = parent1.copy()
                child2 = parent2.copy()

            #мутация потомков
            if random.random() < self.mutation_prob:
                child1 = self.swapMutation(child1)
                stats['num_mutations'] += 1
            if random.random() < self.mutation_prob:
                child2 = self.swapMutation(child2)
                stats['num_mutations'] += 1

            #вычисляем стоимости потомков
            cost1 = sum(self.matrix[i][child1[i]] for i in range(self.n))
            cost2 = sum(self.matrix[i][child2[i]] for i in range(self.n))

            #добавляем потомков
            if len(new_population) < self.population_size:
                new_population.append(child1)
                new_costs.append(cost1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
                new_costs.append(cost2)

        #вычисляем процент улучшения
        old_best = min(costs)
        new_best = min(new_costs)
        if old_best != 0:
            stats['improvement'] = (old_best - new_best) / old_best * 100.0
        else:
            stats['improvement'] = 0.0

        stats['mean_cost'] = sum(new_costs) / len(new_costs)

        return new_population, new_costs, stats