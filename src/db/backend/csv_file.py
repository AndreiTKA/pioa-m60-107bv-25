import csv
from src.db.backend.memory import StudentTable


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