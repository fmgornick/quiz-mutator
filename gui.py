import os
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as msg
from tkinter import END
import tkinter.font as tkfont

END = "end-1c"

class GUI:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.file = None

        # main window
        self.root = tk.Tk()
        self.root.geometry(f'{self.width}x{self.height}')
        self.root.title("parsons / mutation quiz generator")
        self.root.focus_set()

        # menu bar and text area
        self.menu = tk.Menu(self.root, background='#ff8000')
        self.text = tk.Text(self.root, font=("Hack Nerd Font Mono", 12), undo=True)
        # self.text.grid(column=0, row=0, sticky="nsew")

# def about():
#     filewin = tk.Toplevel(root)
#     string = "this editor provides a graphical interface for creating parsons / mutation problems\n"
#     string += "output from this application currently only works for Canvas's QTI format and Moodle's Moodle XML format\n"
#     string += "if you'd like to add further implementation you can view my repo at https://github.com/fmgornick/mutator\n"
#     button = tk.Label(filewin,text=string)
#     button.pack()
    def run(self):
        self.root.mainloop()

    def config(self):
        self.create_menu()
        self.create_textbox()

    def create_menu(self):
        # file menu
        self.file_menu = tk.Menu(self.menu, tearoff = 0)
        self.file_menu.add_command(label="new file", command=self.new_file)
        self.file_menu.add_command(label = "open file...", command = self.open_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label = "save", command = self.save)
        self.file_menu.add_command(label = "save as...", command = self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label = "quit", command = self.close)
        self.menu.add_cascade(label = "file", menu = self.file_menu)

        # edit menu
        self.edit_menu = tk.Menu(self.menu, tearoff = 0)
        self.edit_menu.add_command(label = 'undo', command = self.text.edit_undo)
        self.edit_menu.add_command(label = 'redo', command = self.text.edit_redo)
        self.edit_menu.add_separator()
        self.menu.add_cascade(label = 'edit', menu = self.edit_menu)

        self.root.config(menu = self.menu)

        # self.root.bind('<Control-n>', self.new_file)
        # self.root.bind('<Control-o>', self.open_file)
        # self.root.bind('<Control-s>', self.save)
        # self.root.bind('<Control-S>', self.save_as)
        # self.root.bind('<Control-q>', self.close)
        # self.root.bind('<Control-u>', self.text.edit_undo)
        # self.root.bind('<Control-r>', self.text.edit_redo)

    def create_textbox(self):
        self.text.pack(expand=True, fill=tk.BOTH)

        self.scrollbar = tk.Scrollbar(self.text)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)

    def new_file(self):
        content = self.text.get(1.0, END)

        if self.file != None:
            yn = msg.askyesnocancel("file", f"do you want to save changes to {self.file}?")
            if yn != None:
                if yn:
                    self.save()
                self.file = None
                self.root.title("untitled")
                self.text.delete(1.0, END)

        elif len(content) > 0:
            yn = msg.askyesnocancel("file", f"do you want to save changes to this doc?")
            if yn != None:
                if yn:
                    self.save_as()
                self.file = None
                self.root.title("untitled")
                self.text.delete(1.0, END)

        else:
            self.root.title("untitled")
            self.text.delete(1.0, END)

    def open_file(self):
        self.file = fd.askopenfilename()

        if self.file == "":
            self.file = None

        else:
            self.root.title(os.path.basename(self.file))
            self.text.delete(1.0, END)
            f = open(self.file, "r")
            self.text.insert(1.0, f.read())
            f.close()

    def save(self):
        if self.file == "" or self.file == None:
            self.file = None
        else:
            f = open(self.file, "w")
            f.write(self.text.get(1.0, END))
            f.close

    def save_as(self):
        self.file = fd.asksaveasfilename()
        if self.file == "":
            self.file = None
        else:
            self.root.title(os.path.basename(self.file))
            f = open(self.file, "w")
            f.write(self.text.get(1.0, END))
            f.close

    def close(self):
        content = self.text.get(1.0, END)

        if self.file != None:
            yn = msg.askyesnocancel("file", f"do you want to save changes to {self.file}?")
            if yn != None:
                if yn:
                    self.save()
                self.root.destroy()

        elif len(content) > 0:
            yn = msg.askyesnocancel("file", f"do you want to save changes to this doc?")
            if yn != None:
                if yn:
                    self.save_as()
                self.root.destroy()

        else:
            self.root.destroy()

if __name__ == "__main__":
    window = GUI(700, 500)
    window.config()
    window.run()
