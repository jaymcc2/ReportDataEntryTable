import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from collections import OrderedDict
from collections import namedtuple

"""
This module requires three functions to operate
1. A controller function that wraps the working functions, and provides an instanciation method for 
   the other classes, and an input and output method for information to the package
2. A table function, that exposes methods and properties to input and output information
3. An entry function that allows user input, and provides methods to input and output information
4. A command function that bridges the table and entry functions, it should connect to the methods of 
   each in a logical way

Each of these seperate functions should be created as a seperate class in the package.  The controller
function should be the only one that is called on???
"""


class Controller:

    def start(self, parent, table_columns):
        self.table = ReportDataTable(parent, table_columns, self)
        self.entry = ReportDataEntryInputs(parent, table_columns, self)
        self.command = ReportDataEntryButtons(parent, self)

        self.create_dialog_bindings()

    def show(self):
        # content = ttk.Frame(parent, borderwidth=1, relief='ridge', padding=(5, 5, 5, 5))
        self.table.grid(row=10, column=0)
        self.entry.grid(row=20, column=0)
        self.command.grid(row=30, column=0)

    # Entry functions ###############################################
    def get_entry_row_data(self):
        return self.entry.get()

    def handle_clear_entry_row(self):
        self.entry.clear()
        first_entry_field_name = next(iter(self.entry.entries))
        self.entry.entries[first_entry_field_name].entry.focus_set()

    # Table functions ###############################################
    def handle_unselect_table_row(self):
        self.table.unselect()
        self.command.hide_selected_row_buttons()

    def handle_add_table_row(self):
        self.table.add(list(self.get_entry_row_data().values()))
        self.handle_clear_entry_row()

    def handle_table_row_selected(self, event):
        if not self.table.selected:
            return
        self.command.show_selected_row_buttons()
        self.handle_clear_entry_row()
        self.entry.set(self.table.get())

    def handle_update_selected_row(self):
        self.table.update(self.table.selected, self.get_entry_row_data())

    def handle_delete_table_row(self):
        self.table.delete(self.table.selected)

    # Dialog Bindings ###############################################
    def create_dialog_bindings(self):

        # bind enter key to last entry field, have it add entry fields to data table
        last_entry_field_name = next(reversed(self.entry.entries))
        self.entry.entries[last_entry_field_name].entry.bind('<Return>', lambda event: self.handle_add_table_row())

        # Bind selection to tree widget, call _table_row_selected
        self.table.table.bind('<<TreeviewSelect>>', self.handle_table_row_selected)


class ReportDataTable(ttk.Frame):
    def __init__(self, parent, table_columns, controller, row_cnt=5):
        super().__init__(parent)

        self.table = ttk.Treeview(self, height=row_cnt)
        self.table.grid(column=0, row=0)

        # Add scrollbar function to table
        scrll_table = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.table.yview)
        self.table['yscrollcommand'] = scrll_table.set
        scrll_table.grid(column=1, row=0, sticky=('N', 'S', 'E'))

        # Declare and configure columns
        self.table['show'] = 'headings'
        self.table['columns'] = list(table_columns.keys())  # (table_columns.keys())
        for k, v in table_columns.items():
            self.table.column(k, width=v[1], anchor=tk.CENTER)
            self.table.heading(k, text=v[0])
        ttk.Style().configure('Treeview', rowheight=30)

    def get(self):
        return self.table.set(self.table.focus())

    def get_all(self):
        return [self.table.set(r) for r in self.get_table_iids()]

    def add(self, row_data):  # table_index=None,
        self.table.insert('', tk.END, values=row_data)
        self.table.yview(tk.MOVETO, 1)  # Scroll Y to see new entry

    def update(self, iid, row_data):  # row_num
        for k, v in row_data.items():
            self.table.set(iid, k, v)

    def delete(self, row_iid):
        if not self._verify_delete_table_row():
            return
        self.table.delete(row_iid)

    def unselect(self):
        self.table.selection_set('')

    # def _renumber_rows(self):
    #     for num, row in enumerate(self.get_table_iids()):
    #         self.table.set(row, 'ROWNUMBER', num + 1)

    @property
    def selected(self):
        """Returns the iid of the selected row, or False 
        if a table item is not selected"""
        if self.table.selection():
            return self.table.selection()[0]
        return False

    @property
    def selected_row_iid(self):
        return self.table.selection()[0]

    @property
    def selected_row_index(self):
        return self.table.index(self.table.selection())

    @property
    def selected_row_number(self):
        return self.selected_row_index + 1

    @property
    def table_row_count(self):
        return len(self.table.get_children())

    def get_table_iids(self):
        return self.table.get_children()

    @property
    def last_row_id(self):
        if self.table_row_count:
            return self.get_table_iids()[-1]
        return None

    @property
    def last_row_index(self):
        return self.table.index(self.last_row_id)

    @property
    def last_row_number(self):
        """Uses table index to determine last row number"""
        if not self.table_row_count:
            return 0  # Return 0 for an empty table
        return self.table.index(self.last_row_id) + 1

    def _verify_delete_table_row(self):
        return messagebox.askyesno(title='Warning! Deleting a table row...', message='This action will permamanently\
                                      delete the selected table row.\nAre you sure you want to proceed?', icon='warning')


