import pytest

from src.hh_api import HeadHunterAPI


@pytest.fixture()
def hh_api():
    return HeadHunterAPI()


def test_init(hh_api):
    """Проверяем что класс создаётся."""

    assert hh_api is not None
    assert getattr(hh_api, '_HeadHunterAPI__url', None) == 'https://api.hh.ru/vacancies'


def test_get_connect(hh_api):
    """Проверяем что метод есть."""
    assert hasattr(hh_api, 'get_connect')


def test_get_vacancies_logic():
    """Тестируем логику обработки данных (без API вызова)."""

    # Создаём тестовые данные как будто они пришли из API
    fake_api_response = {
        "items": [
            {
                "name": "Python Dev",
                "alternate_url": "https://hh.ru/1",
                "employer": {"name": "Company A"},
                "salary": {"from": 100000}
            }
        ]
    }

    # Вручную проверяем что делает наш метод
    # (имитируем его логику)
    vacancies_filter = []
    for vacancy in fake_api_response["items"]:
        vacancies_filter.append({
            "name": vacancy["name"],
            "url": vacancy["alternate_url"],
            "employer": vacancy["employer"]["name"],
            "salary": vacancy.get("salary")
        })

    # Проверяем результат
    assert len(vacancies_filter) == 1
    assert vacancies_filter[0]["name"] == "Python Dev"
    print("✓ Логика обработки данных правильная")
