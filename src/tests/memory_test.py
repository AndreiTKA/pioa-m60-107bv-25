import unittest, tempfile, os, json, csv
from src.db.backend.memory import StudentTable, JsonStudentTable, CsvStudentTable


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.student_table = StudentTable()
        self.assertIsInstance(self.student_table, StudentTable)

    def test_create(self):
        cases = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]
        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.student_table.create(*test_data)
                self.assertEqual(record, test_data)

    def test_create_negative_age(self):
        cases = [
            (1, "John", "Doe", -1, "M"),
            (2, "Jane", "Smith", -5, "F"),
            (3, "Alice", "Johnson", -10, "F"),
        ]
        error_message = "Поле age не может быть отрицательным."
        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(ValueError) as context:
                    self.student_table.create(*test_data)
                self.assertEqual(str(context.exception), error_message)

    def test_create_duplicate_id(self):
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        self.student_table.create(*test_data_1)

        with self.assertRaises(ValueError) as context:
            self.student_table.create(*test_data_2)
        self.assertIn("Запись с id=1 уже существует.", str(context.exception))

    def test_select(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
        ]
        for data in test_datas:
            self.student_table.create(*data)

        cases = [
            {
                "name": "Выбор без фильтров (filters=None)",
                "filters": None,
                "expected": test_datas,
            },
            {
                "name": "Выбор без фильтров (пустой словарь)",
                "filters": {},
                "expected": test_datas,
            },
            {
                "name": "Фильтр по ID",
                "filters": {"id": 1},
                "expected": [test_datas[0]],
            },
            {
                "name": "Фильтр по имени",
                "filters": {"first_name": "Jane"},
                "expected": [test_datas[1]],
            },
            {
                "name": "Фильтр по фамилии",
                "filters": {"second_name": "Johnson"},
                "expected": [test_datas[2]],
            },
            {
                "name": "Фильтр по возрасту",
                "filters": {"age": 20},
                "expected": [test_datas[0], test_datas[6]],
            },
            {
                "name": "Фильтр по полу",
                "filters": {"sex": "F"},
                "expected": [
                    test_datas[1],
                    test_datas[2],
                    test_datas[5],
                    test_datas[7],
                    test_datas[9],
                ],
            },
            {
                "name": "Комбинированный фильтр",
                "filters": {"first_name": "Alice", "sex": "F"},
                "expected": [test_datas[2]],
            },
        ]

        for case in cases:
            with self.subTest(name=case["name"]):
                result = self.student_table.select(case["filters"])
                self.assertEqual(result, case["expected"])

    def test_update_success(self):
        self.student_table.create(1, "John", "Doe", 20, "M")
        self.student_table.create(2, "Jane", "Smith", 22, "F")
        self.student_table.create(3, "Alice", "Johnson", 19, "F")

        updated = self.student_table.update(
            {"first_name": "Jane"}, {"age": 23}
        )
        self.assertEqual(updated, 1)
        records = self.student_table.select({"id": 2})
        self.assertEqual(records[0], (2, "Jane", "Smith", 23, "F"))

    def test_update_multiple_fields(self):
        self.student_table.create(1, "John", "Doe", 20, "M")
        self.student_table.update(
            {"id": 1},
            {"first_name": "Jonathan", "second_name": "Dorian", "age": 21, "sex": "M"}
        )
        record = self.student_table.select({"id": 1})
        self.assertEqual(record[0], (1, "Jonathan", "Dorian", 21, "M"))

    def test_update_empty_filters_raises(self):
        with self.assertRaises(ValueError) as context:
            self.student_table.update({}, {"age": 30})
        self.assertEqual(
            str(context.exception),
            "Не заданы фильтры для обновления. Обновление всех записей запрещено."
        )

    def test_update_id_field_raises(self):
        self.student_table.create(1, "John", "Doe", 20, "M")
        with self.assertRaises(ValueError) as context:
            self.student_table.update({"id": 1}, {"id": 2})
        self.assertEqual(str(context.exception), "Поле id нельзя изменять.")

    def test_update_negative_age_raises(self):
        self.student_table.create(1, "John", "Doe", 20, "M")
        with self.assertRaises(ValueError) as context:
            self.student_table.update({"id": 1}, {"age": -5})
        self.assertEqual(str(context.exception), "Поле age не может быть отрицательным.")

    def test_update_no_matching_records_raises(self):
        self.student_table.create(1, "John", "Doe", 20, "M")
        with self.assertRaises(ValueError) as context:
            self.student_table.update({"first_name": "Nonexistent"}, {"age": 30})
        self.assertEqual(
            str(context.exception),
            "Не найдено записей, соответствующих фильтрам."
        )
    def test_delete_success(self):
        self.student_table.create(1, "John", "Doe", 20, "M")
        self.student_table.create(2, "Jane", "Smith", 22, "F")
        self.student_table.create(3, "Alice", "Johnson", 19, "F")

        deleted = self.student_table.delete({"sex": "F"})
        self.assertEqual(deleted, 2)
        remaining = self.student_table.select()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0], (1, "John", "Doe", 20, "M"))

    def test_delete_empty_filters_raises(self):
        with self.assertRaises(ValueError) as context:
            self.student_table.delete({})
        self.assertEqual(
            str(context.exception),
            "Не заданы фильтры для удаления. Удаление всех записей запрещено."
        )

    def test_delete_no_matching_records_raises(self):
        self.student_table.create(1, "John", "Doe", 20, "M")
        with self.assertRaises(ValueError) as context:
            self.student_table.delete({"first_name": "Nonexistent"})
        self.assertEqual(
            str(context.exception),
            "Не найдено записей, соответствующих фильтрам."
        )


