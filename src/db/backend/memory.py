class StudentTable:
    def __init__(self) -> None:
        self._records: list[tuple[int, str, str, int, str]] = []

    def create(self, student_id: int, first_name: str,
               second_name: str, age: int, sex: str) -> tuple[int, str, str, int, str]:
        if age < 0:
            raise ValueError("Поле age не может быть отрицательным.")

        if any(record[0] == student_id for record in self._records):
            raise ValueError(f"Запись с id={student_id} уже существует.")

        new_record = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._records.append(new_record)
        return new_record

    def select(self, filters: dict | None = None) -> list[tuple[int, str, str, int, str]]:
        if not filters:
            return self._records.copy()

        result = []
        for record in self._records:
            match = True
            if "id" in filters and record[0] != filters["id"]:
                match = False
            if "first_name" in filters and record[1] != filters["first_name"]:
                match = False
            if "second_name" in filters and record[2] != filters["second_name"]:
                match = False
            if "age" in filters and record[3] != filters["age"]:
                match = False
            if "sex" in filters and record[4] != filters["sex"]:
                match = False
            if match:
                result.append(record)
        return result

    def update(self, filters: dict, new_values: dict) -> int:
        if not filters:
            raise ValueError("Не заданы фильтры для обновления. Обновление всех записей запрещено.")
        if "id" in new_values:
            raise ValueError("Поле id нельзя изменять.")

        if "age" in new_values and new_values["age"] < 0:
            raise ValueError("Поле age не может быть отрицательным.")

        updated_count = 0
        for i, record in enumerate(self._records):
            match = True
            if "id" in filters and record[0] != filters["id"]:
                match = False
            if "first_name" in filters and record[1] != filters["first_name"]:
                match = False
            if "second_name" in filters and record[2] != filters["second_name"]:
                match = False
            if "age" in filters and record[3] != filters["age"]:
                match = False
            if "sex" in filters and record[4] != filters["sex"]:
                match = False

            if match:
                updated_record = list(record)
                if "first_name" in new_values:
                    updated_record[1] = new_values["first_name"].strip()
                if "second_name" in new_values:
                    updated_record[2] = new_values["second_name"].strip()
                if "age" in new_values:
                    updated_record[3] = new_values["age"]
                if "sex" in new_values:
                    updated_record[4] = new_values["sex"].strip()
                self._records[i] = tuple(updated_record)
                updated_count += 1

        if updated_count == 0:
            raise ValueError("Не найдено записей, соответствующих фильтрам.")
        return updated_count

    def delete(self, filters: dict) -> int:
        if not filters:
            raise ValueError("Не заданы фильтры для удаления. Удаление всех записей запрещено.")

        deleted_count = 0
        for i in range(len(self._records) - 1, -1, -1):
            record = self._records[i]
            match = True
            if "id" in filters and record[0] != filters["id"]:
                match = False
            if "first_name" in filters and record[1] != filters["first_name"]:
                match = False
            if "second_name" in filters and record[2] != filters["second_name"]:
                match = False
            if "age" in filters and record[3] != filters["age"]:
                match = False
            if "sex" in filters and record[4] != filters["sex"]:
                match = False

            if match:
                del self._records[i]
                deleted_count += 1

        if deleted_count == 0:
            raise ValueError("Не найдено записей, соответствующих фильтрам.")
        return deleted_count
