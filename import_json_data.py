import json
import os
from typing import List, Dict

def import_json_files(directory: str) -> List[Dict]:
    """
    Импортирует данные из всех JSON файлов в указанной директории.
    
    :param directory: Путь к директории с JSON файлами
    :return: Список словарей с данными из JSON файлов
    """
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                    data.append(json_data)
                print(f"Успешно импортирован файл: {filename}")
            except json.JSONDecodeError:
                print(f"Ошибка при декодировании JSON в файле: {filename}")
            except IOError:
                print(f"Ошибка при чтении файла: {filename}")
    return data

def main():
    # Укажите путь к директории с JSON файлами
    json_directory = 'C:/Users/kiril/Documents/GitHub/Areal/profiles/ExpansionMod/Quests/NPCs'
    
    # Импорт данных
    imported_data = import_json_files(json_directory)
    
    # Вывод результатов
    print(f"\nВсего импортировано файлов: {len(imported_data)}")
    print("Пример данных из первого файла:")
    print(json.dumps(imported_data[0], indent=2, ensure_ascii=False) if imported_data else "Нет данных")

if __name__ == "__main__":
    main()