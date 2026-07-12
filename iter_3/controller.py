from ga import GeneticAlgorithm

class Controller:
    def __init__(self, n, matrix, pop_size, cross_prob, mut_prob, max_gen, elite_size=2, max_history=3):
        self.n = n
        self.matrix = matrix
        self.pop_size = pop_size
        self.cross_prob = cross_prob
        self.mut_prob = mut_prob
        self.max_gen = max_gen
        self.elite_size = elite_size
        self.max_history = max_history

        self.ga = GeneticAlgorithm(n, matrix, pop_size, cross_prob, mut_prob, elite_size)
        self.history = []
        self.plot_history = []
        self.current_index = -1
        self.global_best = None
        self.no_improvement_counter = 0
        self.stopped = False
        self._init_first_generation()

    def _init_first_generation(self):
        population = self.ga.initPopulation()
        costs, best_cost, best_sol = self.ga.evaluate(population)
        self.global_best = (best_sol, best_cost)
        mean_cost = sum(costs) / len(costs)
        state = {
            'generation': 0,
            'population': population,
            'fitness': costs,
            'best_cost': best_cost,
            'best_sol': best_sol,
            'mean_cost': mean_cost,
            'num_crossovers': 0,
            'num_mutations': 0,
            'improvement': 0.0,
            'no_improvement_counter': 0
        }
        self.history = [state]
        self.plot_history = [{'generation': 0, 'best_cost': best_cost, 'mean_cost': mean_cost, 'best_sol': best_sol}]
        self.current_index = 0
        self.no_improvement_counter = 0
        self.stopped = False

    def get_current_state(self):
        return self.history[self.current_index]

    def step_forward(self):
        if self.stopped:
            return self.get_current_state()

        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.get_current_state()

        current = self.history[-1]
        if current['generation'] >= self.max_gen:
            self.stopped = True
            return self.get_current_state()


        new_pop, new_costs, stats = self.ga.step(current['population'], current['fitness'])
        _, best_cost, best_sol = self.ga.evaluate(new_pop)

        if best_cost < self.global_best[1]:
            self.global_best = (best_sol, best_cost)
            self.no_improvement_counter = 0
        else:
            self.no_improvement_counter += 1
            if self.no_improvement_counter >= 20:
                self.stopped = True

        new_state = {
            'generation': current['generation'] + 1,
            'population': new_pop,
            'fitness': new_costs,
            'best_cost': best_cost,
            'best_sol': best_sol,
            'mean_cost': stats['mean_cost'],
            'num_crossovers': stats['num_crossovers'],
            'num_mutations': stats['num_mutations'],
            'improvement': stats['improvement'],
            'no_improvement_counter': self.no_improvement_counter
        }

        self.history.append(new_state)
        self.plot_history.append({
            'generation': new_state['generation'],
            'best_cost': best_cost,
            'mean_cost': stats['mean_cost'],
            'best_sol': best_sol
        })

        if len(self.history) > self.max_history:
            self.history.pop(0)
            if self.current_index > 0:
                self.current_index -= 1

        self.current_index = len(self.history) - 1
        return new_state

    def step_back(self):
        current = self.history[-1]
        if self.current_index > 0:
            self.current_index -= 1
            self.history = self.history[:self.current_index + 1]
            self.plot_history = self.plot_history[:current['generation']]
            self.stopped = False
            self.no_improvement_counter = self.get_current_state()['no_improvement_counter']
            return self.get_current_state()
        return None

    def reset(self):
        self._init_first_generation()
        return self.get_current_state()

    def is_stopped(self):
        return self.stopped

    def get_plot_data(self):
        return self.plot_history