import pytest

from src.vacancy import Vacancy


@pytest.fixture()
def vacancy():
    return Vacancy('Техник-Слесарь', 'https://hh.ru/vacancy/128720176', 'Альянс региональных групп оптового сбыта',
                   '400000 - 500000 ₽')


def test_init(vacancy):
    assert vacancy.name == 'Техник-Слесарь'
    assert vacancy.url == "https://hh.ru/vacancy/128720176"
    assert vacancy.employer == "Альянс региональных групп оптового сбыта"
    assert vacancy.salary == "400000 - 500000 ₽"


def test_validate_salary():
    # Тестируем статический метод
    assert Vacancy.validate_salary(None) == "Зарплата не указана"
    assert Vacancy.validate_salary("100000 ₽") == "100000 ₽"
    assert Vacancy.validate_salary({"from": 100000, "to": 150000}) == "100000 - 150000 ₽"


def test_cast_to_object_list():
    data = [{"name": "Dev", "url": "url", "employer": "Comp", "salary": "100000 ₽"}]
    vacancies = Vacancy.cast_to_object_list(data)
    assert len(vacancies) == 1
    assert vacancies[0].name == "Dev"


def test_to_dict(vacancy):
    result = vacancy.to_dict()
    assert isinstance(result, dict)
    assert result["name"] == "Техник-Слесарь"


def test_str(vacancy):
    text = str(vacancy)
    assert "Техник-Слесарь" in text
    assert "400000 - 500000 ₽" in text


def test_repr(vacancy):
    text = repr(vacancy)
    assert "Vacancy(" in text


def test_get_salary_number(vacancy):
    assert vacancy.get_salary_number() == 400000
    # Другие случаи создаем локально
    assert Vacancy("A", "b", "c", "50000 ₽").get_salary_number() == 50000
    assert Vacancy("A", "b", "c", None).get_salary_number() == 0


def test_comparison_operators():
    """Все тесты сравнения в одном методе"""
    high = Vacancy("High", "url1", "emp1", "400000 - 500000 ₽")
    low = Vacancy("Low", "url2", "emp2", "50000 ₽")
    same = Vacancy("Same", "url3", "emp3", "400000 - 500000 ₽")

    # <
    assert low < high
    assert not high < low

    # >
    assert high > low
    assert not low > high

    # ==
    assert high == same
    assert not high == low

    # <=
    assert low <= high
    assert high <= same
    assert not high <= low

    # >=
    assert high >= low
    assert high >= same
    assert not low >= high

    # !=
    assert high != low
    assert not high != same

