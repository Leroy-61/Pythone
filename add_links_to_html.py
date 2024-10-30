import os
from bs4 import BeautifulSoup
import re

def add_links_and_toc(input_file, output_file):
    # Чтение исходного HTML файла
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Создание объекта BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Добавление стилей для оглавления
    style = soup.new_tag('style')
    style.string = '''
        #toc { background-color: #f8f8f8; padding: 20px; margin-bottom: 20px; }
        .quest-link { display: block; margin-bottom: 5px; }
    '''
    soup.head.append(style)

    # Создание оглавления
    toc = soup.new_tag('div', id='toc')
    toc.append(soup.new_tag('h2'))
    toc.h2.string = 'Оглавление'
    
    # Поиск всех квестов и добавление им id
    quests = soup.find_all('div', class_='quest-node')
    for i, quest in enumerate(quests, 1):
        quest_title = quest.h2.string if quest.h2 else f'Квест {i}'
        quest_id = f'quest_{i}'
        quest['id'] = quest_id

        # Добавление ссылки в оглавление
        link = soup.new_tag('a', href=f'#{quest_id}', **{'class': 'quest-link'})
        link.string = quest_title
        toc.append(link)

    # Вставка оглавления в начало body
    soup.body.insert(1, toc)

    # Добавление ссылок на предыдущие квесты
    for quest in quests:
        prev_quests = quest.find_all(string=re.compile('Предыдущий квест:'))
        for prev_quest in prev_quests:
            match = re.search(r'ID (\d+)', prev_quest)
            if match:
                prev_id = match.group(1)
                new_string = prev_quest.replace(
                    f'ID {prev_id}',
                    f'<a href="#quest_{prev_id}">ID {prev_id}</a>'
                )
                prev_quest.replace_with(BeautifulSoup(new_string, 'html.parser'))

    # Сохранение обновленного HTML
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Использование функции
input_file = 'quest_structure.html'  # Путь к исходному HTML файлу
output_file = 'quest_structure_with_links.html'  # Путь к новому HTML файлу с ссылками

add_links_and_toc(input_file, output_file)
print(f"Обновленный HTML-файл создан: {output_file}")