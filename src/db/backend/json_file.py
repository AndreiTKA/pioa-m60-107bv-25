import json
import os
from src.db.backend.memory import StudentTable, TYPES


class JsonStudentTable(StudentTable):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.table_structure = {
            'columns': ['id', 'first_name', 'second_name', 'age', 'sex'],
            'types': ['int', 'str', 'str', 'int', 'str']
        }
        self.load()

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
        to_write = {'data': data, 'table_structure': self.table_structure}
        try:
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump(to_write, file, ensure_ascii=False, indent=2)
        except OSError as e:
            raise OSError(f'Ошибка при сохранении файла {self.path}: {e}')

    def load(self) -> None:
        try:
            if not os.path.exists(self.path):
                self.save()
                return

            with open(self.path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f'Ошибка чтения JSON из файла {self.path}: поврежденный формат',
                        e.doc, e.pos
                    )

        except OSError as e:
            raise OSError(f'Ошибка при чтении файла {self.path}: {e}')

        try:
            if self.table_structure['columns'] != data['table_structure']['columns']:
                raise KeyError('Заголовки таблицы некорректны')

            if self.table_structure['types'] != data['table_structure']['types']:
                raise TypeError('Типы данных некорректны')
        except KeyError as e:
            raise KeyError(f'Отсутствуют ключи структуры таблицы в файле {self.path}: {e}')

        self._records.clear()
        for item in data['data']:
            try:
                record = (
                    item["id"],
                    item["first_name"],
                    item["second_name"],
                    item["age"],
                    item["sex"]
                )
            except KeyError as e:
                raise KeyError(f'Отсутствует ключ в записи данных: {e}')

            for it, _type in zip(record, data['table_structure']['types']):
                if not isinstance(it, TYPES[_type]):
                    raise TypeError(f'Неверный тип данных {it}, ожидался {_type}')

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