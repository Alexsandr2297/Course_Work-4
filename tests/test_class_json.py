import os

import pytest

from src.class_json import JSONSaver


@pytest.fixture()
def js():
    """Фикстура для JSONSaver - каждый тест с чистого листа"""

    filename = "test_vacancies.json"

    # Полный путь к файлу
    file_path = f"data/{filename}"

    # Удаляем файл если существует
    if os.path.exists(file_path):
        os.remove(file_path)

    # Удаляем папку data если пуста
    if os.path.exists("data") and not os.listdir("data"):
        os.rmdir("data")

    # Создаем новый экземпляр
    saver = JSONSaver(filename)

    yield saver

    # Очистка после теста
    if os.path.exists(file_path):
        os.remove(file_path)
    # Не удаляем папку data - она может быть создана классом JSONSaver


def test_init(js):

    # Проверяем что можно получить вакансии (значит файл создан)
    vacancies = js.get_vacancies()
    assert isinstance(vacancies, list)
    assert vacancies == []


def test_add_vacancy(js):
    """Тест добавления вакансии"""
    vacancy = {"name": "Python Developer", "salary": "100000 ₽"}

    js.add_vacancy([vacancy])

    result = js.get_vacancies()
    assert len(result) == 1
    assert result[0]["name"] == "Python Developer"


def test_get_vacancies(js):
    """Тест получения вакансий"""

    # Должен быть пустой список при создании
    assert js.get_vacancies() == []

    # Добавляем и проверяем
    js.add_vacancy([{"name": "Test", "salary": "50000 ₽"}])
    vacancies = js.get_vacancies()
    assert len(vacancies) == 1
    assert vacancies[0]["salary"] == "50000 ₽"


def test_delete_vacancy(js):
    """Тест удаления вакансии"""

    # Добавляем
    js.add_vacancy([
        {"name": "Job1", "salary": "50000 ₽"},
        {"name": "Job2", "salary": "60000 ₽"}
    ])

    # Проверяем добавление
    assert len(js.get_vacancies()) == 2

    # Удаляем
    assert js.delete_vacancy("Job1") is True

    # Проверяем
    vacancies = js.get_vacancies()
    assert len(vacancies) == 1
    assert vacancies[0]["name"] == "Job2"

    # Несуществующая
    assert js.delete_vacancy("NonExistent") is False
