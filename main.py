import subprocess
import os
import platform
import datetime
from win10toast_click import ToastNotifier

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import sv_ttk

notifier = ToastNotifier()


def log(message: str, level: str = "info") -> None:
    """
    Writes a message to the log.log file
    :param message: The message to write
    :param level: The level ("warning" and "critical" change colors)
    :return: None
    """

    with open("log.log", "a") as fh:
        output = f"{datetime.datetime.now()} | {level.lower()} | {message}\n"

        if level.lower() == "warning":
            output = "\033[93m" + output + "\033[0m"
        elif level.lower() == "critical":
            output = "\033[91m" + output + "\033[0m"

        fh.write(output)


def check_file_exists(path: str) -> bool:
    """
    Check that a file exists
    :param path: The file path to check exists
    :return: True if the file exists, otherwise False
    """
    return os.path.exists(path)


def check_pip_installed() -> bool:
    """
    Check if pip is installed and accessible
    :return: True if pip is present, otherwise False
    """
    return subprocess.check_output("python -m pip --version").decode("utf-8").startswith("pip")


class Application(tk.Frame):

    def __init__(self, master=None) -> None:
        """
        Initialise the application
        :param master: I don't actually know what this does, but it's necessary.
        """
        # tkinter setup
        super().__init__()
        self.master = master
        self.grid()
        self.winfo_toplevel().title("Python Compiler")

        # check pip is installed
        if not check_pip_installed():
            log("PIP not installed, refused to run.", "critical")
            messagebox.showerror("PIP not found", "Could not find a version of PIP installed on this machine.")
            exit(1)

        # check running on Windows
        if platform.system() != "Windows":
            log("Not running on windows, refused to run.", "critical")
            messagebox.showerror("OS Error",
                                 f"This program is not supported on your operating system ({platform.system()})")
            exit(1)

        # declare some important variables
        self.target_file = None
        self.target_directory = None
        self.show_console = tk.IntVar()
        self.one_file_mode = tk.IntVar()

        self.create_widgets()

    def create_widgets(self) -> None:
        """
        Creates the UI elements in the application
        :return: None
        """

        self.file_label = ttk.Label(self, width=13, justify=tk.LEFT)
        self.file_label.grid(row=1, column=1)
        self.file_label["text"] = "Launcher:"

        self.file_choose_button = ttk.Button(self)
        self.file_choose_button.grid(row=1, column=2, sticky="e")
        self.file_choose_button["text"] = "Browse..."
        self.file_choose_button["command"] = self.choose_file

        self.requirements_label = ttk.Label(self, width=13, justify=tk.LEFT)
        self.requirements_label.grid(row=2, column=1)
        self.requirements_label["text"] = "Requirements: "

        self.create_requirements_btn = ttk.Button(self)
        self.create_requirements_btn.grid(row=2, column=2, sticky="e")
        self.create_requirements_btn["text"] = "Awaiting launcher..."

        self.windowed_label = ttk.Label(self, width=13, justify=tk.LEFT)
        self.windowed_label.grid(row=3, column=1)
        self.windowed_label["text"] = "Show console?"

        self.windowed_selector = ttk.Checkbutton(self, variable=self.show_console)
        self.windowed_selector.grid(row=3, column=2, sticky="e")

        self.one_file_label = ttk.Label(self, width=13, justify=tk.LEFT)
        self.one_file_label.grid(row=4, column=1)
        self.one_file_label["text"] = "One file?"

        self.onefile_selector = ttk.Checkbutton(self, variable=self.one_file_mode)
        self.onefile_selector.grid(row=4, column=2, sticky="e")

        self.go_btn = ttk.Button(self)
        self.go_btn.grid(row=5, column=1, columnspan=2)
        self.go_btn["text"] = "Compile"
        self.go_btn["command"] = self.compile

    def choose_file(self) -> None:
        """
        Set the launcher file by opening a file choose dialogue, then check requirements file validity.
        :return: None
        """

        self.target_file = askopenfilename().replace("\\", "/")
        self.target_directory = os.path.split(self.target_file)[0]

        self.file_choose_button["text"] = self.target_file

        self.check_requirements()

    def check_requirements(self) -> bool:
        """
        Check for the existence of a requirements file and update the UI accordingly
        :return: True if a requirements file exists, otherwise False
        """
        requirements_path = self.target_directory + "/requirements.txt"

        if check_file_exists(requirements_path):
            self.create_requirements_btn["text"] = "[...]/requirements.txt"
            return True
        else:
            self.create_requirements_btn["text"] = "Create"

            return False

    def create_requirements(self) -> None:
        """
        Opens the requirements file (creates one if none is present)
        :return: None
        """

        if self.target_directory is None:
            messagebox.showerror('Sequence Error', 'Error: Please specify a launcher script first.')

        # create the file
        requirements_path = self.target_directory.replace("\\", "/") + "/requirements.txt"
        if not os.path.exists(requirements_path):
            log(f"Created requirements at {requirements_path}")
            with open(requirements_path, "w") as fh:
                fh.write(
                    """This is the requirements file. 
                    
You should delete all text in this file and replace it with any modules you need installed. 
Save and close the file when you are finished.

Examples:
speedtest-cli (plain install for latest version of speedtest-cli)
speedtest-cli==2.1.3 (installs speedtest-cli version 2.1.3)
speedtest_cli>2.0.2 (installs any version of speedtest-cli after 2.0.2)
speedtest_cli>2.0.2,<2.1.2 (installs any version of speedtest-cli between 2.0.2 and 2.1.2 non-inclusive)
                    """
                )

        os.system(f"notepad {requirements_path}")

        self.check_requirements()

    def compile(self) -> None:
        """
        Constructs a command based on parameters and attempts to compile the program
        :return: None
        """

        if self.target_file is None:
            messagebox.showerror("Launcher Not Found", "Your program was not compiled.\n"
                                                       "Please choose a launcher file before compiling.")
            return

        if not check_file_exists(self.target_directory + "/requirements.txt"):
            messagebox.showerror("Requirements Not Found", "Your program was not compiled.\n"
                                                           "Please create a requirements file before compiling.")
            self.check_requirements()
            return

        log(f"Compiling program at {self.target_file}\n\tParameters:"
            f"\n\tOne file: {self.one_file_mode.get()}"
            f"\n\tShow console: {self.show_console.get()}")

        command = "pyinstaller "
        if self.one_file_mode.get() == 1:
            command += "--onefile "
        if not self.show_console.get() == 1:
            command += "-w "

        command += self.target_file

        messagebox.showinfo("Ready to compile", f"Click \"OK\" to compile with the following parameters:"
                                                f"\n\tFile: {self.target_file}"
                                                f"\n\tOne file: {self.one_file_mode.get()}"
                                                f"\n\tShow console: {self.show_console.get()}")
        os.system(command)
        notifier.show_toast(
            "Compiled!",
            "Click here to view output.",
            duration=20,
            threaded=True,
            callback_on_click=self.show_output_location
        )

    def show_output_location(self):
        print(self.target_directory)
        path = self.target_directory.replace('/', '\\') + "\\dist"
        os.system(f"explorer \"{path}\"")


def main() -> None:
    log("Startup")

    root = tk.Tk()
    try:
        sv_ttk.set_theme("light")
    except:
        log("Could not load themes", "warning")
    app = Application(root)
    app.mainloop()


if __name__ == "__main__":
    main()
