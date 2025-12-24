from abc import ABC, abstractmethod

import requests


class HH(ABC):
    """абстрактный класс для подключения с API"""

    @abstractmethod
    def get_vacancies(self, text: str, per_page: int):
        """получение вакансий"""

        pass


class HeadHunterAPI(HH):
    """Класс для работы с API (HH.ru)"""

    def __init__(self):
        """Кокнструктор для API"""

        self.__url = 'https://api.hh.ru/vacancies'

    def get_connect(self, text: str, per_page: int):
        """Получем запрос на подключение API"""

        params = {"text": text, "per_page": per_page}
        connect = requests.get(self.__url, params=params)
        return connect

    def get_vacancies(self, text: str, per_page: int = 20):
        """Получаем вакансии"""
        response = self.get_connect(text, per_page)
        vacancies = response.json()["items"]

        vacancies_filter = []
        for vacancy in vacancies:
            # Безопасное получение URL
            url = vacancy.get("alternate_url") or vacancy.get("url") or ""

            # Безопасное получение employer name
            employer = vacancy.get("employer")
            employer_name = employer.get("name", "") if employer else ""

            vacancies_filter.append({
                "name": vacancy.get("name", ""),
                "url": url,
                "employer": employer_name,
                "salary": vacancy.get("salary")
            })

        return vacancies_filter


# hh = HeadHunterAPI()
# print(hh.get_vacancies("python"))
