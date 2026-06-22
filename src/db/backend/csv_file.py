import csv
import os
from src.db.backend.memory import StudentTable, TYPES


class CsvStudentTable(StudentTable):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.table_structure = {
            'columns': ['id', 'first_name', 'second_name', 'age', 'sex'],
            'types': ['int', 'str', 'str', 'int', 'str']
        }

        self.load()

    def save(self) -> None:
        try:
            with open(self.path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                schema_info = [
                    'SCHEMA',
                    ','.join(self.table_structure['columns']),
                    ','.join(self.table_structure['types'])
                ]
                writer.writerow(schema_info)
                # Сохраняем заголовки и данные
                writer.writerow(self.table_structure['columns'])
                writer.writerows(self._records)
        except OSError as e:
            raise OSError(f'Ошибка при сохранении файла {self.path}: {e}')

    def load(self) -> None:
        try:
            if not os.path.exists(self.path):
                self.save()
                return

        with open(self.path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)

                try:
                    schema_info = next(reader)
                    if schema_info[0] == 'SCHEMA':
                        saved_columns = schema_info[1].split(',')
                        saved_types = schema_info[2].split(',')

                        if saved_columns != self.table_structure['columns']:
                            raise KeyError(
                                f'Заголовки таблицы некорректны: ожидались {self.table_structure["columns"]}, получены {saved_columns}')

                        if saved_types != self.table_structure['types']:
                            raise TypeError(
                                f'Типы данных некорректны: ожидались {self.table_structure["types"]}, получены {saved_types}')

                        headers = next(reader)
                    else:
                        headers = schema_info

                except StopIteration:
                    raise ValueError(f'Файл {self.path} пуст или имеет неверный формат')

                self._records.clear()
                for row in reader:
                    try:
                        record = (
                            int(row[0]),
                            row[1],
                            row[2],
                            int(row[3]),
                            row[4]
                        )
                        self._records.append(record)
                    except (ValueError, IndexError) as e:
                        raise ValueError(f'Ошибка формата данных в строке {row}: {e}')

        except OSError as e:
            raise OSError(f'Ошибка при чтении файла {self.path}: {e}')

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