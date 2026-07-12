import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from controller import Controller

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Задача о назначениях")
        self.matrix = None
        self.params = None
        self.controller = None
        self.cell_widgets = []
        self.tree = None
        self.show_startup()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def show_startup(self):
        self.clear()
        f = ttk.Frame(self.root)
        f.pack(fill=tk.BOTH, expand=True)

        self.n_var = tk.IntVar(value=6)
        self.pop_var = tk.IntVar(value=50)
        self.gen_var = tk.IntVar(value=100)
        self.cross_var = tk.DoubleVar(value=0.8)
        self.mut_var = tk.DoubleVar(value=0.05)
        self.method_var = tk.StringVar(value="manual")

        row = 0
        ttk.Label(f, text="N:").grid(row=row, column=0)
        ttk.Spinbox(f, from_=2, to=100, textvariable=self.n_var, width=5).grid(row=row, column=1)
        row += 1

        ttk.Label(f, text="Размер популяции:").grid(row=row, column=0)
        ttk.Spinbox(f, from_=10, to=300, textvariable=self.pop_var, width=5).grid(row=row, column=1)
        row += 1

        ttk.Label(f, text="Макс. поколений:").grid(row=row, column=0)
        ttk.Spinbox(f, from_=10, to=500, textvariable=self.gen_var, width=5).grid(row=row, column=1)
        row += 1

        ttk.Label(f, text="Вер. скрещивания:").grid(row=row, column=0)
        ttk.Spinbox(f, from_=0.1, to=1.0, increment=0.05, textvariable=self.cross_var, width=5).grid(row=row, column=1)
        row += 1

        ttk.Label(f, text="Вер. мутации:").grid(row=row, column=0)
        ttk.Spinbox(f, from_=0.01, to=0.5, increment=0.01, textvariable=self.mut_var, width=5).grid(row=row, column=1)
        row += 1

        ttk.Label(f, text="Способ ввода:").grid(row=row, column=0)
        mf = ttk.Frame(f)
        mf.grid(row=row, column=1)
        ttk.Radiobutton(mf, text="Ручной", variable=self.method_var, value="manual").pack(side=tk.LEFT)
        ttk.Radiobutton(mf, text="Файл", variable=self.method_var, value="file").pack(side=tk.LEFT)
        ttk.Radiobutton(mf, text="Случайный", variable=self.method_var, value="random").pack(side=tk.LEFT)
        row += 1

        ttk.Button(f, text="Начать", command=self.start).grid(row=row, column=0, columnspan=2, pady=10)

    def start(self):
        self.params = {
            'n': self.n_var.get(),
            'pop': self.pop_var.get(),
            'gen': self.gen_var.get(),
            'cross': self.cross_var.get(),
            'mut': self.mut_var.get(),
            'method': self.method_var.get()
        }
        if self.params['method'] == 'manual':
            self.show_matrix_input()
        elif self.params['method'] == 'file':
            with open("matrix.txt", "r") as f:
                self.matrix = []
                for line in f:
                    row = list(map(int, line.split()))
                    self.matrix.append(row)
            self.init_controller_and_show_main()
        else:
            n = self.params['n']
            self.matrix = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
            self.init_controller_and_show_main()

    def init_controller_and_show_main(self):
        n = self.params['n']
        pop = self.params['pop']
        gen = self.params['gen']
        cross = self.params['cross']
        mut = self.params['mut']
        self.controller = Controller(n, self.matrix, pop, cross, mut, gen, max_history=3)
        self.show_main()

    def show_matrix_input(self):
        self.clear()
        n = self.params['n']
        f = ttk.Frame(self.root)
        f.pack()

        ttk.Label(f, text=f"Матрица {n}x{n}").pack()
        ttk.Label(f, text="Задачи").pack()
        matrix_row = ttk.Frame(f)
        matrix_row.pack()
        worker_label = ttk.Label(matrix_row, text="Р\nа\nб\nо\nт\nн\nи\nк\nи")
        worker_label.pack(side=tk.LEFT, padx=(0, 10))

        table_frame = ttk.Frame(matrix_row)
        table_frame.pack(side=tk.LEFT)

        tk.Label(table_frame, width=4, height=1, relief='ridge', bg='lightgray').grid(row=0, column=0, padx=1, pady=1)

        for j in range(n):
            lbl = tk.Label(table_frame, text=str(j), width=4, height=1, relief='ridge', bg='lightgray')
            lbl.grid(row=0, column=j + 1, padx=1, pady=1)

        for i in range(n):
            lbl = tk.Label(table_frame, text=str(i), width=4, height=1, relief='ridge', bg='lightgray')
            lbl.grid(row=i + 1, column=0, padx=1, pady=1)

        self.entries = []
        for i in range(n):
            row_ent = []
            for j in range(n):
                e = ttk.Entry(table_frame, width=4)
                e.grid(row=i+1, column=j+1, padx=1, pady=1)
                e.insert(0, "1")
                row_ent.append(e)
            self.entries.append(row_ent)

        bf = ttk.Frame(f)
        bf.pack()
        ttk.Button(bf, text="OK", command=self.confirm_matrix).pack(side=tk.LEFT)
        ttk.Button(bf, text="Назад", command=self.show_startup).pack(side=tk.LEFT)

    def confirm_matrix(self):
        n = self.params['n']
        mat = []
        try:
            for i in range(n):
                row = [int(self.entries[i][j].get()) for j in range(n)]
                mat.append(row)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целые числа")
            return
        self.matrix = mat
        self.init_controller_and_show_main()

    def setup_plot(self, parent):
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.set_xlabel("Поколение")
        self.ax.set_ylabel("Стоимость")
        self.ax.grid(True)
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        self.line_best, = self.ax.plot([], [], 'b-', marker='o', markersize=4, label='Лучшая', picker = True)
        self.line_mean, = self.ax.plot([], [], 'r--', marker='s', markersize=3, label='Средняя')
        self.ax.legend()
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()
        self.fig.canvas.mpl_connect('pick_event', self.on_dot)

    def on_dot(self, event):
        if event.artist != self.line_best:
            return
        ind = event.ind[0]
        plot_data = self.controller.get_plot_data()
        if ind >= len(plot_data):
            return
        point_data = plot_data[ind]
        generation = point_data['generation']
        best_cost = point_data['best_cost']
        best_sol = point_data['best_sol']
        msg = f"Поколение {generation}\n"
        msg += f"Лучшая стоимость: {best_cost}\n"
        msg += f"Лучшая особь: {best_sol}"
        messagebox.showinfo("Информация о поколении", msg)

    def redraw_plot(self):
        plot_data = self.controller.get_plot_data()
        if not plot_data:
            self.line_best.set_data([], [])
            self.line_mean.set_data([], [])
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
            return

        generations = [p['generation'] for p in plot_data]
        best_costs = [p['best_cost'] for p in plot_data]
        mean_costs = [p['mean_cost'] for p in plot_data]

        self.line_best.set_data(generations, best_costs)
        self.line_mean.set_data(generations, mean_costs)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()


    def update_stats(self, state):
        global_best_ind, global_best_cost = self.controller.global_best
        text = f"Поколение: {state['generation']}\n"
        text += f"Лучшая стоимость: {state['best_cost']}\n"
        text += f"Средняя стоимость: {state['mean_cost']:.2f}\n"
        text += f"Лучшая особь: {state['best_sol']}\n"
        text += f"Число скрещиваний: {state['num_crossovers']}\n"
        text += f"Число мутаций: {state['num_mutations']}\n"
        text += f"Улучшение: {state['improvement']:+.2f}%\n"
        text += f"Глобальный лучший: {global_best_ind} (стоимость {global_best_cost})"
        if self.controller.is_stopped():
            text += "\n[Алгоритм остановлен: нет улучшения за 20 шагов]"
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state='disabled')

    def update_nav_buttons(self):
        idx = self.controller.current_index
        total = len(self.controller.history)
        stopped = self.controller.is_stopped()
        max_reached = self.controller.history[-1]['generation'] >= self.controller.max_gen

        self.btn_back.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)

        if stopped or max_reached:
            self.btn_forward.config(state=tk.DISABLED)
            self.btn_end.config(state=tk.DISABLED)
        else:
            if idx < total - 1:
                self.btn_forward.config(state=tk.NORMAL)
                self.btn_end.config(state=tk.NORMAL)
            else:
                self.btn_forward.config(state=tk.NORMAL)
                self.btn_end.config(state=tk.NORMAL)

    def update_table(self, state):
        if self.tree is None:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        population = state['population']
        costs = state['fitness']
        items = [(i, population[i], costs[i]) for i in range(len(population))]

        items.sort(key=lambda x: x[2])
        for orig_idx, chrom, cost in items:
            chrom_str = str(chrom)
            self.tree.insert('', tk.END, values=(orig_idx, chrom_str, f"{cost:.2f}"))

    def update_display(self):
        state = self.controller.get_current_state()
        self.redraw_plot()
        self.update_stats(state)
        self.update_nav_buttons()
        self.highlight_solution(state['best_sol'])
        self.update_table(state)

        text = self._format_solution_text(state['best_sol'], state['best_cost'], "Глобальное лучшее")
        self.solution_display.config(state='normal')
        self.solution_display.delete(1.0, tk.END)
        self.solution_display.insert(tk.END, text)
        self.solution_display.config(state='disabled')

    def highlight_solution(self, permutation):
        n = len(self.matrix)
        for i in range(n):
            for j in range(n):
                self.cell_widgets[i][j].config(bg='white')
        for i, j in enumerate(permutation):
            self.cell_widgets[i][j].config(bg='lightgreen')

    def show_solution(self):
        try:
            idx = int(self.solution_index_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число")
            return

        current_state = self.controller.get_current_state()
        population = current_state['population']
        costs = current_state['fitness']
        if idx < 0 or idx >= len(population):
            messagebox.showerror("Ошибка", f"Номер должен быть от 0 до {len(population) - 1}")
            return

        perm = population[idx]
        cost = costs[idx]
        self.highlight_solution(perm)

        text = self._format_solution_text(perm, cost, f"Решение №{idx}")
        self.solution_display.config(state='normal')
        self.solution_display.delete(1.0, tk.END)
        self.solution_display.insert(tk.END, text)
        self.solution_display.config(state='disabled')

    def _format_solution_text(self, permutation, cost, label="Решение"):
        n = len(self.matrix)
        workers = ' '.join(str(i) for i in range(n))
        tasks = ' '.join(str(j) for j in permutation)
        return f"{label} (стоимость = {cost})\nРаботники: {workers}\nЗадачи:    {tasks}"

    def show_main(self):
        self.clear()
        if self.controller is None:
            return

        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main_panel)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.setup_plot(left)

        self.stats_text = tk.Text(left, height=8, width=50)
        self.stats_text.pack(fill=tk.X)
        self.stats_text.config(state='disabled')

        nav = ttk.Frame(left)
        nav.pack(fill=tk.X)
        self.btn_back = ttk.Button(nav, text="<- Назад", command=self.on_back)
        self.btn_back.pack(side=tk.LEFT)
        self.btn_forward = ttk.Button(nav, text="Вперёд ->", command=self.on_forward)
        self.btn_forward.pack(side=tk.LEFT)
        self.btn_end = ttk.Button(nav, text="В конец ->->", command=self.on_end)
        self.btn_end.pack(side=tk.LEFT)
        ttk.Button(nav, text="Сброс", command=self.on_reset).pack(side=tk.LEFT)
        ttk.Button(nav, text="Новый запуск", command=self.on_restart).pack(side=tk.LEFT)

        ttk.Label(left, text=f"N={self.params['n']}, популяция={self.params['pop']}, поколений={self.params['gen']}").pack()

        right = ttk.Frame(main_panel)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)


        ttk.Label(right, text="Матрица стоимостей", font=('Arial', 10, 'bold')).pack()
        ttk.Label(right, text="Задачи", font=('Arial', 10, 'bold')).pack()
        matrix_row = ttk.Frame(right)
        matrix_row.pack()
        worker_label = tk.Label(matrix_row, text="Р\nа\nб\nо\nт\nн\nи\nк\nи", font=('Arial', 10, 'bold'))
        worker_label.pack(side=tk.LEFT, padx=(0, 10))

        table_frame = ttk.Frame(matrix_row)
        table_frame.pack(side=tk.LEFT)

        n = len(self.matrix)
        tk.Label(table_frame, width=5, height=1, relief='ridge', bg='lightgray').grid(row=0, column=0, padx=1, pady=1)
        for j in range(n):
            lbl = tk.Label(table_frame, text=str(j), width=5, height=1, relief='ridge', bg='lightgray')
            lbl.grid(row=0, column=j + 1, padx=1, pady=1)
        for i in range(n):
            lbl = tk.Label(table_frame, text=str(i), width=5, height=1, relief='ridge', bg='lightgray')
            lbl.grid(row=i + 1, column=0, padx=1, pady=1)

        self.cell_widgets = []
        for i in range(n):
            row_cells = []
            for j in range(n):
                lbl = tk.Label(table_frame, text=str(self.matrix[i][j]),
                               width=5, height=1, relief='ridge', bg='white')
                lbl.grid(row=i+1, column=j+1, padx=1, pady=1)
                row_cells.append(lbl)
            self.cell_widgets.append(row_cells)

        control_frame = ttk.Frame(right)
        control_frame.pack(pady=5)
        ttk.Label(control_frame, text="Номер решения:").pack(side=tk.LEFT)
        self.solution_index_var = tk.StringVar(value="0")
        entry = ttk.Entry(control_frame, textvariable=self.solution_index_var, width=5)
        entry.pack(side=tk.LEFT, padx=5)
        btn = ttk.Button(control_frame, text="Показать", command=self.show_solution)
        btn.pack(side=tk.LEFT)

        self.solution_display = tk.Text(right, height=4, width=30, state='disabled')
        self.solution_display.pack(pady=5, fill=tk.X)

        table_label = ttk.Label(right, text="Все решения поколения (сортировка по стоимости)", font=('Arial', 10, 'bold'))
        table_label.pack(pady=5)

        tree_frame = ttk.Frame(right)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ('#', 'Решение', 'Стоимость')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        self.tree.heading('#', text='№ в поп.')
        self.tree.heading('Решение', text='Решение (массив)')
        self.tree.heading('Стоимость', text='Стоимость')

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.update_display()

    def on_forward(self):
        self.controller.step_forward()
        self.update_display()

    def on_back(self):
        self.controller.step_back()
        self.update_display()

    def on_end(self):
        current_state = self.controller.get_current_state()
        while current_state['generation'] < self.params['gen'] and not self.controller.is_stopped():
            self.controller.step_forward()
            current_state = self.controller.get_current_state()
            self.update_display()

    def on_reset(self):
        self.controller.reset()
        self.redraw_plot()
        self.update_display()

    def on_restart(self):
        self.controller = None
        self.matrix = None
        self.params = None
        self.cell_widgets = []
        self.tree = None
        self.clear()
        self.show_startup()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x700")
    app = App(root)
    root.mainloop()