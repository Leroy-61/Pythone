import os
import json
import html

# Словарь для сопоставления типов целей с их текстовыми значениями
OBJECTIVE_TYPE_MAPPING = {
    2: "TARGET",
    3: "TRAVEL",
    4: "COLLECT",
    5: "DELIVERY",
    6: "TREASUREHUNT",
    7: "AIPATROL",
    8: "AICAMP",
    9: "AIVIP",
    10: "ACTION",
    11: "CRAFTING"
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

# Извлечение описания цели из файлов в папках, соответствующих типам целей
def get_objective_description(objective_id, objective_type, objectives_data):
    # Получаем текстовое название типа цели
    objective_type_name = OBJECTIVE_TYPE_MAPPING.get(objective_type)
    if not objective_type_name:
        print(f"Неподдерживаемый тип цели: {objective_type}")
        return None, None
    
    # Проверяем, есть ли данные для данного типа цели
    objective_folder = objectives_data.get(objective_type_name)
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

# Функция для создания HTML контента
def create_quest_html(quests, npcs, objectives_data):
    html_content = "<html><head><title>Структура квестов</title></head><body>"
    html_content += "<h1>Структура квестов</h1>"
    
    if not quests or 'Quests' not in quests:
        html_content += "<p>Нет данных о квестах.</p>"
        return html_content
    
    html_content += "<ul>"

    sorted_quests = sorted(quests['Quests'].items(), key=lambda x: int(x[0]))

    for index, (quest_id, quest) in enumerate(sorted_quests, start=1):
        html_content += f"<li><h2>Квест {index} (ID: {quest_id}): {html.escape(quest.get('Title', ''))}</h2>"
        html_content += "<ul>"

        # NPC, выдающие квест
        if quest.get('QuestGiverIDs', []):
            html_content += "<li>Выдается NPC:"
            html_content += "<ul>"
            for npc_id in quest.get('QuestGiverIDs', []):
                npc = npcs.get('NPCs', {}).get(str(npc_id))
                if npc:
                    html_content += f"<li>ID - {npc_id}, \"{html.escape(npc.get('NPCName', ''))}\"</li>"
                    html_content += f"<li>Фракция NPC: {html.escape(npc.get('NPCFaction', 'Нет данных'))}</li>"
                else:
                    html_content += f"<li>NPC {npc_id}: Данные отсутствуют</li>"
            html_content += "</ul></li>"

        # Данные о квесте и связи с другими квестами
        html_content += "<li>Данные о квесте:"
        html_content += "<ul>"
        
        # Предыдущий квест
        pre_quest_ids = quest.get('PreQuestIDs', [])
        if pre_quest_ids:
            for pre_quest_id in pre_quest_ids:
                pre_quest = quests['Quests'].get(str(pre_quest_id))
                if pre_quest:
                    html_content += f"<li>Предыдущий квест: ID {pre_quest_id}, ({html.escape(pre_quest.get('Title', 'Название неизвестно'))})</li>"
                else:
                    html_content += f"<li>Предыдущий квест: ID {pre_quest_id}, (Данные отсутствуют)</li>"
        
        # Следующий квест
        follow_up_quest = quest.get('FollowUpQuest')
        if follow_up_quest:
            next_quest = quests['Quests'].get(str(follow_up_quest))
            if next_quest:
                html_content += f"<li>Следующий квест: ID {follow_up_quest}, ({html.escape(next_quest.get('Title', 'Название неизвестно'))})</li>"
            else:
                html_content += f"<li>Следующий квест: ID {follow_up_quest}, (Данные отсутствуют)</li>"

        # Обработка наград
        rewards = quest.get('Rewards', [])
        if rewards:
            reward_selection = "Выбрать что-то одно" if quest.get('NeedToSelectReward') == 1 else "Получить все"
            html_content += f"<li>Награды ({reward_selection}):"
            html_content += "<ul>"
            for reward in rewards:
                reward_text = f"{html.escape(reward['ClassName'])} - {reward['Amount']} шт."
                html_content += f"<li>{reward_text}</li>"
            html_content += "</ul></li>"

        # Обработка репутации
        html_content += "<li>Репутация:"
        html_content += "<ul>"

        # Требуемая фракция
        required_faction = quest.get('RequiredFaction')
        if required_faction:
            html_content += f"<li>Требуемая фракция: {html.escape(required_faction)}</li>"

        # Требуемое количество очков репутации (если не -1)
        reputation_requirement = quest.get('ReputationRequirement')
        if reputation_requirement is not None and reputation_requirement != -1:
            html_content += f"<li>Требуемое количество очков репутации: {reputation_requirement}</li>"

        # Присваиваемая игроку фракция
        faction_reward = quest.get('FactionReward')
        if faction_reward:
            html_content += f"<li>Присваиваемая игроку фракция: {html.escape(faction_reward)}</li>"

        # Награда очками фракций
        faction_reputation_rewards = quest.get('FactionReputationRewards', {})
        if faction_reputation_rewards:
            html_content += "<li>Награда очками фракций:"
            html_content += "<ul>"
            for faction, points in faction_reputation_rewards.items():
                if points != 0:
                    html_content += f"<li>{html.escape(faction)}: {points}</li>"
            html_content += "</ul></li>"

        html_content += "</ul></li>"  # Закрываем блок репутации

        # Цели (objectives)
        html_content += "<li>Цели:"
        html_content += "<ul>"
        for obj in quest.get('Objectives', []):
            obj_id = obj.get('ID')
            obj_type = obj.get('ObjectiveType')
            
            # Получаем тип цели и описание
            objective_type_name, objective_description = get_objective_description(obj_id, obj_type, objectives_data)
            
            if objective_type_name:
                html_content += f"<li>Цель: {objective_type_name}, ID {obj_id}"
                html_content += f"{html.escape(objective_description)}</li></ul></li>"
            else:
                html_content += f"<li>Цель {obj_id}: Неподдерживаемый тип цели ({obj_type})</li>"
                
        html_content += "</ul></li>"  # Закрываем блок целей

        html_content += "</ul></li>"  # Закрываем блок квеста

    html_content += "</ul></body></html>"  # Завершаем HTML-документ
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