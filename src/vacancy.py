class Vacancy:
    """Класс для представления вакансии."""

    __slots__ = ("name", "url", "employer", "__salary")

    def __init__(self, name, url, employer, salary):
        self.name = name
        self.url = url
        self.employer = employer
        self.__salary = self.validate_salary(salary)

    @staticmethod
    def validate_salary(salary) -> str:
        """Валидация зарплаты."""

        # 1. Если пусто
        if not salary:
            return "Зарплата не указана"

        # 2. Если уже строка - возвращаем как есть
        if isinstance(salary, str):
            return salary

        # 3. Если словарь с данными о зарплате
        salary_from = salary.get("from")
        salary_to = salary.get("to")

        if salary_from and salary_to:
            return f"{salary_from} - {salary_to} ₽"
        elif salary_from:
            return f"от {salary_from} ₽"
        elif salary_to:
            return f"до {salary_to} ₽"

        # 4. Любой другой случай
        return "Зарплата не указана"

    @property
    def salary(self):
        """Свойство для доступа к зарплате."""

        return self.__salary

    @classmethod
    def cast_to_object_list(cls, filtered_vacancies: list) -> list:
        """Создание списка объектов из отфильтрованных данных."""

        vacancies = []
        for vac in filtered_vacancies:
            # Теперь vac уже содержит нужные ключи: name, url, employer, salary
            vacancy = cls(
                name=vac.get("name", ""),
                url=vac.get("url", ""),
                employer=vac.get("employer", ""),
                salary=vac.get("salary")
            )
            vacancies.append(vacancy)
        return vacancies

    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "employer": self.employer,
            "salary": self.__salary
        }

    def __str__(self):
        return (
            f"Вакансия: {self.name}\n"
            f"Работодатель: {self.employer}\n"
            f"Зарплата: {self.__salary}\n"
            f"Ссылка: {self.url}"
        )

    def __repr__(self):
        return f"Vacancy(name='{self.name}', salary='{self.__salary}')"

    def get_salary_number(self):
        """Извлекает число из строки зарплаты."""

        text = self.__salary

        num_str = ''
        for char in text:
            if char.isdigit():
                num_str += char
            elif num_str:
                break

        return int(num_str) if num_str else 0

    def __lt__(self, other):
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.get_salary_number() < other.get_salary_number()

    def __gt__(self, other):
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.get_salary_number() > other.get_salary_number()

    def __eq__(self, other):
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.get_salary_number() == other.get_salary_number()

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __ne__(self, other):
        return not self == other
