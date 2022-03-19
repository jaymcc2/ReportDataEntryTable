import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
"""
Create a class that is specific to each analysis type
"""


class AnalysisController:
    """Provide logical interface for the table and entry widget functins"""
    def start(self, parent, table, entry):
        self.table = table(parent, self)
        self.entry = entry(parent, self)
        self.command = AnalysisDataButtons(parent, self)

        self.create_dialog_bindings()

    def show(self):
        # content = ttk.Frame(parent, borderwidth=1, relief='ridge', padding=(5, 5, 5, 5))
        self.table.grid(row=10, column=0)
        self.entry.grid(row=20, column=0)
        self.command.grid(row=30, column=0, sticky=('E', 'W'))

    # Entry functions ###############################################
    def get_entry_row_data(self):
        return self.entry.get()

    def handle_clear_entry_row(self):
        self.entry.clear()
        first_entry_field_name = next(iter(self.entry.entries))
        self.entry.set_focus()

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
        print(self.table.get())
        self.entry.set(self.table.get())

    def handle_update_selected_row(self):
        self.table.update(self.table.selected, self.get_entry_row_data())

    def handle_delete_table_row(self):
        self.table.delete(self.table.selected)

    # Dialog Bindings ###############################################
    def create_dialog_bindings(self):

        # bind enter key to last entry field, have it add entry fields to data table
        last_entry_field_name = next(reversed(self.entry.entries))
        # self.entry.entries[last_entry_field_name].entry.bind('<Return>', lambda event: self.handle_add_table_row())

        # Bind selection to tree widget, call _table_row_selected
        self.table.table.bind('<<TreeviewSelect>>', self.handle_table_row_selected)


class AnalysisDataButtons(ttk.Frame):
    """Define buttons and the call to controller functions for them"""
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

        self.columnconfigure(0, weight=1)

    def show_selected_row_buttons(self):
        self.fr_selected_row_commands.grid(row=2, column=20)
        self.fr_selected_row_commands.tkraise()

    def hide_selected_row_buttons(self):
        self.fr_selected_row_commands.grid_forget()


class AnalysisDataTable(ttk.Frame):
    """Create a table to view data that is input from the entry fields"""
    def __init__(self, parent, controller, row_cnt=5):
        super().__init__(parent)

        self.table = ttk.Treeview(self, height=row_cnt)
        self.table.grid(column=0, row=0)

        # Add scrollbar function to table
        scrll_table = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.table.yview)
        self.table['yscrollcommand'] = scrll_table.set
        scrll_table.grid(column=1, row=0, sticky=('N', 'S', 'E'))

        # Declare and configure columns
        self.table['show'] = 'headings'
        ttk.Style().configure('Treeview', rowheight=30)
        self._set_columns()

    def _set_columns(self):
        # Create columns for entry data
        self.table['columns'] = ['Row', 'State', 'City', 'Zip', 'Description']

        # Define the apperance of the columns
        self.table.column('Row', width=50, anchor=tk.CENTER)
        self.table.heading('Row', text='Row')
        self.table.column('State', width=100, anchor=tk.CENTER)
        self.table.heading('State', text='State')        
        self.table.column('City', width=100, anchor=tk.CENTER)
        self.table.heading('City', text='City')
        self.table.column('Zip', width=100, anchor=tk.CENTER)
        self.table.heading('Zip', text='Zip')
        self.table.column('Description', width=100, anchor=tk.CENTER)
        self.table.heading('Description', text='Description')

        # Set which columns should appear in the table, any defined columns
        # not in this list will not appear, but will still be able to contain
        # data from entry inputs
        self.table['displaycolumns'] = ('Row', 'State', 'City', 'Zip')

    def get(self):
        # Get table row of given iid
        # Data is returned as of dictionary
        # Color: 'red', shape='square'
        return self.table.set(self.table.focus())

    def get_all(self):
        # This should return all rows, as a list of dicts
        # [DEBUG] NOT TESTED!!!
        return [self.table.set(r) for r in self.get_table_iids()]

    def add(self, row_data):
        # Insert new data row into the table
        row_data.insert(0, self.last_row_index + 2)      # Add row number to list
        self.table.insert('', tk.END, values=row_data)   # Insert to table
        self.table.yview(tk.MOVETO, 1)                   # Scroll Y to see new entry

    def update(self, iid, row_data):
        # Update the table row of the given iid
        for k, v in row_data.items():
            self.table.set(iid, k, v)

    def delete(self, row_iid):
        # Delete table row of the given iid
        if not self._verify_delete_table_row():  # Offer last chance to not delete the row
            return
        self.table.delete(row_iid)  # Delete the given row iid
        self._renumber_rows()       # Renumber the row column

    def unselect(self):
        # Remove table selection
        self.table.selection_set('')

    def _renumber_rows(self):
        # Loop through table and renumber the row column
        # [INFO]This uses a different logic to set row number 
        # than the add method, could be an issue
        for num, iid in enumerate(self.get_table_iids()):
            self.table.set(iid, 'Row', num + 1)

    @property
    def selected(self):
        """Returns the iid of the selected row, or False 
        if a table item is not selected"""
        if self.table.selection():
            return self.table.selection()[0]
        return False

    @property
    def selected_row_index(self):
        """Return the index of the selected row"""
        return self.table.index(self.table.selection())

    @property
    def table_row_count(self):
        """Returns the number of entries in the data table
           Useful as a check for empty table"""
        return len(self.table.get_children())

    def get_table_iids(self):
        """Returns a list of all iid in the table"""
        return self.table.get_children()

    @property
    def last_row_iid(self):
        """Returns the iid of the last row in the table"""
        if self.table_row_count:
            return self.get_table_iids()[-1]
        return None

    @property
    def last_row_index(self):
        """Returns the index of the last row in the table"""
        if self.table_row_count:
            return self.table.index(self.last_row_iid)
        return -1

    def _verify_delete_table_row(self):
        return messagebox.askyesno(title='Warning! Deleting a table row...', message='This action will permamanently\
                                      delete the selected table row.\nAre you sure you want to proceed?', icon='warning')


