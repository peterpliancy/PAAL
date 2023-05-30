import sys
import os
import datetime
import shutil
import csv
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PAAL')

        layout = QVBoxLayout()

        self.label = QLabel('Client Code')
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.text_line = QLineEdit()
        layout.addWidget(self.text_line)

        self.manual_select_label = QLabel('Manually Select A CSV')
        self.manual_select_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.manual_select_label)

        self.service_requirements = {
            "365 AutoPilot": ["Profile status", "Purchase order"],
            "365 AzureAD": ["registeredOwners", "joinType (trustType)"],
            "365 Endpoint": ["EAS activation ID", "EAS activated"],
            "Addigy Devices": ["Activation Lock Enabled", "Addigy Splashtop Installed"],
            "ScreenConnect": ["HostDurationSeconds", "GuestInfoUpdateTime"],
            "SentinelOne Applications": ["Base Score", "Days From CVE Detection"],
            "SentinelOne Sentinels (Full)": ["Subscribed On", "Management Connectivity"],
        }

        self.buttons = {}

        for service, requirements in self.service_requirements.items():
            btn = QPushButton(service)
            btn.setProperty("service", service)
            btn.clicked.connect(self.select_csv)
            btn.setFixedHeight(30)  # Set fixed button height
            btn.setFocusPolicy(Qt.NoFocus)  # Remove focus indication
            layout.addWidget(btn)
            self.buttons[service] = btn

        self.auto_search_label = QLabel('Automatically Find The Correct CSVs')
        self.auto_search_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.auto_search_label)

        self.auto_search_btn = QPushButton('Auto Search')
        self.auto_search_btn.clicked.connect(self.auto_select_csvs)
        layout.addWidget(self.auto_search_btn)

        self.auto_audit_label = QLabel('Process And Audit All Selected Services')
        self.auto_audit_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.auto_audit_label)

        self.auto_audit_btn = QPushButton('Auto Audit')
        self.auto_audit_btn.clicked.connect(self.process_selection)
        layout.addWidget(self.auto_audit_btn)

        self.reset_btn = QPushButton('Reset')
        self.reset_btn.clicked.connect(self.reset)
        self.reset_btn.setFixedHeight(30)
        self.reset_btn.setFocusPolicy(Qt.NoFocus)
        self.reset_btn.hide()
        layout.addWidget(self.reset_btn)

        self.setLayout(layout)

        self.selected_files = {}
        self.client_code = ""

    def select_csv(self):
        service = self.sender().property("service")
        requirements = self.service_requirements.get(service, [])

        default_dir = os.path.expanduser("~/Downloads")
        file_path, _ = QFileDialog.getOpenFileName(self, f'Select {service} CSV', default_dir, 'CSV(*.csv)')
        if file_path:
            if self.validate_csv(file_path, requirements):
                self.process_file(service, file_path)
            else:
                QMessageBox.warning(self, "Invalid CSV File",
                                    "The selected file does not meet the requirements. If you suspect there is an error with the application, please contact the PAAL admin!")

    def process_file(self, service, file_path):
        self.buttons[service].setStyleSheet('background-color: #7F4BAE; color: white')
        self.selected_files[service] = file_path

        now = datetime.datetime.now().strftime('%m-%d-%Y')
        desktop_path = os.path.expanduser("~/Desktop")
        paal_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress")
        service_folder = os.path.join(paal_path, service)
        os.makedirs(service_folder, exist_ok=True)
        new_file_name = f"{service} - Original - {now}.csv"
        new_file_path = os.path.join(service_folder, new_file_name)
        shutil.copy(file_path, new_file_path)

        self.reset_btn.show()  # Show the Reset button after any file is selected

        print(f"File selected for {service}: {file_path}")
        print(f"File copied to: {new_file_path}")

    def validate_csv(self, file_path, requirements):
        try:
            with open(file_path, "r") as csv_file:
                reader = csv.reader(csv_file)
                headers = next(reader)
                return all(column in headers for column in requirements)
        except Exception as e:
            print(f"Error while reading CSV file: {e}")
            return False

    def auto_select_csvs(self):
        default_dir = os.path.expanduser("~/Downloads")
        now = datetime.datetime.now()

        for service, requirements in self.service_requirements.items():
            files = []
            for file in os.listdir(default_dir):
                file_path = os.path.join(default_dir, file)
                if os.path.isfile(file_path) and file.lower().endswith(".csv"):
                    created_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                    if created_time >= now - datetime.timedelta(days=2):
                        if self.validate_csv(file_path, requirements):
                            files.append((file_path, created_time))

            if files:
                files.sort(key=lambda x: x[1], reverse=True)
                file_path = files[0][0]
                self.process_file(service, file_path)

        if not self.selected_files:
            QMessageBox.information(self, "Auto Search", "No files found.")
        else:
            QMessageBox.information(self, "Auto Search", "All original CSVs are ready to be audited!")

        print("Auto search completed!")

    def process_selection(self):
        if self.selected_files:
            script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "scripts", "Auto_Audit_scripts_button.py")

            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, cwd=os.path.dirname(os.path.realpath(__file__)))

            if result.returncode != 0:
                print(f"Error while running script: {result.stderr}")
                QMessageBox.warning(self, "Script Error", f"An error occurred while running the script: {result.stderr}")
                return

            self.client_code = self.text_line.text().strip()
            now = datetime.datetime.now().strftime('%m-%d-%Y')
            desktop_path = os.path.expanduser("~/Desktop")
            paal_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress")

            new_folder_name = f"Audit - {now}"
            if self.client_code:
                new_folder_name = f"{self.client_code} - {new_folder_name}"
            new_folder_path = os.path.join(os.path.dirname(paal_path), new_folder_name)

            counter = 2
            while os.path.exists(new_folder_path):
                new_folder_name_with_counter = f"{new_folder_name} ({counter})"
                new_folder_path = os.path.join(os.path.dirname(paal_path), new_folder_name_with_counter)
                counter += 1

            try:
                os.rename(paal_path, new_folder_path)
                QMessageBox.information(self, "Auto Audit", "All Done! Please inspect the PAAL folder on your Desktop to see the results!")
            except OSError as e:
                print(f"Error while renaming folder: {e}")
                QMessageBox.warning(self, "Folder Rename Error", f"An error occurred while renaming the folder: {e}")

        else:
            QMessageBox.warning(self, "Auto Audit", "No services are selected.")

    def reset(self):
        for service in self.service_requirements.keys():
            self.buttons[service].setStyleSheet('')
        self.selected_files = {}
        self.reset_btn.hide()
        self.text_line.clear()

        # Deleting the "PAAL in Progress" folder when reset button is pressed
        desktop_path = os.path.expanduser("~/Desktop")
        paal_in_progress_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress")
        try:
            if os.path.exists(paal_in_progress_path):
                shutil.rmtree(paal_in_progress_path)
        except OSError as e:
            print(f"Error while deleting folder: {e}")


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