class TestJsonStudentTable(unittest.TestCase):
    def setUp(self):
        self.json_table = JsonStudentTable()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_students.json")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_inheritance(self):
        self.assertIsInstance(self.json_table, StudentTable)
        self.assertIsInstance(self.json_table, JsonStudentTable)

    def test_save_empty_table(self):
        self.json_table.save(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))

        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data, [])

    def test_save_and_load_single_record(self):
        test_record = (1, "John", "Doe", 20, "M")
        self.json_table.create(*test_record)

        self.json_table.save(self.test_file)

        new_table = JsonStudentTable()
        new_table.load(self.test_file)

        loaded_records = new_table.select()
        self.assertEqual(len(loaded_records), 1)
        self.assertEqual(loaded_records[0], test_record)

    def test_save_and_load_multiple_records(self):
        test_records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]

        for record in test_records:
            self.json_table.create(*record)

        self.json_table.save(self.test_file)

        with open(self.test_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        self.assertEqual(len(json_data), len(test_records))
        self.assertEqual(json_data[0]["id"], 1)
        self.assertEqual(json_data[0]["first_name"], "John")

        new_table = JsonStudentTable()
        new_table.load(self.test_file)

        loaded_records = new_table.select()
        self.assertEqual(len(loaded_records), len(test_records))
        self.assertEqual(loaded_records, test_records)

    def test_load_preserves_data_types(self):
        test_record = (1, "John", "Doe", 20, "M")
        self.json_table.create(*test_record)
        self.json_table.save(self.test_file)

        new_table = JsonStudentTable()
        new_table.load(self.test_file)

        loaded_record = new_table.select()[0]
        self.assertIsInstance(loaded_record[0], int)
        self.assertIsInstance(loaded_record[3], int)
        self.assertIsInstance(loaded_record[1], str)

    def test_load_clears_existing_data(self):
        self.json_table.create(1, "John", "Doe", 20, "M")

        other_table = JsonStudentTable()
        other_table.create(2, "Jane", "Smith", 22, "F")
        other_table.save(self.test_file)

        self.json_table.load(self.test_file)

        records = self.json_table.select()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], (2, "Jane", "Smith", 22, "F"))

    def test_json_file_format(self):
        """Тест проверки формата JSON файла"""
        self.json_table.create(1, "Иван", "Иванов", 20, "М")
        self.json_table.save(self.test_file)

        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("Иван", content)
        self.assertIn("Иванов", content)

        data = json.loads(content)
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["first_name"], "Иван")

    def test_save_overwrites_existing_file(self):
        self.json_table.create(1, "John", "Doe", 20, "M")
        self.json_table.save(self.test_file)

        self.json_table.create(2, "Jane", "Smith", 22, "F")
        self.json_table.save(self.test_file)

        new_table = JsonStudentTable()
        new_table.load(self.test_file)
        self.assertEqual(len(new_table.select()), 2)


