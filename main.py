from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QGridLayout, QLineEdit, QPushButton, QComboBox, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QToolBar, QStatusBar, QMessageBox
import sys, os
from dotenv import load_dotenv
import pymysql

load_dotenv()
my_password = os.getenv("MYSQLPASSWORD")

class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password=my_password, database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        try:
            connection = pymysql.connect(host=self.host, user=self.user,
                                                 password=self.password, database=self.database)
            print("Connection Successful!")
            with connection.cursor() as cursor: # testing
                cursor.execute("SELECT DATABASE();")
                result = cursor.fetchall()
                print("You're connected to database:", result)
            return connection
        except pymysql.Error as err:
            print(f"Error: {err}")
            return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # create menubar
        file_menu_item = self.menuBar().addMenu("File")
        help_menu_item = self.menuBar().addMenu("Help")
        search_menu_item = self.menuBar().addMenu("Search")

        # create actions for each menu items

        # actions for file menu item
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        file_menu_item.addAction(add_student_action)
        add_student_action.triggered.connect(self.insert)

        # actions for help menu item
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # actions for edit menu item
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # create table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone No."))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # create toolbar and toolbar element
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # create statusbar and add statusbar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        results = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table.insertRow(row_number)
            for column_number, column_data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(column_data)))
        cursor.close()
        connection.close()

    def cell_clicked(self): # this function dynamically adds buttons/widgets to the statusbar when a cell is clicked
        # create edit button in the statusbar
        edit_button = QPushButton("Edit Data")
        edit_button.clicked.connect(self.edit)

        # create delete button in the statusbar
        delete_button = QPushButton("Delete Data")
        delete_button.clicked.connect(self.delete)

        # find if there are already any existing button in the statusbar
        children = self.findChildren(QPushButton)
        # delete pre-existing buttons from the statusbar before adding the new ones
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        # add button to the statusbar
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedSize(300, 280)

        layout = QVBoxLayout()

        # add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter Name")
        layout.addWidget(self.student_name)

        # add course list widget
        self.course_name = QComboBox()
        courses = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile No.")
        layout.addWidget(self.mobile)

        # add submit button
        button = QPushButton("Submit")
        layout.addWidget(button)
        button.clicked.connect(self.add_student)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name,course,mobile) VALUES (%s,%s,%s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()
        self.close()

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student Data")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        layout.addWidget(button)
        button.clicked.connect(self.search_data)

        self.setLayout(layout)

    def search_data(self):
        name = self.student_name.text().strip()
        # Connect to database
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        # Query the database
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        rows = cursor.fetchall()

        # Highlight matching rows in the table
        items = window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            row = item.row()
            for col in range(window.table.columnCount()):
                window.table.item(row, col).setSelected(True)

        # Debug print
        print(rows)
        cursor.close()
        connection.close()
        self.close()

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedSize(300, 280)

        layout = QVBoxLayout()

        # get data from the selected cell of the table
        index = window.table.currentRow()
        self.student_id = window.table.item(index, 0).text()

        # add student name widget
        wrong_student_name = window.table.item(index, 1).text()
        self.student_name = QLineEdit(wrong_student_name)
        self.student_name.setPlaceholderText("Enter Name")
        layout.addWidget(self.student_name)

        # add course list widget
        wrong_course_name = window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(wrong_course_name)
        layout.addWidget(self.course_name)

        # add mobile widget
        wrong_mobile_no = window.table.item(index, 3).text()
        self.mobile = QLineEdit(wrong_mobile_no)
        self.mobile.setPlaceholderText("Mobile No.")
        layout.addWidget(self.mobile)

        # add submit button
        button = QPushButton("Submit")
        layout.addWidget(button)
        button.clicked.connect(self.edit_data)

        self.setLayout(layout)

    def edit_data(self):
        correct_name = self.student_name.text()
        correct_course = self.course_name.itemText(self.course_name.currentIndex())
        correct_mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name=%s, course=%s, mobile=%s WHERE id=%s",
                       (correct_name, correct_course, correct_mobile, self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()
        self.close()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        # get data from the selected cell of the table
        index = window.table.currentRow()
        self.student_id = window.table.item(index, 0).text()

        layout = QGridLayout()

        warning_statement = QLabel("Are you sure you want to delete this data?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(warning_statement, 0, 0, 1, 4)
        layout.addWidget(yes, 1, 1)
        layout.addWidget(no, 1, 2)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_data)
        no.clicked.connect(self.close_dialog)

    def delete_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (self.student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was successfully deleted.")
        confirmation_widget.exec()

    def close_dialog(self):
        self.close()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This application was created during the course "The Python Mega Course".
        Feel free to modify and reuse this app.
        """
        self.setText(content)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.load_data()
    window.show()
    sys.exit(app.exec())