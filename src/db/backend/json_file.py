import json
from src.db.backend.memory import StudentTable, TYPES


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
