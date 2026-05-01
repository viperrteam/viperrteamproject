import json
import random
from datetime import datetime

# ------------------- НАСТРОЙКИ -------------------
NUM_COURSES = 100  # количество курсов (можно менять)
OUTPUT_FILE = "courses.json"

# Банк названий, описаний и тегов для генерации
TITLES = [
    "Введение в программирование на Python",
    "Продвинутый Python: ООП и паттерны",
    "Анализ данных с Pandas и NumPy",
    "Машинное обучение для начинающих",
    "Основы нейронных сетей и Deep Learning",
    "Веб-разработка на Django",
    "FastAPI: создание высокопроизводительных API",
    "Frontend-разработка: HTML, CSS, JavaScript",
    "React для современных веб-приложений",
    "Базы данных: SQL и PostgreSQL",
    "NoSQL базы данных: MongoDB",
    "Алгоритмы и структуры данных",
    "Дискретная математика для программистов",
    "Математический анализ для Data Science",
    "Линейная алгебра и её приложения",
    "Теория вероятностей и статистика",
    "Компьютерное зрение с OpenCV",
    "Обработка естественного языка (NLP)",
    "Разработка игр на Unity",
    "Основы кибербезопасности",
    "DevOps: CI/CD и Docker",
    "Облачные вычисления: AWS и Azure",
    "UI/UX дизайн для разработчиков",
    "Графический дизайн в Figma",
    "3D-моделирование в Blender",
    "Мобильная разработка на Flutter",
    "Android разработка на Kotlin",
    "iOS разработка на Swift",
    "Кроссплатформенная разработка с React Native",
    "Блокчейн и криптовалюты",
    "Интернет вещей (IoT) с Arduino",
    "Робототехника на Python",
    "Системное администрирование Linux",
    "Сетевые технологии и протоколы",
    "Тестирование программного обеспечения",
    "Управление IT-проектами (Agile/Scrum)",
    "Цифровой маркетинг и SEO",
    "Продуктовый менеджмент в IT",
    "Основы бизнес-аналитики",
    "Этика и право в IT сфере"
]

DESCRIPTIONS = [
    "Практический курс, который поможет освоить {topic} с нуля. Вы научитесь применять знания в реальных проектах.",
    "Полный курс по {topic}. Включает теорию, практические задания и финальный проект.",
    "Углублённое изучение {topic} для продолжающих. Рассматриваются продвинутые техники и подходы.",
    "Экспресс-курс по {topic} для занятых. Всего за 4 недели вы освоите ключевые навыки.",
    "Авторский курс от эксперта. Уникальная методика обучения {topic} с примерами из реальной практики.",
    "Бесплатный вводный курс по {topic}. Идеально подходит для знакомства с предметом.",
    "Интенсив по {topic} с менторской поддержкой и проверкой домашних заданий.",
    "Курс-тренажёр: {topic} на практике. Более 50 интерактивных заданий и кейсов.",
    "Профессиональная переподготовка по направлению {topic}. Диплом государственного образца.",
    "Мастер-класс по {topic} от топового эксперта отрасли. Только практика и лайфхаки."
]

TAGS_POOL = [
    "Python", "Java", "JavaScript", "C++", "C#", "PHP", "Ruby", "Go", "Rust", "Swift", "Kotlin",
    "Web разработка", "Frontend", "Backend", "Fullstack", "React", "Angular", "Vue", "Django", "Flask", "FastAPI",
    "Базы данных", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "Data Science", "Анализ данных", "Машинное обучение", "Нейронные сети", "Deep Learning", "NLP",
    "Компьютерное зрение",
    "Алгоритмы", "Структуры данных", "Дискретная математика", "Линейная алгебра", "Мат. анализ", "Статистика",
    "Мобильная разработка", "Android", "iOS", "Flutter", "React Native",
    "GameDev", "Unity", "Unreal Engine", "Blender", "3D моделирование",
    "Кибербезопасность", "DevOps", "Docker", "Kubernetes", "Облачные технологии", "AWS", "Azure",
    "UI/UX", "Дизайн", "Figma", "Photoshop", "Illustrator",
    "Блокчейн", "IoT", "Робототехника", "Linux", "Сети", "Тестирование", "QA",
    "Управление проектами", "Agile", "Scrum", "Маркетинг", "SEO", "Продуктовая аналитика"
]


# ------------------- ГЕНЕРАЦИЯ -------------------
def generate_course(course_id):
    """Генерирует один курс со случайными данными"""

    # Выбираем случайное название
    title = random.choice(TITLES)
# Генерируем уникальное описание, вставляя тему в шаблон
    topic = title.lower()
    description_template = random.choice(DESCRIPTIONS)
    description = description_template.format(topic=topic)

    # Выбираем 2-5 случайных тегов
    num_tags = random.randint(2, 5)
    tags = random.sample(TAGS_POOL, num_tags)

    # Убеждаемся, что тег из названия есть в списке (логичность)
    # Пример: если в названии "Python", добавляем тег Python
    for tag in TAGS_POOL:
        if tag.lower() in title.lower() and tag not in tags:
            tags.append(tag)
            break

    # Убираем дубликаты тегов
    tags = list(set(tags))

    return {
        "id": course_id,
        "title": title,
        "description": description,
        "tags": tags
    }

def generate_courses(num_courses):
    """Генерирует указанное количество курсов"""
    courses = []
    for i in range(1, num_courses + 1):
        course = generate_course(i)
        courses.append(course)
    return courses

def save_to_json(courses, filename):
    """Сохраняет курсы в JSON файл"""
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_courses": len(courses),
        "courses": courses
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Сгенерировано {len(courses)} курсов")
    print(f"Файл сохранён: {filename}")

if __name__ == "__main__":
    print(f"Генерация {NUM_COURSES} курсов...")
    courses = generate_courses(NUM_COURSES)
    save_to_json(courses, OUTPUT_FILE)