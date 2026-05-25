import unittest
from src.db.backend.memory import StudentTable


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


if __name__ == "__main__":
    unittest.main()
