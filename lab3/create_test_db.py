import sqlite3
import os


def create_test_database():
    # Удаляем существующую базу данных если есть
    if os.path.exists('test_database.db'):
        os.remove('test_database.db')

    # Создаем соединение с базой данных
    conn = sqlite3.connect('test_database.db')
    cursor = conn.cursor()

    # Создаем таблицу Users
    cursor.execute('''
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Создаем таблицу Products
    cursor.execute('''
        CREATE TABLE Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            in_stock INTEGER DEFAULT 0
        )
    ''')

    # Создаем таблицу Orders
    cursor.execute('''
        CREATE TABLE Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users (id),
            FOREIGN KEY (product_id) REFERENCES Products (id)
        )
    ''')

    # Добавляем индексы
    cursor.execute('CREATE INDEX idx_user_email ON Users(email)')
    cursor.execute('CREATE INDEX idx_product_category ON Products(category)')

    # Добавляем тестовые данные в Users
    users_data = [
        ('Иван Иванов', 'ivan@mail.com', 25),
        ('Мария Петрова', 'maria@mail.com', 30),
        ('Алексей Сидоров', 'alex@mail.com', 35),
        ('Елена Кузнецова', 'elena@mail.com', 28),
        ('Дмитрий Волков', 'dmitry@mail.com', 40)
    ]

    cursor.executemany(
        'INSERT INTO Users (name, email, age) VALUES (?, ?, ?)',
        users_data
    )

    # Добавляем тестовые данные в Products
    products_data = [
        ('Ноутбук', 50000.0, 'Электроника', 10),
        ('Смартфон', 25000.0, 'Электроника', 15),
        ('Книга', 500.0, 'Книги', 100),
        ('Кофе', 350.0, 'Продукты', 50),
        ('Футболка', 1200.0, 'Одежда', 30)
    ]

    cursor.executemany(
        'INSERT INTO Products (product_name, price, category, in_stock) VALUES (?, ?, ?, ?)',
        products_data
    )

    # Добавляем тестовые данные в Orders
    orders_data = [
        (1, 1, 2),
        (1, 2, 1),
        (2, 3, 5),
        (3, 4, 3),
        (4, 5, 1),
        (2, 1, 1)
    ]

    cursor.executemany(
        'INSERT INTO Orders (user_id, product_id, quantity) VALUES (?, ?, ?)',
        orders_data
    )

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    print("Тестовая база данных 'test_database.db' успешно создана!")
    print("Содержимое базы данных:")
    print("- Таблица Users (5 записей)")
    print("- Таблица Products (5 записей)")
    print("- Таблица Orders (6 записей)")
    print("- Индексы для оптимизации запросов")


if __name__ == '__main__':
    create_test_database()