class AnalysisDataEntry(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        fr_entry_form = ttk.Frame(self)  # Frame for Entry widgets
        fr_entry_form.grid(row=50, column=0, padx=10, pady=20)  # Frame for Entry widgets

        self._set_widgets(fr_entry_form)

    def _set_widgets(self, parent):
        """Create and grid entry widgets for report dialog
        
        When subclassing the AnalysisDataEntry class this method should be redefined
        with the specific widgets and layout desired
        """
        self.entries = {}

        self.entries['State'] = (ttk.Label(parent, text='State', anchor='center'), ttk.Entry(parent, width=15))
        self.entries['City'] = (ttk.Label(parent, text='City', anchor='center'), ttk.Entry(parent, width=15))
        self.entries['Zip'] = (ttk.Label(parent, text='Zip', anchor='center'), ttk.Entry(parent, width=15))
        self.entries['Description'] = (ttk.Label(parent, text='Description', anchor='center'), ttk.Entry(parent, width=50))

        self._grid_label_entry(self.entries['State'], 0, 0)
        self._grid_label_entry(self.entries['City'], 0, 1)
        self._grid_label_entry(self.entries['Zip'], 0, 2)
        self._grid_label_entry(self.entries['Description'], 3, 0, columnspan=3)

        # Add validation to entry
        check_number = (parent.register(self.isNumber), '%P', 99)
        self.entries['Zip'][1].config(validate='all', validatecommand=(check_number))

    def isNumber(self, input, value=None):
        """Function returns True if given data is a number or
        an empty string, all other values will return False"""
        if not input:  # Allow empty field
            return True
        if not input.isdigit():
            return False
        if value and int(input) > int(value):
            return False
        return True

    def _grid_label_entry(self, widget_collection, row, column, **kwargs):
        l, e = widget_collection
        l.grid(row=row, column=column, **kwargs)
        e.grid(row=row + 1, column=column, **kwargs)

    def get(self):
        return {k: v[1].get() for k, v in self.entries.items()}

    def set(self, row_data):
        for k, v in self.entries.items():
            v[1].insert(0, row_data[k])

    def clear(self):
        """Clear the entry widgets that are used to add data to table"""
        for v in self.entries.values():
            if v[1] is not None:
                v[1].delete(0, tk.END)

    def set_focus(self):
        list(self.entries.values())[0][1].focus_set()

    def validate_entry_row_data(self):
        """validate the row data"""
        for k, v in self.entries.items():
            if k != 'ROWNUMBER' and not v.entry.get():
                print('EMPTY FOUND')
                return 0
        return 1


def main():

    root = tk.Tk()

    content = ttk.Frame(root, padding=(10, 10, 10, 10))
    control = AnalysisController()
    control.start(content, AnalysisDataTable, AnalysisDataEntry)
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
