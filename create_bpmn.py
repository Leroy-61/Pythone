import xml.etree.ElementTree as ET
import os

def create_bpmn_diagram(quests):
    # Создаем корневой элемент BPMN
    root = ET.Element('bpmn:definitions', {
        'xmlns:bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'xmlns:bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
        'xmlns:dc': 'http://www.omg.org/spec/DD/20100524/DC',
        'xmlns:di': 'http://www.omg.org/spec/DD/20100524/DI',
        'targetNamespace': 'http://bpmn.io/schema/bpmn'
    })

    # Создаем процесс
    process = ET.SubElement(root, 'bpmn:process', id='Process_1', isExecutable='false')

    # Добавляем стартовое событие
    start_event = ET.SubElement(process, 'bpmn:startEvent', id='StartEvent_1')

    prev_element = start_event
    for i, quest in enumerate(quests):
        # Добавляем задачу для каждого квеста
        task = ET.SubElement(process, 'bpmn:task', id=f'Task_{i+1}')
        task.set('name', quest.get('Title', f'Quest {i+1}'))

        # Соединяем с предыдущим элементом
        ET.SubElement(process, 'bpmn:sequenceFlow', id=f'Flow_{i}', sourceRef=prev_element.get('id'), targetRef=task.get('id'))

        prev_element = task

    # Добавляем конечное событие
    end_event = ET.SubElement(process, 'bpmn:endEvent', id='EndEvent_1')
    ET.SubElement(process, 'bpmn:sequenceFlow', id=f'Flow_{len(quests)}', sourceRef=prev_element.get('id'), targetRef=end_event.get('id'))

    return ET.ElementTree(root)

def save_bpmn_diagram(bpmn_tree, output_directory="output", filename="quest_flow.bpmn"):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = os.path.join(output_directory, filename)
    bpmn_tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"BPMN diagram saved to {output_file}")