import os
from bs4 import BeautifulSoup
import re

def enhance_quest_html(input_file, output_file):
    # Читаем существующий HTML файл
    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Добавляем CSS стили
    style = soup.new_tag('style')
    style.string = """
        .contents { 
            background: #f0f0f0;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .back-to-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #666;
            color: white;
            padding: 10px;
            text-decoration: none;
            border-radius: 5px;
        }
        .quest-link {
            color: #0066cc;
            text-decoration: none;
        }
        .quest-link:hover {
            text-decoration: underline;
        }
        #search-box {
            padding: 10px;
            margin: 20px 0;
            width: 300px;
        }
        .highlight {
            background-color: yellow;
        }
    """
    soup.head.append(style)

    # Создаем оглавление
    contents = soup.new_tag('div', id='contents', **{'class': 'contents'})
    contents.append(soup.new_tag('h2'))
    contents.h2.string = 'Оглавление'

    # Собираем все квесты
    quests = {}
    for quest_node in soup.find_all('div', class_='quest-node'):
        quest_title = quest_node.h2.string
        if quest_title:
            # Извлекаем ID квеста из заголовка
            quest_id = re.search(r'Квест (\d+):', quest_title)
            if quest_id:
                quest_id = quest_id.group(1)
                # Создаем якорь для квеста
                quest_node['id'] = f'quest_{quest_id}'
                quests[quest_id] = quest_title

    # Добавляем ссылки в оглавление
    for quest_id, title in sorted(quests.items(), key=lambda x: int(x[0])):
        link = soup.new_tag('a', href=f'#quest_{quest_id}', **{'class': 'quest-link'})
        link.string = title
        p = soup.new_tag('p')
        p.append(link)
        contents.append(p)

    # Добавляем поиск
    search_script = soup.new_tag('script')
    search_script.string = """
        function searchQuests() {
            var input = document.getElementById('search-box').value.toLowerCase();
            var questNodes = document.getElementsByClassName('quest-node');
            
            // Убираем предыдущие подсветки
            var highlights = document.getElementsByClassName('highlight');
            while(highlights.length > 0) {
                highlights[0].classList.remove('highlight');
            }
            
            for(var i = 0; i < questNodes.length; i++) {
                var node = questNodes[i];
                var text = node.textContent.toLowerCase();
                
                if(text.includes(input)) {
                    node.style.display = '';
                    if(input.length > 0) {
                        node.classList.add('highlight');
                    }
                } else {
                    node.style.display = 'none';
                }
            }
        }
    """
    
    # Добавляем поле поиска
    search_box = soup.new_tag('input', id='search-box', type='text', 
                             placeholder='Поиск по квестам...', 
                             onkeyup='searchQuests()')

    # Добавляем элементы в начало body
    soup.body.insert(0, search_box)
    soup.body.insert(1, contents)
    soup.head.append(search_script)

    # Добавляем кнопку "Наверх"
    back_to_top = soup.new_tag('a', href='#contents', **{'class': 'back-to-top'})
    back_to_top.string = 'Наверх'
    soup.body.append(back_to_top)

    # Сохраняем обновленный HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

def main():
    input_file = 'quest_structure.html'  # Исходный файл
    output_file = 'quest_structure_enhanced.html'  # Новый файл с навигацией
    
    if os.path.exists(input_file):
        enhance_quest_html(input_file, output_file)
        print(f"Создан улучшенный файл: {output_file}")
    else:
        print(f"Файл {input_file} не найден!")

if __name__ == "__main__":
    main()