class ReportDataEntryButtons(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Create buttons to manage the table and entry widgets
        btn_clear_row = ttk.Button(self, text='Clear', command=controller.handle_clear_entry_row)
        btn_add_row = ttk.Button(self, text='Add Row', command=controller.handle_add_table_row) 
        # Create unselect button, call configure to assign command that hides btn_table_unselect
        self.fr_selected_row_commands = ttk.Frame(self)
        btn_table_unselect = ttk.Button(self.fr_selected_row_commands, text='Unselect Row', command=controller.handle_unselect_table_row)
        btn_table_row_update = ttk.Button(self.fr_selected_row_commands, text='Update Row', command=controller.handle_update_selected_row)
        btn_table_delete_row = ttk.Button(self.fr_selected_row_commands, text='Delete Row', command=controller.handle_delete_table_row)

        btn_table_unselect.grid(column=25, row=2)
        btn_table_row_update.grid(column=20, row=2, padx=(5, 20))
        btn_table_delete_row.grid(column=10, row=2, padx=(5, 100))

        btn_add_row.grid(row=2, column=90, sticky=('W', 'E'))
        btn_clear_row.grid(row=2, column=80, padx=(0, 5), sticky=('E'))

        # self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def show_selected_row_buttons(self):
        self.fr_selected_row_commands.grid(row=2, column=20)
        self.fr_selected_row_commands.tkraise()

    def hide_selected_row_buttons(self):
        self.fr_selected_row_commands.grid_forget()


class ReportDataEntryInputs(ttk.Frame):
    def __init__(self, parent, input_info, controller):
        super().__init__(parent)

        self.controller = controller

        fr_entry_form = ttk.Frame(self)  # Frame for Entry widgets
        fr_entry_form.grid(row=50, column=0, padx=10, pady=20)  # Frame for Entry widgets

        # Keep widgets related to user input contained within self.entries for ease of access
        self.entries = OrderedDict()
        EntryCollection = namedtuple('EntryCollection', 'entry label name')
        # Loop through input to the class, create each dictionary as an EntryCollection and add
        # to self.entries
        for num, (k, v) in enumerate(input_info.items()):
            self.entries[k] = EntryCollection(entry=ttk.Entry(fr_entry_form),
                                              label=ttk.Label(fr_entry_form),
                                              name=v[0])
            self.entries[k].label.configure(text=self.entries[k].name, anchor='center')
            self.entries[k].entry.configure(width=v[2])
            self.entries[k].label.grid(row=0, column=num)
            self.entries[k].entry.grid(row=1, column=num, sticky=('W', 'E'))

    def get(self):
        return {k: v.entry.get() for k, v in self.entries.items()}

    def set(self, row_data):
        for e, i in zip(self.entries.values(), row_data.values()):
            print(i)
            e.entry.insert(0, i)

    def clear(self):
        """Clear the entry widgets that are used to add data to table"""
        for v in self.entries.values():
            if v.entry is not None:
                v.entry.delete(0, tk.END)
        list(self.entries.values())[1].entry.focus_set()

    def validate_entry_row_data(self):
        """validate the row data"""
        for k, v in self.entries.items():
            if k != 'ROWNUMBER' and not v.entry.get():
                print('EMPTY FOUND')
                return 0
        return 1


def main():
    # table_columns = {'NAME': 'Name', 'COLOR': 'Color', 'SHAPE': 'Shape'}
    table_columns = {
                     'STATE': ('State', 200, 20),
                     'CITY': ('City', 200, 20),
                     'ZIP': ('Zip', 200, 20),
                     }

    root = tk.Tk()

    content = ttk.Frame(root, padding=(10, 10, 10, 10))
    control = Controller()
    control.start(content, table_columns)
    control.show()

    close = ttk.Button(content, text='Close', command=root.destroy)
    get_rows = ttk.Button(content, text='Get Rows', command=lambda: print(table.get_all()))

    # Layout widgets
    content.grid(row=99, column=0, sticky=('W', 'E'))
    close.grid(row=99, column=0, sticky='E')
    get_rows.grid(row=98, column=0, sticky='E')

    root.columnconfigure(0, weight=1)
    content.columnconfigure(0, weight=1)

    root.mainloop()


if __name__ == '__main__':
    main()
