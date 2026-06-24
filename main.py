
from collections import deque

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node

    def get_all(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return elements

def quick_sort_fields(fields):
    if len(fields) <= 1:
        return fields
    pivot = fields[len(fields) // 2]
    left = [f for f in fields if f.area > pivot.area]
    middle = [f for f in fields if f.area == pivot.area]
    right = [f for f in fields if f.area < pivot.area]
    return quick_sort_fields(left) + middle + quick_sort_fields(right)

def binary_search_catalog(catalog, target_name):
    low, high = 0, len(catalog) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_name = catalog[mid][0]
        if mid_name == target_name:
            return catalog[mid]
        elif mid_name < target_name:
            low = mid + 1
        else:
            high = mid - 1
    return None

class Crop:
    def __init__(self, name, grow_days, yield_rate):
        self.name = name
        self.grow_days = grow_days
        self.yield_rate = yield_rate

class Machine:
    def __init__(self, name):
        self.name = name
        self.wear = 0 

    def work(self, warehouse, fuel_cost):
        if warehouse.take("топливо", fuel_cost) and self.wear < 100:
            self.wear += 10
            return True
        return False

class Warehouse:
    def __init__(self):
        self.storage = {"топливо": 1000, "Пшеница": 0, "Кукуруза": 0, "Ячмень": 0}

    def add(self, item, amount):
        self.storage[item] = self.storage.get(item, 0) + amount

    def take(self, item, amount):
        if self.storage.get(item, 0) >= amount:
            self.storage[item] -= amount
            return True
        return False

class Field:
    def __init__(self, field_id, area):
        self.field_id = field_id
        self.area = area
        self.status = "пусто"
        self.crop = None
        self.days_growing = 0
        self.history = LinkedList()

class AgroSimulation:
    def __init__(self):
        self.day = 1
        self.budget = 50000
        
        self.warehouse = Warehouse()
        self.fields = [Field("Поле_А", 50), Field("Поле_Б", 120), Field("Поле_В", 30)]
        self.machines = [Machine("Трактор")]
        
        self.task_queue = deque()
        self.catalog = sorted([("Кукуруза", 1000), ("Пшеница", 800), ("Ячмень", 650)])

    def show_status(self):
        print(f"\n=== ДЕНЬ {self.day} | Бюджет: {self.budget} Руб ===")
        print(f"Склад: {self.warehouse.storage}")
        print("Поля (отсортированы по площади):")
        
        sorted_fields = quick_sort_fields(self.fields)
        for f in sorted_fields:
            crop_name = f.crop.name if f.crop else 'нет'
            print(f"  [{f.field_id}] {f.area}га | Статус: {f.status} | Культура: {crop_name}")

    def add_task(self):
        print("Доступные задачи: 1-Посев, 2-Сбор")
        choice = input("Тип задача: ").strip()
        
        if choice not in ["1", "2"]:
            print("[!] Ошибка: Неверный тип задачи.")
            return

        f_id = input("ID поля: ").strip()
        field = next((f for f in self.fields if f.field_id == f_id), None)
        if not field:
            print(f"[!] Ошибка: Поле с ID '{f_id}' не найдено.")
            return
        
        if choice == "1":
            if field.status != "пусто":
                print(f"[!] Ошибка: {f_id} уже занято!")
                return
                
            crop_name = input("Название культуры для посева: ").strip().capitalize()
            if not binary_search_catalog(self.catalog, crop_name):
                print(f"[!] Ошибка: Культура '{crop_name}' отсутствует в каталоге цен.")
                return
                
            self.task_queue.append({"type": "plant", "field": f_id, "crop": crop_name})
            print(f"[-] Задача добавлена в очередь: Посеять {crop_name} на {f_id}.")
            
        elif choice == "2":
            if field.status != "созрело":
                print(f"[!] Ошибка: На {f_id} еще нет созревшего урожая для сбора.")
                return
                
            self.task_queue.append({"type": "harvest", "field": f_id})
            print(f"[-] Задача добавлена в очередь: Собрать урожай с {f_id}.")

    def process_tasks(self):
        while self.task_queue:
            task = self.task_queue.popleft()
            field = next((f for f in self.fields if f.field_id == task["field"]), None)
            
            if not field: continue
            
            if task["type"] == "plant" and field.status == "пусто":
                catalog_item = binary_search_catalog(self.catalog, task["crop"])
                cost = catalog_item[1]
                
                if self.budget >= cost and self.machines[0].work(self.warehouse, 20):
                    self.budget -= cost
                    field.crop = Crop(task["crop"], 3, 5)
                    field.status = "засеяно"
                    field.history.append(f"День {self.day}: Посев {task['crop']}")
                    print(f"[-] Успешно засеяно {task['field']}.")
                else:
                    print(f"[!] Не удалось засеять {task['field']}: не хватает денег или топлива на складе.")

            elif task["type"] == "harvest" and field.status == "созрело":
                if self.machines[0].work(self.warehouse, 30):
                    yield_amount = field.area * field.crop.yield_rate
                    self.warehouse.add(field.crop.name, yield_amount)
                    field.history.append(f"День {self.day}: Сбор {yield_amount}т {field.crop.name}")
                    field.status = "пусто"
                    field.crop = None
                    field.days_growing = 0
                    print(f"[-] Урожай собран с {task['field']}.")
                else:
                    print(f"[!] Не удалось собрать урожай с {task['field']}: недостаточно топлива на складе.")

    def next_day(self):
        self.day += 1
        for f in self.fields:
            if f.status == "засеяно":
                f.days_growing += 1
                if f.days_growing >= f.crop.grow_days:
                    f.status = "созрело"
        
        print("\n--- Запуск рабочих процессов ---")
        self.process_tasks()

    def run(self):
        while True:
            self.show_status()
            print("\nМеню: 1 - Добавить задачу, 2 - След. день, 3 - История поля, 0 - Выход")
            cmd = input("Команда: ").strip()
            
            if cmd == "1": self.add_task()
            elif cmd == "2": self.next_day()
            elif cmd == "3":
                f_id = input("ID поля: ").strip()
                field = next((f for f in self.fields if f.field_id == f_id), None)
                if field:
                    print(f"История {f_id}:", field.history.get_all())
                else:
                    print("[!] Поле не найдено.")
            elif cmd == "0": break

if __name__ == "__main__":
    game = AgroSimulation()
    game.run()
