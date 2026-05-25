import unittest
from unittest.mock import patch
from io import StringIO
from src.db.tui import Tui


class TestTui(unittest.TestCase):
    def setUp(self):
        self.tui = Tui()

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=["1", "John", "Doe", "20", "M"])
    def test_add_student_success(self, mock_input, mock_stdout):
        self.tui._add_student()
        output = mock_stdout.getvalue()
        self.assertIn("Запись добавлена", output)
        records = self.tui._student_table.select()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], (1, "John", "Doe", 20, "M"))

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=["1", "Bad", "Guy", "-5", "M"])
    def test_add_student_negative_age(self, mock_input, mock_stdout):
        self.tui._add_student()
        output = mock_stdout.getvalue()
        self.assertIn("Ошибка: Поле age не может быть отрицательным.", output)
        self.assertEqual(len(self.tui._student_table.select()), 0)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=["1", "John", "Doe", "20", "M",
                                          "1", "Jane", "Smith", "22", "F"])
    def test_add_student_duplicate_id(self, mock_input, mock_stdout):
        self.tui._add_student()
        self.tui._add_student()
        output = mock_stdout.getvalue()
        self.assertIn("Ошибка: Запись с id=1 уже существует.", output)
        self.assertEqual(len(self.tui._student_table.select()), 1)

    @patch("sys.stdout", new_callable=StringIO)
    def test_show_all_students_empty(self, mock_stdout):
        self.tui._show_all_students()
        output = mock_stdout.getvalue()
        self.assertIn("Записи не найдены.", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_show_all_students_with_data(self, mock_stdout):
        self.tui._student_table.create(1, "Alice", "Wonder", 20, "F")
        self.tui._student_table.create(2, "Bob", "Builder", 22, "M")
        self.tui._show_all_students()
        output = mock_stdout.getvalue()
        self.assertIn("(1, 'Alice', 'Wonder', 20, 'F')", output)
        self.assertIn("(2, 'Bob', 'Builder', 22, 'M')", output)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=["", "Alice", "", "", ""])
    def test_select_by_first_name(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "Alice", "Wonder", 20, "F")
        self.tui._student_table.create(2, "Bob", "Builder", 22, "M")
        self.tui._select()
        output = mock_stdout.getvalue()
        self.assertIn("(1, 'Alice', 'Wonder', 20, 'F')", output)
        self.assertNotIn("Bob", output)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=["", "", "", "", ""])
    def test_select_all_empty_filters(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "Alice", "Wonder", 20, "F")
        self.tui._student_table.create(2, "Bob", "Builder", 22, "M")
        self.tui._select()
        output = mock_stdout.getvalue()
        self.assertIn("(1, 'Alice', 'Wonder', 20, 'F')", output)
        self.assertIn("(2, 'Bob', 'Builder', 22, 'M')", output)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=[
        "1", "", "", "", "",
        "y",
        "Alice", "", "30", "F"
    ])
    def test_update_success(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "John", "Doe", 20, "M")
        self.tui.update()
        output = mock_stdout.getvalue()
        self.assertIn("Успешно обновлено записей: 1", output)
        record = self.tui._student_table.select({"id": 1})[0]
        self.assertEqual(record, (1, "Alice", "Doe", 30, "F"))

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=[
        "", "", "", "", "",
        "y"
    ])
    def test_update_empty_filters(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "John", "Doe", 20, "M")
        self.tui.update()
        output = mock_stdout.getvalue()
        self.assertIn("Ошибка: необходимо указать хотя бы один фильтр.", output)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=[
        "1", "", "", "", "",
        "n"
    ])
    def test_update_cancel(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "John", "Doe", 20, "M")
        self.tui.update()
        output = mock_stdout.getvalue()
        self.assertIn("Обновление отменено.", output)
        record = self.tui._student_table.select({"id": 1})[0]
        self.assertEqual(record, (1, "John", "Doe", 20, "M"))

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=[
        "1", "", "", "", "",
        "y"
    ])
    def test_delete_success(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "John", "Doe", 20, "M")
        self.tui._delete()
        output = mock_stdout.getvalue()
        self.assertIn("Успешно удалено записей: 1", output)
        self.assertEqual(len(self.tui._student_table.select()), 0)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=[
        "", "", "", "", "",
        "y"
    ])
    def test_delete_empty_filters(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "John", "Doe", 20, "M")
        self.tui._delete()
        output = mock_stdout.getvalue()
        self.assertIn("Ошибка: необходимо указать хотя бы один фильтр.", output)
        self.assertEqual(len(self.tui._student_table.select()), 1)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=[
        "1", "", "", "", "",
        "n"
    ])
    def test_delete_cancel(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "John", "Doe", 20, "M")
        self.tui._delete()
        output = mock_stdout.getvalue()
        self.assertIn("Удаление отменено.", output)
        self.assertEqual(len(self.tui._student_table.select()), 1)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=["0"])
    def test_run_exit_immediately(self, mock_input, mock_stdout):
        self.tui.run()
        output = mock_stdout.getvalue()
        self.assertIn("Выход из программы.", output)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", side_effect=["2", "0"])
    def test_run_show_all_then_exit(self, mock_input, mock_stdout):
        self.tui._student_table.create(1, "Test", "User", 25, "M")
        self.tui.run()
        output = mock_stdout.getvalue()
        self.assertIn("(1, 'Test', 'User', 25, 'M')", output)
        self.assertIn("Выход из программы.", output)


if __name__ == "__main__":
    unittest.main()
