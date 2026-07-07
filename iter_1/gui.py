import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Задача о назначениях")
        self.matrix = None
        self.params = None
        self.show_startup()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def show_startup(self):
        self.clear()
        f = ttk.Frame(self.root)
        f.pack(fill=tk.BOTH, expand=True)

        self.n_var = tk.IntVar(value=3)
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
            self.show_main()
        else:
            n = self.params['n']
            self.matrix = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
            self.show_main()

    def show_matrix_input(self):
        self.clear()
        n = self.params['n']
        f = ttk.Frame(self.root)
        f.pack()

        ttk.Label(f, text=f"Матрица {n}x{n}").pack()
        tbl = ttk.Frame(f)
        tbl.pack()

        self.entries = []
        for i in range(n):
            row_ent = []
            for j in range(n):
                e = ttk.Entry(tbl, width=4)
                e.grid(row=i, column=j, padx=1, pady=1)
                e.insert(0, "0")
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
        self.show_main()

    def setup_plot(self, parent):
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.set_xlabel("Поколение")
        self.ax.set_ylabel("Лучшая стоимость")
        self.ax.grid(True)

        self.line, = self.ax.plot([], [], 'b-', marker='o', markersize=4)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()

    def update_plot(self, generation, best_cost):
        x_data = list(self.line.get_xdata()) + [generation]
        y_data = list(self.line.get_ydata()) + [best_cost]
        self.line.set_data(x_data, y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def show_main(self):
        self.clear()
        f = ttk.Frame(self.root)
        f.pack(fill=tk.BOTH, expand=True)

        self.setup_plot(f)

        stats = tk.Text(f, height=8, width=50)
        stats.pack(fill=tk.X)
        stats.insert(tk.END, "Поколение: 0\nЛучшая стоимость: 0\nЛучшая особь: [0, 1, 2]\nЧисло скрещиваний: 0\nЧисло мутаций: 0\nУлучшение: +0.00%\nГлобальный лучший: [0,1,2] (стоимость 0)")
        stats.config(state='disabled')

        nav = ttk.Frame(f)
        nav.pack(fill=tk.X)
        ttk.Button(nav, text="<- Назад", command=lambda: messagebox.showinfo("", "Заглушка")).pack(side=tk.LEFT)
        ttk.Button(nav, text="Вперёд ->", command=lambda: messagebox.showinfo("", "Заглушка")).pack(side=tk.LEFT)
        ttk.Button(nav, text="В конец ->->", command=lambda: messagebox.showinfo("", "Заглушка")).pack(side=tk.LEFT)

        ttk.Label(f, text=f"N={self.params['n']}, популяция={self.params['pop']}, поколений={self.params['gen']}").pack()

        self.update_plot(0, 100)
        self.update_plot(1, 80)
        self.update_plot(2, 60)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    app = App(root)
    root.mainloop()