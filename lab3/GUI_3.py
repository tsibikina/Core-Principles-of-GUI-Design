import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTabWidget, QComboBox,
                             QTableWidget, QTableWidgetItem, QMessageBox, QLabel,
                             QLineEdit, QFileDialog)
from PyQt5.QtCore import Qt


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.current_db_path = None

    def connect(self, db_path):
        try:
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
            self.current_db_path = db_path
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            self.current_db_path = None

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall(), [description[0] for description in self.cursor.description]
            else:
                self.connection.commit()
                return None, None
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return None, None

    def get_table_names(self):
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting table names: {e}")
            return []

    def get_table_columns(self, table_name):
        """Get all column names for a specific table"""
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return [row[1] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting columns for table {table_name}: {e}")
            return []

    def get_all_columns_from_all_tables(self):
        """Get all columns from all tables for the combo box"""
        try:
            tables = self.get_table_names()
            all_columns = []

            for table in tables:
                if table != 'sqlite_sequence':  # Skip internal table
                    columns = self.get_table_columns(table)
                    for column in columns:
                        all_columns.append(f"{table}.{column}")

            return all_columns
        except sqlite3.Error as e:
            print(f"Error getting all columns: {e}")
            return []


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SQL Database Browser')
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Menu section
        menu_layout = QHBoxLayout()

        # Connection buttons
        self.connect_btn = QPushButton('Set connection')
        self.connect_btn.clicked.connect(self.set_connection)

        self.close_btn = QPushButton('Close connection')
        self.close_btn.clicked.connect(self.close_connection)
        self.close_btn.setEnabled(False)

        # Database info label
        self.db_info_label = QLabel('No database connected')
        self.db_info_label.setStyleSheet('color: gray; font-style: italic;')

        # Query buttons and combo box
        self.bt1 = QPushButton('Show Table Names')
        self.bt1.clicked.connect(self.execute_select_column)
        self.bt1.setEnabled(False)

        self.columns_combo = QComboBox()
        self.columns_combo.setEnabled(False)
        self.columns_combo.currentTextChanged.connect(self.on_column_selected)

        self.bt2 = QPushButton('Show Tables Data')
        self.bt2.clicked.connect(self.execute_query2)
        self.bt2.setEnabled(False)

        self.bt3 = QPushButton('Show Table Info')
        self.bt3.clicked.connect(self.execute_query3)
        self.bt3.setEnabled(False)

        # Add widgets to menu layout
        menu_layout.addWidget(self.connect_btn)
        menu_layout.addWidget(self.close_btn)
        menu_layout.addWidget(self.bt1)
        menu_layout.addWidget(self.columns_combo)
        menu_layout.addWidget(self.bt2)
        menu_layout.addWidget(self.bt3)
        menu_layout.addWidget(self.db_info_label)
        menu_layout.addStretch()

        # Tab widget
        self.tab_widget = QTabWidget()

        # Create tabs
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()

        # Initialize tab layouts
        self.init_tab1()
        self.init_tab2()
        self.init_tab3()
        self.init_tab4()
        self.init_tab5()

        # Add tabs to tab widget
        self.tab_widget.addTab(self.tab1, "Database Schema")
        self.tab_widget.addTab(self.tab2, "Table Names")
        self.tab_widget.addTab(self.tab3, "Column Data")
        self.tab_widget.addTab(self.tab4, "Tables Data")
        self.tab_widget.addTab(self.tab5, "Table Structure")

        # Add layouts to main layout
        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.tab_widget)

    def init_tab1(self):
        layout = QVBoxLayout(self.tab1)
        self.table1 = QTableWidget()
        layout.addWidget(self.table1)

    def init_tab2(self):
        layout = QVBoxLayout(self.tab2)
        self.table2 = QTableWidget()
        layout.addWidget(self.table2)

    def init_tab3(self):
        layout = QVBoxLayout(self.tab3)
        self.table3 = QTableWidget()
        layout.addWidget(self.table3)

    def init_tab4(self):
        layout = QVBoxLayout(self.tab4)
        self.table4 = QTableWidget()
        layout.addWidget(self.table4)

    def init_tab5(self):
        layout = QVBoxLayout(self.tab5)
        self.table5 = QTableWidget()
        layout.addWidget(self.table5)

    def set_connection(self):
        db_path, _ = QFileDialog.getOpenFileName(
            self, 'Open SQLite Database', '', 'SQLite Databases (*.db *.sqlite *.sqlite3)')

        if db_path:
            if self.db_manager.connect(db_path):
                self.connect_btn.setEnabled(False)
                self.close_btn.setEnabled(True)
                self.bt1.setEnabled(True)
                self.bt2.setEnabled(True)
                self.bt3.setEnabled(True)

                # Update database info
                self.db_info_label.setText(f'Connected: {db_path.split("/")[-1]}')
                self.db_info_label.setStyleSheet('color: green; font-weight: bold;')

                # Execute initial query and display in Tab1
                self.execute_initial_query()

                # Populate columns combo box with all columns from all tables
                self.populate_columns_combo()

                QMessageBox.information(self, 'Success', 'Database connection established successfully!')
            else:
                QMessageBox.critical(self, 'Error', 'Failed to connect to database!')

    def close_connection(self):
        self.db_manager.close()
        self.connect_btn.setEnabled(True)
        self.close_btn.setEnabled(False)
        self.bt1.setEnabled(False)
        self.columns_combo.setEnabled(False)
        self.bt2.setEnabled(False)
        self.bt3.setEnabled(False)

        # Update database info
        self.db_info_label.setText('No database connected')
        self.db_info_label.setStyleSheet('color: gray; font-style: italic;')

        # Clear all tables
        for table in [self.table1, self.table2, self.table3, self.table4, self.table5]:
            table.setRowCount(0)
            table.setColumnCount(0)

        # Clear combo box
        self.columns_combo.clear()

        QMessageBox.information(self, 'Info', 'Database connection closed!')

    def execute_initial_query(self):
        """Execute SELECT * FROM sqlite_master and display in Tab1"""
        query = "SELECT * FROM sqlite_master"
        data, headers = self.db_manager.execute_query(query)

        if data and headers:
            self.display_data_in_table(self.table1, data, headers)
            self.tab_widget.setTabText(0, f"Database Schema ({len(data)} objects)")

    def execute_select_column(self):
        """Execute SELECT name FROM sqlite_master and display in Tab2"""
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        data, headers = self.db_manager.execute_query(query)

        if data and headers:
            self.display_data_in_table(self.table2, data, headers)
            self.tab_widget.setTabText(1, f"Table Names ({len(data)} tables)")

    def on_column_selected(self, column_info):
        """Execute query based on selected column and display in Tab3"""
        # Ignore the placeholder item and empty selections
        if not column_info or column_info == "-- Select a column --" or not self.db_manager.connection:
            self.table3.setRowCount(0)
            self.table3.setColumnCount(0)
            self.tab_widget.setTabText(2, "Column Data")
            return

        try:
            # Parse table and column name from format "table.column"
            if '.' in column_info:
                table_name, column_name = column_info.split('.', 1)  # Split only on first dot

                # Execute query to get data from the selected column
                query = f"SELECT {column_name} FROM {table_name}"
                data, headers = self.db_manager.execute_query(query)

                if data and headers:
                    self.display_data_in_table(self.table3, data, headers)
                    self.tab_widget.setTabText(2, f"Column: {column_info}")
                else:
                    # Clear table if no data
                    self.table3.setRowCount(0)
                    self.table3.setColumnCount(0)
                    self.tab_widget.setTabText(2, f"Column: {column_info} - No results")

            else:
                # If format is incorrect, show error
                self.table3.setRowCount(0)
                self.table3.setColumnCount(0)
                self.tab_widget.setTabText(2, "Column Data - Invalid format")

        except Exception as e:
            QMessageBox.warning(self, 'Query Error', f'Error executing query: {str(e)}')
            self.table3.setRowCount(0)
            self.table3.setColumnCount(0)
            self.tab_widget.setTabText(2, "Column Data - Error")

    def execute_query2(self):
        """Show data from all tables in Tab4"""
        if self.db_manager.connection:
            # Get all table names
            tables = self.db_manager.get_table_names()
            all_data = []
            all_headers = []

            for table in tables:
                if table != 'sqlite_sequence':  # Skip internal table
                    query = f"SELECT * FROM {table} LIMIT 10"  # Limit to 10 rows per table
                    data, headers = self.db_manager.execute_query(query)

                    if data and headers:
                        # Add separator row with table name
                        if all_data:
                            # Add separator before new table
                            separator_row = ['---'] * len(headers)
                            all_data.append(separator_row)
                            # Add table name row
                            table_name_row = [f"📊 Table: {table}"] + [''] * (len(headers) - 1)
                            all_data.append(table_name_row)
                            separator_row = ['---'] * len(headers)
                            all_data.append(separator_row)
                        else:
                            # For first table, set headers
                            all_headers = headers

                        # Add the actual data
                        all_data.extend(data)

            if all_data:
                self.display_data_in_table(self.table4, all_data, all_headers)
                self.tab_widget.setTabText(3, "Tables Data")
            else:
                self.table4.setRowCount(0)
                self.table4.setColumnCount(0)
                self.tab_widget.setTabText(3, "Tables Data - No data")

    def execute_query3(self):
        """Show table structure information in Tab5"""
        if self.db_manager.connection:
            query = """
            SELECT m.name as table_name, 
                   p.name as column_name, 
                   p.type as data_type,
                   p."notnull" as not_null,
                   p.dflt_value as default_value,
                   p.pk as primary_key
            FROM sqlite_master m
            JOIN pragma_table_info(m.name) p
            WHERE m.type = 'table'
            ORDER BY m.name, p.cid
            """
            data, headers = self.db_manager.execute_query(query)

            if data and headers:
                self.display_data_in_table(self.table5, data, headers)
                self.tab_widget.setTabText(4, f"Table Structure ({len(data)} columns)")
            else:
                self.table5.setRowCount(0)
                self.table5.setColumnCount(0)
                self.tab_widget.setTabText(4, "Table Structure - No data")

    def populate_columns_combo(self):
        """Populate combo box with all columns from all tables"""
        if self.db_manager.connection:
            all_columns = self.db_manager.get_all_columns_from_all_tables()

            if all_columns:
                self.columns_combo.clear()
                self.columns_combo.setEnabled(True)

                # Add a default placeholder
                self.columns_combo.addItem("-- Select a column --")

                # Add all columns in format "table.column"
                for column_info in sorted(all_columns):
                    self.columns_combo.addItem(column_info)

                print(f'Loaded {len(all_columns)} columns from database')
            else:
                self.columns_combo.clear()
                self.columns_combo.setEnabled(False)
                self.columns_combo.addItem("No columns found")

    def display_data_in_table(self, table_widget, data, headers):
        """Display query results in a table widget"""
        try:
            table_widget.setRowCount(len(data))
            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)

            for row_idx, row_data in enumerate(data):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data) if cell_data is not None else 'NULL')
                    table_widget.setItem(row_idx, col_idx, item)

            table_widget.resizeColumnsToContents()
        except Exception as e:
            print(f"Error displaying data in table: {e}")


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()