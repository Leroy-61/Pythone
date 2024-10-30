import os
import json
import html

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

def escape_quest_html(text):
    """Экранирование HTML-символов в тексте"""
    return html.escape(str(text)) if text else ""

def import_json_files(directory):
    data = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        json_data = json.load(file)
                        file_type = os.path.basename(root)
                        
                        if file_type not in data:
                            data[file_type] = {}
                        data[file_type][str(json_data.get('ID', ''))] = json_data
                        print(f"Успешно импортирован файл: {file_path}")
                except json.JSONDecodeError as e:
                    print(f"Ошибка при декодировании JSON в файле: {file_path} - {str(e)}")
                except IOError as e:
                    print(f"Ошибка при чтении файла: {file_path} - {str(e)}")
    return data

def get_objective_description(objective_id, objective_type, objectives_data):
    objective_type_name = OBJECTIVE_TYPE_MAPPING.get(objective_type)
    if not objective_type_name:
        print(f"Неподдерживаемый тип цели: {objective_type}")
        return None, None
    
    objective_folder = None
    for key in objectives_data.keys():
        if key.lower() == objective_type_name.lower():
            objective_folder = objectives_data[key]
            break
            
    if not objective_folder:
        print(f"Данные для типа цели '{objective_type_name}' отсутствуют.")
        return objective_type_name, 'Описание отсутствует'
        
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
            body { font-family: Arial, sans-serif; margin: 20px; }
            .quest-tree { margin-left: 20px; }
            .quest-node { border: 1px solid #ccc; margin: 10px 0; padding: 10px; background-color: #f9f9f9; }
            .quest-children { margin-left: 40px; }
            h1 { color: #333; }
            h2 { color: #666; }
            p { margin: 5px 0; }
        </style>
    </head>
    <body>
    <h1>Структура квестов</h1>
    <div class="quest-tree">
    """
    
    if not quests or 'Quests' not in quests:
        html_content += "<p>Нет данных о квестах.</p>"
        return html_content
    
    def render_quest(quest_id):
        quest = quests['Quests'].get(str(quest_id))
        if not quest:
            return f"<p>Квест с ID {quest_id} не найден</p>"
        
        quest_html = '<div class="quest-node">'
        quest_html += f'<h2>Квест {quest_id}: {escape_quest_html(quest.get("Title", ""))}</h2>'
        
        # NPC, выдающие квест
        if quest.get('QuestGiverIDs'):
            quest_html += "<p>Выдается NPC:"
            for npc_id in quest['QuestGiverIDs']:
                npc = npcs.get('NPCs', {}).get(str(npc_id))
                if npc:
                    quest_html += f"<br>ID - {npc_id}, \"{escape_quest_html(npc.get('NPCName', ''))}\""
                    quest_html += f"<br>Фракция NPC: {escape_quest_html(npc.get('NPCFaction', 'Нет данных'))}"
                else:
                    quest_html += f"<br>NPC {npc_id}: Данные отсутствуют"
            quest_html += "</p>"

        # Данные о квесте
        quest_html += "<p>Данные о квесте:"
        
        # Предыдущий квест
        pre_quest_ids = quest.get('PreQuestIDs', [])
        if pre_quest_ids:
            for pre_quest_id in pre_quest_ids:
                pre_quest = quests['Quests'].get(str(pre_quest_id))
                if pre_quest:
                    quest_html += f"<br>Предыдущий квест: ID {pre_quest_id}, ({escape_quest_html(pre_quest.get('Title', 'Название неизвестно'))})"
                else:
                    quest_html += f"<br>Предыдущий квест: ID {pre_quest_id}, (Данные отсутствуют)"
        quest_html += "</p>"
        
        # Награды
        rewards = quest.get('Rewards', [])
        if rewards:
            reward_selection = "Выбрать что-то одно" if quest.get('NeedToSelectReward') == 1 else "Получить все"
            quest_html += f"<p>Награды ({reward_selection}):"
            for reward in rewards:
                reward_text = f"{escape_quest_html(reward.get('ClassName', ''))} - {reward.get('Amount', '')} шт."
                quest_html += f"<br>{reward_text}"
            quest_html += "</p>"

        # Репутация
        quest_html += "<p>Репутация:"
        required_faction = quest.get('RequiredFaction')
        if required_faction:
            quest_html += f"<br>Требуемая фракция: {escape_quest_html(required_faction)}"
        
        reputation_requirement = quest.get('ReputationRequirement')
        if reputation_requirement is not None and reputation_requirement != -1:
            quest_html += f"<br>Требуемое количество очков репутации: {reputation_requirement}"
        
        faction_reward = quest.get('FactionReward')
        if faction_reward:
            quest_html += f"<br>Присваиваемая игроку фракция: {escape_quest_html(faction_reward)}"
        
        faction_reputation_rewards = quest.get('FactionReputationRewards', {})
        if faction_reputation_rewards:
            quest_html += "<br>Награда очками фракций:"
            for faction, points in faction_reputation_rewards.items():
                 if points != 0:
                    quest_html += f"<br>{escape_quest_html(faction)}: {points}"
        quest_html += "</p>"

        # Цели (objectives)
        quest_html += "<p>Цели:"
        for obj in quest.get('Objectives', []):
            obj_id = obj.get('ID')
            obj_type = obj.get('ObjectiveType')
            
            # Получаем тип цели и описание
            objective_type_name, objective_description = get_objective_description(obj_id, obj_type, objectives_data)
            
            if objective_type_name:
                quest_html += f"<br><strong>Цель:</strong> {objective_type_name} (ID: {obj_id})<br>"
                quest_html += f"<strong>Описание цели:</strong> {escape_quest_html(objective_description)}"
            else:
                quest_html += f"<br>Цель {obj_id}: Неподдерживаемый тип цели ({obj_type})"
        quest_html += "</p>"
        
        # Рекурсивно отображаем следующий квест
        follow_up_quest = quest.get('FollowUpQuest')
        if follow_up_quest:
            quest_html += '<div class="quest-children">'
            quest_html += render_quest(follow_up_quest)
            quest_html += '</div>'
        
        quest_html += '</div>'  # Закрываем div.quest-node
        return quest_html
    
    # Находим квесты без предшественников (корневые квесты)
    root_quests = [qid for qid, q in quests['Quests'].items() if not q.get('PreQuestIDs')]
    html_content += f"<p>Найдено корневых квестов: {len(root_quests)}</p>"
    
    if not root_quests:
        # Если корневых квестов нет, выводим все квесты
        html_content += "<p>Корневые квесты не найдены. Отображаем все квесты:</p>"
        for quest_id in quests['Quests']:
            html_content += render_quest(quest_id)
    else:
        for root_quest_id in root_quests:
            html_content += render_quest(root_quest_id)
    
    html_content += "</div></body></html>"
    return html_content

def main():
    base_path = r'F:\Modding\Areal\profiles\ExpansionMod\Quests'  # Измените путь на ваш

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

    output_file = 'quest_structure.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML-файл со структурой квестов создан: {output_file}")

if __name__ == "__main__":
    main()