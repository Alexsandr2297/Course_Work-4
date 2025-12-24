from src.class_json import JSONSaver
from src.hh_api import HeadHunterAPI
from src.vacancy import Vacancy


def filter_vacancies(vacancies, keywords):
    """Фильтрует вакансии по ключевым словам."""

    if not keywords:
        return vacancies

    filtered = []
    for vacancy in vacancies:
        text = f"{vacancy.name} {vacancy.employer}".lower()
        for word in keywords:
            if word.lower() in text:
                filtered.append(vacancy)
                break
    return filtered


def filter_by_salary(vacancies, min_salary_input):
    """Фильтрует вакансии с зарплатой не ниже указанной."""

    if not min_salary_input:
        return vacancies

    try:
        min_salary = int(min_salary_input)
    except ValueError:
        return vacancies

    filtered = []
    for vacancy in vacancies:
        salary_text = vacancy.salary

        # Ищем первое число в строке зарплаты
        for i, char in enumerate(salary_text):
            if char.isdigit():
                # Собираем все следующие цифры
                num_str = char
                for next_char in salary_text[i + 1:]:
                    if next_char.isdigit():
                        num_str += next_char
                    else:
                        break

                # Если нашли число и оно >= min_salary
                if num_str and int(num_str) >= min_salary:
                    filtered.append(vacancy)
                    break

    return filtered


def sort_by_salary(vacancies):
    """Сортирует вакансии по зарплате."""

    def get_salary_value(vac):
        salary_text = vac.salary

        # Извлекаем числа вручную
        numbers = []
        current_num = ''

        for char in str(salary_text):
            if char.isdigit():
                current_num += char
            elif current_num:
                numbers.append(int(current_num))
                current_num = ''

        if current_num:
            numbers.append(int(current_num))

        return numbers[0] if numbers else 0

    return sorted(vacancies, key=get_salary_value, reverse=True)


def print_results(vacancies):
    """Выводит результаты."""

    if not vacancies:
        print("Нет подходящих вакансий.")
        return

    print(f"\nРезультаты ({len(vacancies)}):")
    print("=" * 60)

    for i, vac in enumerate(vacancies, 1):
        print(f"{i}. {vac.name}")
        print(f"   Компания: {vac.employer}")
        print(f"   Зарплата: {vac.salary}")  # используем свойство salary
        print(f"   Ссылка: {vac.url}")
        print("-" * 60)


def user_interaction() -> None:
    """Взаимодействие с пользователем."""
    print("=" * 60)
    print("ПОИСК ВАКАНСИЙ НА HH.RU")
    print("=" * 60)

    # 1. Поисковый запрос
    search_query = input("\nВведите поисковый запрос: ")
    if not search_query:
        print("Запрос не может быть пустым!")
        return

    # 2. Получаем вакансии
    print(f"\nИщем '{search_query}'...")
    hh_api = HeadHunterAPI()
    hh_vacancies = hh_api.get_vacancies(search_query)

    if not hh_vacancies:
        print("Вакансии не найдены.")
        return

    all_vacancies = Vacancy.cast_to_object_list(hh_vacancies)
    print(f"Найдено: {len(all_vacancies)} вакансий")

    # 3. Топ N
    try:
        top_n = int(input("\nВведите количество вакансий для вывода в топ N: "))
        if top_n <= 0:
            print("Число должно быть больше 0!")
            return
    except ValueError:
        print("Введите число!")
        return

    # 4. Ключевые слова
    filter_words = input("\nВведите ключевые слова для фильтрации вакансий: ").split()

    # 5. Диапазон зарплат
    salary_range = input("Введите диапазон зарплат (например: 100000 - 150000): ")

    # 6. Обработка
    filtered = filter_vacancies(all_vacancies, filter_words)
    if filter_words:
        print(f"После фильтрации по ключевым словам: {len(filtered)} вакансий")

    ranged = filter_by_salary(filtered, salary_range)
    if salary_range:
        print(f"После фильтрации по зарплате: {len(ranged)} вакансий")

    sorted_vacancies = sort_by_salary(ranged)
    top_vacancies = sorted_vacancies[:top_n]

    # 7. Выводим
    print_results(top_vacancies)

    # 8. Сохраняем
    save = input("\nСохранить результаты? (да/нет): ").lower()
    if save == 'да':
        json_saver = JSONSaver()
        json_saver.add_vacancy(top_vacancies)
        print(f"Сохранено {len(top_vacancies)} вакансий в data/vacancies.json")

    print("\nГотовo!")


if __name__ == "__main__":
    user_interaction()
