import heapq
import json
import os
from datetime import datetime

class Task:
    def __init__(self, name, priority, due_date, dependencies=None):
        self.name = name
        self.priority = priority
        self.due_date = due_date  # formato 'YYYY-MM-DD'
        self.dependencies = set(dependencies) if dependencies else set()

    def __lt__(self, other):
        # Ordenar por prioridad y luego por fecha de vencimiento
        if self.priority == other.priority:
            return self.due_date < other.due_date
        return self.priority < other.priority

    def to_dict(self):
        return {
            'name': self.name,
            'priority': self.priority,
            'due_date': self.due_date,
            'dependencies': list(self.dependencies)
        }

    @staticmethod
    def from_dict(data):
        # Maneja tareas antiguas sin 'due_date'
        due_date = data.get('due_date', '2100-01-01')  # Fecha lejana por defecto
        dependencies = data.get('dependencies', [])
        return Task(data['name'], data['priority'], due_date, dependencies)

    def __repr__(self):
        return f"{self.name} (Prioridad: {self.priority}, Vence: {self.due_date})"


class TaskManager:
    def __init__(self, filename="tareas.json"):
        self.filename = filename
        self.task_dict = {}
        self.heap = []
        self.completed = set()
        self.load_tasks()

    def add_task(self, name, priority, due_date, dependencies=None):
        if not name.strip():
            print(" El nombre de la tarea no puede estar vacío.")
            return
        if not isinstance(priority, int):
            print(" La prioridad debe ser un número entero.")
            return
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print(" Fecha inválida. Usa el formato YYYY-MM-DD.")
            return

        if name in self.task_dict:
            print(f" La tarea '{name}' ya existe.")
            return

        task = Task(name, priority, due_date, dependencies)
        self.task_dict[name] = task
        if not task.dependencies:
            heapq.heappush(self.heap, task)
        self.save_tasks()
        print(f" Tarea '{name}' añadida.")

    def complete_task(self, name):
        if name not in self.task_dict:
            print(f" La tarea '{name}' no existe.")
            return

        del self.task_dict[name]
        self.completed.add(name)

        for task in self.task_dict.values():
            if name in task.dependencies:
                task.dependencies.remove(name)
                if not task.dependencies:
                    heapq.heappush(self.heap, task)
        self.save_tasks()
        print(f" Tarea '{name}' completada.")

    def show_pending_tasks(self):
        pending = [task for task in self.heap if task.name in self.task_dict]
        sorted_pending = sorted(pending)
        print(" Tareas pendientes:")
        for task in sorted_pending:
            print(f" - {task}")

    def get_next_task(self):
        while self.heap and self.heap[0].name not in self.task_dict:
            heapq.heappop(self.heap)

        if not self.heap:
            print(" No hay tareas disponibles.")
            return None

        task = self.heap[0]
        print(f" Siguiente tarea: {task}")
        return task

    def save_tasks(self):
        data = {
            'tasks': {name: task.to_dict() for name, task in self.task_dict.items()},
            'completed': list(self.completed)
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_tasks(self):
        if not os.path.exists(self.filename):
            return

        with open(self.filename, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(" Archivo de tareas corrupto. Se ignorará.")
                return

            self.task_dict = {
                name: Task.from_dict(task_data)
                for name, task_data in data.get('tasks', {}).items()
            }
            self.completed = set(data.get('completed', []))
            self.rebuild_heap()

    def rebuild_heap(self):
        self.heap = []
        for task in self.task_dict.values():
            if not task.dependencies:
                heapq.heappush(self.heap, task)


# ---------------------
# Menú interactivo
# ---------------------

def menu():
    tm = TaskManager()

    while True:
        print("\n Menú de opciones:")
        print("1. Añadir tarea")
        print("2. Mostrar tareas pendientes")
        print("3. Completar tarea")
        print("4. Obtener siguiente tarea")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre de la tarea: ").strip()
            try:
                prioridad = int(input("Prioridad (entero, menor = mayor prioridad): "))
            except ValueError:
                print(" La prioridad debe ser un número entero.")
                continue
            fecha = input("Fecha de vencimiento (YYYY-MM-DD): ").strip()
            deps = input("Dependencias (separadas por coma, dejar vacío si ninguna): ")
            deps_list = [d.strip() for d in deps.split(",") if d.strip()] if deps else []
            tm.add_task(nombre, prioridad, fecha, deps_list)
        elif opcion == "2":
            tm.show_pending_tasks()
        elif opcion == "3":
            nombre = input("Nombre de la tarea a completar: ").strip()
            tm.complete_task(nombre)
        elif opcion == "4":
            tm.get_next_task()
        elif opcion == "5":
            print(" Saliendo del gestor de tareas.")
            break
        else:
            print(" Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    menu()
