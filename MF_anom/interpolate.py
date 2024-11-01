import numpy as np
import matplotlib.pyplot as plt
import json

# Задаем координаты центра основания
start_point = np.array([5891.979004, 124.585770, 5005.175781])

# Параметры спиралей
num_points = 50  # Количество точек в одну спираль
turns = 10  # Количество оборотов
radius = 15  # Радиус (половина диаметра спирали)
height_increase = 1  # Увеличение высоты на каждый оборот

# Генерация углов для спиралей
angles = np.linspace(0, turns * 2 * np.pi, num_points)

# Создаем координаты для первой спирали (по часовой стрелке)
x_spiral_1 = start_point[0] + radius * np.cos(angles)
z_spiral_1 = start_point[2] + radius * np.sin(angles)
height_1 = start_point[1] + height_increase * np.linspace(0, turns, num_points)

# Собираем точки первой спирали
spiral_points_1 = np.vstack((x_spiral_1, height_1, z_spiral_1)).T

# Создаем координаты для второй спирали (против часовой стрелки)
x_spiral_2 = start_point[0] + radius * np.cos(-angles)
z_spiral_2 = start_point[2] + radius * np.sin(-angles)
height_2 = start_point[1] + height_increase * np.linspace(0, turns, num_points)

# Собираем точки второй спирали
spiral_points_2 = np.vstack((x_spiral_2, height_2, z_spiral_2)).T

# Создаем структуру JSON для первой спирали
wander_anomaly_positions = []

# Добавляем точки первой спирали
for coord in spiral_points_1:
    position = {
        "m_pos": f"{coord[0]} {coord[1]} {coord[2]}",
        "m_speedX": 1,
        "m_speedY": 1,
        "m_speedZ": 1,
        "m_radius": 2.0
    }
    wander_anomaly_positions.append(position)

# Создаем финальную структуру для первой спирали
output_json_1 = {
    "m_WanderAnomalyOnePosition": wander_anomaly_positions
}

# Сохраняем в файл для первой спирали
with open('spiral_coordinates.json', 'w') as json_file:
    json.dump(output_json_1, json_file, indent=4)

# Создаем структуру JSON для второй спирали (инвертированные координаты)
wander_anomaly_positions_inverse = []

# Добавляем точки второй спирали
for coord in spiral_points_2:
    position = {
        "m_pos": f"{coord[0]} {coord[1]} {coord[2]}",
        "m_speedX": 1,
        "m_speedY": 1,
        "m_speedZ": 1,
        "m_radius": 2.0
    }
    wander_anomaly_positions_inverse.append(position)

# Создаем финальную структуру для второй спирали
output_json_2 = {
    "m_WanderAnomalyTwoPosition": wander_anomaly_positions_inverse
}

# Сохраняем в файл для второй спирали
with open('spiral_coordinates_inverse.json', 'w') as json_file:
    json.dump(output_json_2, json_file, indent=4)

# Визуализация
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Рисуем первую спираль
ax.plot(spiral_points_1[:, 0], spiral_points_1[:, 1], spiral_points_1[:, 2], label='Spiral 1', color='orange')
# Рисуем вторую спираль
ax.plot(spiral_points_2[:, 0], spiral_points_2[:, 1], spiral_points_2[:, 2], label='Spiral 2', color='blue')

# Отображаем начальную точку
ax.scatter(start_point[0], start_point[1], start_point[2], color='green', label='Start Point', s=100)

ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
ax.legend()
plt.title('3D Ascending Parallel Spirals')
plt.show()