class TestCsvStudentTable(unittest.TestCase):

    def setUp(self):
        self.csv_table = CsvStudentTable()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_students.csv")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_inheritance(self):
        self.assertIsInstance(self.csv_table, StudentTable)
        self.assertIsInstance(self.csv_table, CsvStudentTable)

    def test_save_empty_table(self):
        self.csv_table.save(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))

        with open(self.test_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], ["id", "first_name", "second_name", "age", "sex"])

    def test_save_and_load_single_record(self):
        test_record = (1, "John", "Doe", 20, "M")
        self.csv_table.create(*test_record)

        self.csv_table.save(self.test_file)

        new_table = CsvStudentTable()
        new_table.load(self.test_file)

        loaded_records = new_table.select()
        self.assertEqual(len(loaded_records), 1)
        self.assertEqual(loaded_records[0], test_record)

    def test_save_and_load_multiple_records(self):
        test_records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]

        for record in test_records:
            self.csv_table.create(*record)

        self.csv_table.save(self.test_file)

        with open(self.test_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0], ["id", "first_name", "second_name", "age", "sex"])

        new_table = CsvStudentTable()
        new_table.load(self.test_file)

        loaded_records = new_table.select()
        self.assertEqual(len(loaded_records), len(test_records))
        self.assertEqual(loaded_records, test_records)

    def test_load_preserves_data_types(self):
        test_record = (1, "John", "Doe", 20, "M")
        self.csv_table.create(*test_record)
        self.csv_table.save(self.test_file)

        new_table = CsvStudentTable()
        new_table.load(self.test_file)

        loaded_record = new_table.select()[0]
        self.assertIsInstance(loaded_record[0], int)
        self.assertIsInstance(loaded_record[3], int)
        self.assertIsInstance(loaded_record[1], str)

    def test_load_clears_existing_data(self):
        self.csv_table.create(1, "John", "Doe", 20, "M")

        other_table = CsvStudentTable()
        other_table.create(2, "Jane", "Smith", 22, "F")
        other_table.save(self.test_file)

        self.csv_table.load(self.test_file)

        records = self.csv_table.select()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], (2, "Jane", "Smith", 22, "F"))

    def test_csv_header_format(self):
        self.csv_table.create(1, "John", "Doe", 20, "M")
        self.csv_table.save(self.test_file)

        with open(self.test_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()

        self.assertEqual(first_line, "id,first_name,second_name,age,sex")

    def test_csv_with_special_characters(self):
        test_record = (1, "Mary-Jane", "O'Connor", 25, "F")
        self.csv_table.create(*test_record)
        self.csv_table.save(self.test_file)

        new_table = CsvStudentTable()
        new_table.load(self.test_file)

        loaded_records = new_table.select()
        self.assertEqual(len(loaded_records), 1)
        self.assertEqual(loaded_records[0], test_record)

    def test_save_overwrites_existing_file(self):
        self.csv_table.create(1, "John", "Doe", 20, "M")
        self.csv_table.save(self.test_file)

        self.csv_table.create(2, "Jane", "Smith", 22, "F")
        self.csv_table.save(self.test_file)

        new_table = CsvStudentTable()
        new_table.load(self.test_file)
        self.assertEqual(len(new_table.select()), 2)


if __name__ == "__main__":
    unittest.main()
