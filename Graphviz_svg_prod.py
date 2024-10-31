import json
import os
import pydot

def read_quests(directory):
    data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = json.load(file)
                quest_id = content.get('ID')
                if quest_id:
                    data[quest_id] = {
                        'filename': filename,
                        'name': content.get('Title'),
                        'follow_up_quest': content.get('FollowUpQuest'),
                        'pre_quests': content.get('PreQuestIDs', []),
                        'objective_text': content.get('ObjectiveText'),
                        'objectives': content.get('Objectives', []),
                        'repeatable': content.get('Repeatable'),
                        'is_daily_quest': content.get('IsDailyQuest'),
                        'is_weekly_quest': content.get('IsWeeklyQuest'),
                        'need_to_select_reward': content.get('NeedToSelectReward'),
                        'rewards': content.get('Rewards', []),
                        'quest_giver_ids': content.get('QuestGiverIDs', []),
                        'quest_turn_in_ids': content.get('QuestTurnInIDs', [])
                    }
    return data

def read_objectives(directory):
    data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = json.load(file)
                objective_id = content.get('ID')
                if objective_id:
                    data[objective_id] = {
                        'filename': filename,
                        'ObjectiveType': content.get('ObjectiveType'),
                        'text': content.get('ObjectiveText'),
                        'position': content.get('Position'),
                        'max_distance': content.get('MaxDistance'),
                        'marker_name': content.get('MarkerName')
                    }
    return data

def read_npcs(directory):
    data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = json.load(file)
                npc_id = content.get('ID')
                if npc_id:
                    data[npc_id] = {
                        'filename': filename,
                        'name': content.get('NPCName'),
                        'position': content.get('Position'),
                        'faction': content.get('NPCFaction')
                    }
    return data

def build_graph(quests, objectives, npcs):
    graph = pydot.Dot(graph_type='digraph', rankdir='LR', newrank='True')

    def escape_string(s):
        if s is None or s == "":
            return "НЕТ"
        return s.encode('utf-8').decode('utf-8')

    objective_types = {
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

    # Добавляем узлы для квестов
    for quest_id, quest_data in quests.items():
        label = f"ID: {quest_id}\n"
        label += f"Название: {escape_string(quest_data['name'])}\n"
        label += f"Задача: {escape_string(quest_data['objective_text'])}\n"
        label += "Тип цели: "
        
        print(f"\nDebug для квеста {quest_id}:")
        print(f"Objectives в квесте: {quest_data['objectives']}")
        
        # ЗАМЕНИТЬ ЭТОТ БЛОК КОДА:
        if quest_data['objectives']:
            objective_types_list = []
            for objective in quest_data['objectives']:
                objective_id = objective.get('ID')
                obj_type = objective.get('ObjectiveType')  # Получаем тип прямо из objective
                print(f"Проверяем objective_id: {objective_id}, тип: {obj_type}")
                
                if isinstance(obj_type, int) and obj_type in objective_types:
                    objective_types_list.append(f"{objective_types[obj_type]} ({objective_id})")
                else:
                    print(f"Проблема с типом objective: {obj_type}")
            
            label += ', '.join(objective_types_list) if objective_types_list else "НЕТ"
        else:
            label += "НЕТ"
        label += "\n"
        
        label += f"Повторяемый: {'Да' if quest_data['repeatable'] else 'Нет'}\n"
        label += f"Ежедневный: {'Да' if quest_data['is_daily_quest'] else 'Нет'}\n"
        label += f"Еженедельный: {'Да' if quest_data['is_weekly_quest'] else 'Нет'}\n"
        label += f"Выбор наград: {'Да' if quest_data['need_to_select_reward'] else 'Нет'}\n"
        label += "Награды: "
        if quest_data['rewards']:
            label += "\n"
            for reward in quest_data['rewards']:
                label += f"{escape_string(reward['ClassName'])} (x{reward['Amount']})\n"
        else:
            label += "НЕТ\n"

        node = pydot.Node(f"Q{quest_id}", 
                         label=label, 
                         shape='box',
                         fontname="Arial",
                         charset="utf-8")
        graph.add_node(node)

    # Добавляем узлы для NPCs
    for npc_id, npc_data in npcs.items():
        label = f"ID: {npc_id}\nИмя: {escape_string(npc_data['name'])}\n"
        label += f"Фракция: {escape_string(npc_data['faction'])}"
        node = pydot.Node(f"N{npc_id}", 
                         label=label, 
                         shape='diamond',
                         fontname="Arial",
                         charset="utf-8")
        graph.add_node(node)

    # Добавляем связи между квестами и NPC, которые выдают квесты
    for quest_id, quest_data in quests.items():
        for npc_id in quest_data['quest_giver_ids']:
            if npc_id in npcs:
                edge = pydot.Edge(f"N{npc_id}", f"Q{quest_id}")
                graph.add_edge(edge)

    # Добавляем связи между квестами и NPC, которым сдаются квесты
    for quest_id, quest_data in quests.items():
        for npc_id in quest_data['quest_turn_in_ids']:
            if npc_id in npcs:
                edge = pydot.Edge(f"Q{quest_id}", f"N{npc_id}")
                graph.add_edge(edge)

    # Добавляем связи между квестами и следующими квестами
    for quest_id, quest_data in quests.items():
        if quest_data['follow_up_quest'] and quest_data['follow_up_quest'] != -1:  # Добавлена проверка на -1
            edge = pydot.Edge(f"Q{quest_id}", f"Q{quest_data['follow_up_quest']}")
            graph.add_edge(edge)

    # Добавляем связи между квестами и предыдущими квестами
    for quest_id, quest_data in quests.items():
        for pre_quest in quest_data['pre_quests']:
            edge = pydot.Edge(f"Q{pre_quest}", f"Q{quest_id}")
            graph.add_edge(edge)

    return graph

def main():
    quests_directory = 'C:/Users/kiril/Documents/GitHub/Areal/profiles/ExpansionMod/Quests/Quests'
    objectives_directory = 'C:/Users/kiril/Documents/GitHub/Areal/profiles/ExpansionMod/Quests/Objectives'
    npcs_directory = 'C:/Users/kiril/Documents/GitHub/Areal/profiles/ExpansionMod/Quests/NPCs'

    try:
        quests = read_quests(quests_directory)
        objectives = read_objectives(objectives_directory)
        npcs = read_npcs(npcs_directory)

        graph = build_graph(quests, objectives, npcs)

        # Устанавливаем глобальные параметры графа
        graph.set_charset("UTF-8")
        graph.set_fontname("Arial")

        # Сохраняем в dot-файл сначала
        graph.write("quest_graph.dot", encoding='utf-8')
        
        # Используем graphviz напрямую для конвертации в SVG
        os.system('dot -Tsvg -Nfontname=Arial -Gcharset=UTF-8 quest_graph.dot -o quest_graph.svg')

        print("Диаграмма сохранена в quest_graph.svg")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()