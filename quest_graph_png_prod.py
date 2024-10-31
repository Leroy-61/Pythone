import os
import json
from graphviz import Digraph

# Функция для чтения данных из JSON-файлов квестов
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
                        'quest_giver_ids': content.get('QuestGiverIDs', []),
                        'quest_turn_in_ids': content.get('QuestTurnInIDs', [])
                    }
    return data

# Функция для чтения данных из JSON-файлов Objectives
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
                        'type': content.get('ObjectiveType'),
                        'text': content.get('ObjectiveText'),
                        'position': content.get('Position'),
                        'max_distance': content.get('MaxDistance'),
                        'marker_name': content.get('MarkerName')
                    }
    return data

# Функция для чтения данных из JSON-файлов NPCs
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

# Функция для построения графа
def build_graph(quests, objectives, npcs):
    dot = Digraph(comment='Quest Graph', format='png')
    
    # Добавляем узлы для квестов
    for quest_id, quest_data in quests.items():
        label = f"{quest_data['name']}\n{quest_data['objective_text']}"
        dot.node(f"Q{quest_id}", label=label, shape='box')
    
    # Добавляем узлы для Objectives
    for objective_id, objective_data in objectives.items():
        label = f"Type: {objective_data['type']}\nText: {objective_data['text']}\nPosition: {objective_data['position']}\nMax Distance: {objective_data['max_distance']}\nMarker: {objective_data['marker_name']}"
        dot.node(f"O{objective_id}", label=label, shape='ellipse')
    
    # Добавляем узлы для NPCs
    for npc_id, npc_data in npcs.items():
        label = f"NPC: {npc_data['name']}\nFaction: {npc_data['faction']}"
        dot.node(f"N{npc_id}", label=label, shape='diamond')
    
    # Добавляем связи между квестами и следующими квестами
    for quest_id, quest_data in quests.items():
        if quest_data['follow_up_quest']:
            dot.edge(f"Q{quest_id}", f"Q{quest_data['follow_up_quest']}")
    
    # Добавляем связи между квестами и предыдущими квестами
    for quest_id, quest_data in quests.items():
        for pre_quest in quest_data['pre_quests']:
            dot.edge(f"Q{pre_quest}", f"Q{quest_id}")
    
    # Добавляем связи между квестами и их целями (Objectives)
    for quest_id, quest_data in quests.items():
        for objective in quest_data['objectives']:
            objective_id = objective.get('ID')
            if objective_id in objectives:
                dot.edge(f"Q{quest_id}", f"O{objective_id}")
    
    # Добавляем связи между квестами и NPC, которые выдают квесты
    for quest_id, quest_data in quests.items():
        for npc_id in quest_data['quest_giver_ids']:
            if npc_id in npcs:
                dot.edge(f"N{npc_id}", f"Q{quest_id}")
    
    # Добавляем связи между квестами и NPC, которым сдаются квесты
    for quest_id, quest_data in quests.items():
        for npc_id in quest_data['quest_turn_in_ids']:
            if npc_id in npcs:
                dot.edge(f"Q{quest_id}", f"N{npc_id}")
    
    return dot

# Основная функция
def main():
    quests_directory = 'C:/Users/kiril/Documents/GitHub/Areal/profiles/ExpansionMod/Quests/Quests'  # Укажите путь к директории с квестами
    objectives_directory = 'C:/Users/kiril/Documents/GitHub/Areal/profiles/ExpansionMod/Quests/Objectives'  # Укажите путь к директории с Objectives
    npcs_directory = 'C:/Users/kiril/Documents/GitHub/Areal/profiles/ExpansionMod/Quests/NPCs'  # Путь к директории с NPC
    
    quests = read_quests(quests_directory)
    objectives = read_objectives(objectives_directory)
    npcs = read_npcs(npcs_directory)
    
    graph = build_graph(quests, objectives, npcs)
    
    # Сохраняем граф в файл
    graph.render('quest_graph', view=True)

if __name__ == '__main__':
    main()