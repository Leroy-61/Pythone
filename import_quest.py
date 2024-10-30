import json
import os
import html
import json
import os
import html

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
                        if 'ID' not in json_data:
                            print(f"Предупреждение: файл {filename} не содержит поля 'ID'")
                            continue
                        if file_type not in data:
                            data[file_type] = {}
                        data[file_type][str(json_data['ID'])] = json_data
                        print(f"Успешно импортирован файл: {filename}")
                except json.JSONDecodeError:
                    print(f"Ошибка при декодировании JSON в файле: {filename}")
                except IOError:
                    print(f"Ошибка при чтении файла: {filename}")
    return data

def create_quest_html(quests, npcs, objectives):
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
        
        # Данные о квесте
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
        
        # Тип квеста
        if quest.get('Repeatable') == 1:
            html_content += "<li>Повторяемый квест: да</li>"
        elif quest.get('IsDailyQuest') == 1:
            html_content += "<li>Ежедневный квест: да</li>"
        elif quest.get('IsWeeklyQuest') == 1:
            html_content += "<li>Еженедельный квест: да</li>"
        
       # Награды
        rewards = quest.get('Rewards', [])
        if rewards:
            reward_selection = "Выбрать что-то одно" if quest.get('NeedToSelectReward') == 1 else "Получить все"
            html_content += f"<li>Награды ({reward_selection}):"
            html_content += "<ul>"
            for reward in rewards:
                reward_text = f"{reward['ClassName']} - {reward['Amount']} шт."
                
                additional_info = []
                if reward.get('Attachments'):
                    additional_info.append(f"Attachments: {reward['Attachments']}")
                if reward.get('DamagePercent'):
                    additional_info.append(f"Damage: {reward['DamagePercent']}%")
                if reward.get('HealthPercent'):
                    additional_info.append(f"Health: {reward['HealthPercent']}%")
                if reward.get('QuestID', -1) != -1:
                    additional_info.append(f"QuestID: {reward['QuestID']}")
                if reward.get('Chance', 1.0) != 1.0:
                    additional_info.append(f"Chance: {reward['Chance']}")
                
                if additional_info:
                    reward_text += f" ({', '.join(additional_info)})"
                
                html_content += f"<li>{reward_text}</li>"
            html_content += "</ul>"
            html_content += "</li>"
            html_content += "</li>"
        
        # Репутация
        html_content += "<li>Репутация:"
        html_content += "<ul>"
        
        # Требуемая фракция
        required_faction = quest.get('RequiredFaction')
        if required_faction:
            html_content += f"<li>Требуемая фракция: {html.escape(required_faction)}</li>"
        
        # Требуемое количество очков репутации
        reputation_requirement = quest.get('ReputationRequirement')
        if reputation_requirement and reputation_requirement != 0:
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
            html_content += "</ul>"
            html_content += "</li>"
        
        html_content += "</ul>"
        html_content += "</li>"
        
        # Цели (objectives)
        html_content += "<li>Цели:"
        html_content += "<ul>"
        for obj in quest.get('Objectives', []):
            obj_id = obj.get('ID')
            obj_type = obj.get('ObjectiveType')
            objective = objectives.get(str(obj_type), {}).get(str(obj_id))
            if objective:
                html_content += f"<li>Цель: {html.escape(objective.get('ObjectiveText', f'Objective {obj_id}'))}"
                html_content += "<ul>"
                html_content += f"<li>Тип: {obj_type}</li>"
                html_content += f"<li>Позиция: {objective.get('Position', 'Нет данных')}</li>"
                html_content += f"<li>Ограничение по времени: {objective.get('TimeLimit', 'Нет данных')}</li>"
                html_content += "</ul></li>"
            else:
                html_content += f"<li>Цель {obj_id}: Данные отсутствуют</li>"
        html_content += "</ul></li>"

        html_content += "</ul></li>"

    html_content += "</ul></body></html>"
    return html_content

def main():
    base_path = r'C:\Users\kiril\Documents\GitHub\Areal\profiles\ExpansionMod\Quests'

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

    html_content = create_quest_html(quests, npcs, objectives)

    with open('quest_structure.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("HTML-файл со структурой квестов создан: quest_structure.html")

if __name__ == "__main__":
    main()

def main():
    base_path = r'C:\Users\kiril\Documents\GitHub\Areal\profiles\ExpansionMod\Quests'

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

    html_content = create_quest_html(quests, npcs, objectives)

    with open('quest_structure.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("HTML-файл со структурой квестов создан: quest_structure.html")

if __name__ == "__main__":
    main()