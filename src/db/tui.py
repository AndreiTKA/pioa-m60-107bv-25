from src.db.backend.memory import StudentTable


class Tui:
    def __init__(self) -> None:
        self._student_table = StudentTable()

    def _print_menu(self) -> None:
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи")
        print("4. Обновить записи")
        print("5. Удалить записи")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _build_filters_from_input(self) -> dict:
        filters = {}
        raw_id = self._read_optional_int("id: ")
        if raw_id is not None:
            filters["id"] = raw_id

        first_name = input("first_name: ").strip()
        if first_name:
            filters["first_name"] = first_name

        second_name = input("second_name: ").strip()
        if second_name:
            filters["second_name"] = second_name

        raw_age = self._read_optional_int("age: ")
        if raw_age is not None:
            filters["age"] = raw_age

        sex = input("sex: ").strip()
        if sex:
            filters["sex"] = sex

        return filters

    def _print_records(self, records: list[tuple[int, str, str, int, str]]) -> None:
        if not records:
            print("Записи не найдены.")
            return
        for record in records:
            print(record)

    def _add_student(self) -> None:
        print("\nДобавление записи")
        student_id = self._read_int("id: ")
        first_name = input("first_name: ").strip()
        second_name = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()

        try:
            record = self._student_table.create(
                student_id, first_name, second_name, age, sex
            )
            print(f"Запись добавлена: {record}")
        except ValueError as exc:
            print(f"Ошибка: {exc}")

    def _show_all_students(self) -> None:
        print("\nСписок записей")
        self._print_records(self._student_table.select())

    def _select(self) -> None:
        print("\nПоиск по фильтру (Enter = пропустить поле)")
        filters = self._build_filters_from_input()
        records = self._student_table.select(filters)
        self._print_records(records)

    def update(self) -> None:
        print("\n=== Обновление записей ===")
        print("Сначала задайте фильтры для поиска записей, которые нужно обновить.")
        filters = self._build_filters_from_input()

        if not filters:
            print("Ошибка: необходимо указать хотя бы один фильтр.")
            return

        matched = self._student_table.select(filters)
        if not matched:
            print("Нет записей, соответствующих заданным фильтрам.")
            return

        print(f"\nНайдено {len(matched)} записей для обновления:")
        self._print_records(matched)

        confirm = input("Продолжить обновление? (y/n): ").strip().lower()
        if confirm != "y":
            print("Обновление отменено.")
            return

        print("\nВведите новые значения полей (Enter — не изменять):")
        new_values = {}
        first_name = input("Новое имя: ").strip()
        if first_name:
            new_values["first_name"] = first_name

        second_name = input("Новая фамилия: ").strip()
        if second_name:
            new_values["second_name"] = second_name

        raw_age = input("Новый возраст: ").strip()
        if raw_age:
            try:
                age = int(raw_age)
                new_values["age"] = age
            except ValueError:
                print("Ошибка: возраст должен быть целым числом. Изменения не сохранены.")
                return

        sex = input("Новый пол: ").strip()
        if sex:
            new_values["sex"] = sex

        if not new_values:
            print("Не указано ни одного нового значения. Обновление отменено.")
            return

        try:
            count = self._student_table.update(filters, new_values)
            print(f"Успешно обновлено записей: {count}")
        except ValueError as exc:
            print(f"Ошибка: {exc}")

    def _delete(self) -> None:
        print("\n=== Удаление записей ===")
        print("Задайте фильтры для поиска записей, которые нужно удалить.")
        filters = self._build_filters_from_input()

        if not filters:
            print("Ошибка: необходимо указать хотя бы один фильтр.")
            return

        matched = self._student_table.select(filters)
        if not matched:
            print("Нет записей, соответствующих заданным фильтрам.")
            return

        print(f"\nНайдено {len(matched)} записей для удаления:")
        self._print_records(matched)

        confirm = input("Подтвердите удаление (y/n): ").strip().lower()
        if confirm != "y":
            print("Удаление отменено.")
            return

        try:
            count = self._student_table.delete(filters)
            print(f"Успешно удалено записей: {count}")
        except ValueError as exc:
            print(f"Ошибка: {exc}")

    def run(self) -> None:
        while True:
            self._print_menu()
            action = input("Выберите действие: ").strip()

            if action == "1":
                self._add_student()
            elif action == "2":
                self._show_all_students()
            elif action == "3":
                self._select()
            elif action == "4":
                self.update()
            elif action == "5":
                self._delete()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")
