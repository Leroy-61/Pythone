import os
import json
import html

# Словарь для сопоставления типов целей с их текстовыми значениями
# Словарь для сопоставления типов целей с их текстовыми значениями
OBJECTIVE_TYPE_MAPPING = {
    2: "Target",
    3: "Travel",
    4: "Collection",
    5: "Delivery",
    6: "TreasureHunt",
    7: "AIPatrol",
    8: "AICamp",
    9: "AIVIP",
    10: "Action",
    11: "Crafting"
}

# Функция для чтения JSON файлов из директории
def import_json_files(directory):
    data = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        json_data = json.load(file)
                        # Определяем тип цели на основе имени папки
                        file_type = os.path.basename(root)
                        
                        # Проверяем наличие ID и ObjectiveText
                        if 'ID' not in json_data or 'ObjectiveText' not in json_data:
                            print(f"Предупреждение: файл {filename} не содержит нужных полей ('ID' или 'ObjectiveText')")
                            continue
                        
                        if file_type not in data:
                            data[file_type] = {}
                        # Добавляем данные по цели с указанным ID
                        data[file_type][str(json_data['ID'])] = json_data
                        print(f"Успешно импортирован файл: {file_path}")
                except json.JSONDecodeError as e:
                    print(f"Ошибка при декодировании JSON в файле: {file_path} - {str(e)}")
                except IOError as e:
                    print(f"Ошибка при чтении файла: {file_path} - {str(e)}")
    return data

def get_objective_description(objective_id, objective_type, objectives_data):
    # Получаем текстовое название типа цели
    objective_type_name = OBJECTIVE_TYPE_MAPPING.get(objective_type)
    if not objective_type_name:
        print(f"Неподдерживаемый тип цели: {objective_type}")
        return None, None
    
    # Приводим названия к одному регистру для сопоставления
    objective_folder = None
    for key in objectives_data.keys():
        if key.lower() == objective_type_name.lower():
            objective_folder = objectives_data[key]
            break
    
    if not objective_folder:
        print(f"Данные для типа цели '{objective_type_name}' отсутствуют.")
        return objective_type_name, 'Описание отсутствует'
    
    # Получаем описание цели по ID
    objective = objective_folder.get(str(objective_id))
    if objective:
        description = objective.get('ObjectiveText', 'Описание отсутствует')
        return objective_type_name, description
    else:
        print(f"Цель с ID {objective_id} для типа '{objective_type_name}' не найдена.")
        return objective_type_name, 'Описание отсутствует'

def create_quest_html(quests, npcs, objectives_data):
    html_content = """
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>Структура квестов</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .quest {
                border: 1px solid #ccc;
                padding: 10px;
                margin-bottom: 10px;
            }
            .quest h2 {
                margin-top: 0;
            }
        </style>
    </head>
    <body>
    """

    if not quests or 'Quests' not in quests:
        html_content += "<p>Нет данных о квестах.</p>"
        return html_content

    for index, (quest_id, quest) in enumerate(sorted(quests['Quests'].items()), start=1):
        html_content += f"<div class='quest'>"
        html_content += f"<h2>Квест {index} (ID: {quest_id}): {html.escape(quest.get('Title', ''))}</h2>"

        # NPC, выдающие квест
        if quest.get('QuestGiverIDs', []):
            html_content += "<p>Выдается NPC: "
            for npc_id in quest.get('QuestGiverIDs', []):
                npc = npcs.get('NPCs', {}).get(str(npc_id))
                if npc:
                    html_content += f"{html.escape(npc.get('NPCName', ''))}, "
                else:
                    html_content += f"NPC {npc_id}, "
            html_content += "</p>"

        # Данные о квесте и связи с другими квестами
        html_content += "<p>Данные о квесте: "
        if quest.get('PreQuestIDs', []):
            html_content += "Предыдущий квест: "
            for pre_quest_id in quest.get('PreQuestIDs', []):
                pre_quest = quests['Quests'].get(str(pre_quest_id))
                if pre_quest:
                    html_content += f"{html.escape(pre_quest.get('Title', ''))}, "
                else:
                    html_content += f"Квест {pre_quest_id}, "
        if quest.get('FollowUpQuest'):
            next_quest = quests['Quests'].get(str(quest.get('FollowUpQuest')))
            if next_quest:
                html_content += f"Следующий квест: {html.escape(next_quest.get('Title', ''))}"
            else:
                html_content += f"Следующий квест: Квест {quest.get('FollowUpQuest')}"
        html_content += "</p>"

        # Обработка наград
        if quest.get('Rewards', []):
            html_content += "<p>Награды: "
            for reward in quest.get('Rewards', []):
                html_content += f"{html.escape(reward['ClassName'])} - {reward['Amount']} шт., "
            html_content += "</p>"

        # Обработка репутации
        if quest.get('ReputationRequirement') is not None and quest.get('ReputationRequirement') != -1:
            html_content += f"<p>Требуемое количество очков репутации: {quest.get('ReputationRequirement')}</p>"

        # Цели (objectives)
        if quest.get('Objectives', []):
            html_content += "<p>Цели: "
            for obj in quest.get('Objectives', []):
                obj_id = obj.get('ID')
                obj_type = obj.get('ObjectiveType')
                objective_type_name, objective_description = get_objective_description(obj_id, obj_type, objectives_data)
                if objective_type_name:
                    html_content += f"{objective_type_name} (ID: {obj_id}) - {html.escape(objective_description)}, "
                else:
                    html_content += f"Цель {obj_id} - Неподдерживаемый тип цели ({obj_type}), "
            html_content += "</p>"

        html_content += "</div>"

    html_content += "</body></html>"
    return html_content
def main():
    base_path = r'F:\Modding\Areal\profiles\ExpansionMod\Quests'

    print("Импорт данных квестов...")
    quests = import_json_files(os.path.join(base_path, 'Quests'))
    print(f"Импортировано квестов: {len(quests.get('Quests', {}))}")

    print("Импорт данных NPC...")
    npcs = import_json_files(os.path.join(base_path, 'NPCs'))
    print(f"Импортировано NPC: {len(npcs.get('NPCs', {}))}")

    print("Импорт данных целей...")
    objectives = import_json_files(os.path.join(base_path, 'Objectives'))
    print(f"Импортировано типов целей: {len(objectives)}")
    for obj_type, objs in objectives.items():
        print(f"  - {obj_type}: {len(objs)} целей")

    # Генерация HTML-файла
    html_content = create_quest_html(quests, npcs, objectives)

    with open('quest_structure.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("HTML-файл со структурой квестов создан: quest_structure.html")

if __name__ == "__main__":
    main()