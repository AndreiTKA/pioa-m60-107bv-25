import json
import csv

TYPES = {'int': int, 'str': str}

class StudentTable:
    def __init__(self) -> None:
        self._records: list[tuple[int, str, str, int, str]] = []

    def _check_filters(self, record: tuple[int, str, str, int, str],
                       filters: dict) -> bool:
        if "id" in filters and record[0] != filters["id"]:
            return False
        if "first_name" in filters and record[1] != filters["first_name"]:
            return False
        if "second_name" in filters and record[2] != filters["second_name"]:
            return False
        if "age" in filters and record[3] != filters["age"]:
            return False
        if "sex" in filters and record[4] != filters["sex"]:
            return False
        return True

    def create(self, student_id: int, first_name: str,
               second_name: str, age: int, sex: str) -> tuple[int, str, str, int, str]:

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

        return [record for record in self._records if self._check_filters(record, filters)]

    def update(self, filters: dict, new_values: dict) -> int:
        if not filters:
            raise ValueError("Не заданы фильтры для обновления. Обновление всех записей запрещено.")

        updated_count = 0
        for i, record in enumerate(self._records):
            if self._check_filters(record, filters):
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
            if self._check_filters(self._records[i], filters):
                del self._records[i]
                deleted_count += 1

        if deleted_count == 0:
            raise ValueError("Не найдено записей, соответствующих фильтрам.")
        return deleted_count


class JsonStudentTable(StudentTable):
    def __init__(self, path):
        super().__init__()
        self.path = path


    def save(self) -> None:
        data = []
        for record in self._records:
            data.append({
                "id": record[0],
                "first_name": record[1],
                "second_name": record[2],
                "age": record[3],
                "sex": record[4]
            })
        to_write = {'data': data, 'table_structure': {'columns': ['id', 'first_name', 'second_name', 'age', 'sex'], 'types': ['int', 'str', 'str', 'int', 'str']}}
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(to_write, file, ensure_ascii=False, indent=2)

    def load(self) -> None:
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if ['id', 'first_name', 'second_name', 'age', 'sex'] != data['table_structure']['columns']:
            raise KeyError('Заголовки таблицы некорректны')

        if ['int', 'str', 'str', 'int', 'str'] != data['table_structure']['types']:
            raise TypeError('Типы данных некорректны')
        self._records.clear()
        for item in data['data']:
            record = (
                item["id"],
                item["first_name"],
                item["second_name"],
                item["age"],
                item["sex"]
            )
            for it, _type in zip(record, data['table_structure']['types']):
                if not isinstance(it, TYPES[_type]):
                    raise TypeError('Неdерный тип данных {}'.format(it))

            self._records.append(record)

    def update(self, *args, **kwargs):
        data = super().update(*args, **kwargs)
        self.save()
        return data

    def create(self, *args, **kwargs):
        data = super().create(*args, **kwargs)
        self.save()
        return data

    def delete(self, *args, **kwargs):
        data = super().delete(*args, **kwargs)
        self.save()
        return data


class CsvStudentTable(StudentTable):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def save(self) -> None:
        with open(self.path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["id", "first_name", "second_name", "age", "sex"])
            writer.writerows(self._records)

    def load(self) -> None:
        with open(self.path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            self._records.clear()
            for row in reader:
                record = (
                    int(row[0]),
                    row[1],
                    row[2],
                    int(row[3]),
                    row[4]
                )
                self._records.append(record)

    def update(self, *args, **kwargs):
        data = super().update(*args, **kwargs)
        self.save()
        return data

    def create(self, *args, **kwargs):
        data = super().create(*args, **kwargs)
        self.save()
        return data

    def delete(self, *args, **kwargs):
        data = super().delete(*args, **kwargs)
        self.save()
        return data