import json
import os
from abc import ABC, abstractmethod


class Json(ABC):
    @abstractmethod
    def add_vacancy(self, vacancies):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_name):
        pass


class JSONSaver(Json):
    """Класс для работы с файлами"""

    def __init__(self, filename="vacancies.json"):
        self.__filename = f"data/{filename}"

        # Создаем папку и файл если нет
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(self.__filename):
            with open(self.__filename, "w", encoding="UTF-8") as f:
                json.dump([], f)

    def add_vacancy(self, vacancies):
        """Добавляет вакансии без дублей."""

        # Читаем существующие
        existing = self.get_vacancies()

        # Простая проверка дублей по названию
        existing_names = set()
        for vac in existing:
            if hasattr(vac, 'name'):
                existing_names.add(vac.name)
            elif isinstance(vac, dict):
                existing_names.add(vac.get('name', ''))

        # Фильтруем новые
        new_vacancies = []
        for vacancy in vacancies:
            vac_name = ""
            if hasattr(vacancy, 'name'):
                vac_name = vacancy.name
            elif isinstance(vacancy, dict):
                vac_name = vacancy.get('name', '')

            if vac_name and vac_name not in existing_names:
                new_vacancies.append(vacancy)

        if not new_vacancies:
            return

        # Сохраняем все вместе
        all_vacancies = existing + new_vacancies

        with open(self.__filename, "w", encoding="UTF-8") as f:
            # Преобразуем в словари
            data = []
            for vac in all_vacancies:
                if hasattr(vac, 'to_dict'):
                    data.append(vac.to_dict())
                else:
                    data.append(vac)

            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_vacancies(self):
        """Загружает вакансии."""

        try:
            with open(self.__filename, encoding="UTF-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def delete_vacancy(self, vacancy_name):
        """Удаляет вакансию по названию."""

        vacancies = self.get_vacancies()

        # Фильтруем
        new_vacancies = []
        for vac in vacancies:
            if isinstance(vac, dict):
                if vac.get('name') != vacancy_name:
                    new_vacancies.append(vac)

        # Сохраняем если что-то удалили
        if len(new_vacancies) < len(vacancies):
            with open(self.__filename, "w", encoding="UTF-8") as f:
                json.dump(new_vacancies, f, indent=4, ensure_ascii=False)
            return True

        return False
