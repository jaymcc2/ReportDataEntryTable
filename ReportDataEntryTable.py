import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from collections import OrderedDict
from collections import namedtuple


class ReportDataEntryTable(ttk.Frame):
    def __init__(self, parent, table_columns, row_cnt):
        super().__init__(parent)

        # Make container for all content in this frame
        fr_content = ttk.Frame(self, borderwidth=1, relief='ridge', padding=(5, 5, 5, 5))
        fr_content.grid(row=0, column=0, padx=10, pady=10)

        fr_entry_form = ttk.Frame(fr_content)  # Frame for Entry widgets
        fr_command_btns = ttk.Frame(fr_content)  # Frame for command buttons

        fr_entry_form.grid(row=50, column=0, padx=10, pady=20)  # Frame for Entry widgets
        fr_command_btns.grid(row=60, column=0, padx=10, sticky=('E', 'W'))  # Frame for command buttons

        # Keep widgets related to user input contained within self.entries for ease of access
        self.entries = OrderedDict()
        EntryCollection = namedtuple('EntryCollection', 'entry label name col_width entry_width')
        # Loop through input to the class, create each dictionary as an EntryCollection and add
        # to self.entries
        for k, v in table_columns.items():
            self.entries[k] = EntryCollection(entry=ttk.Entry(fr_entry_form),
                                              label=ttk.Label(fr_entry_form),
                                              name=v[0],
                                              col_width=v[1],
                                              entry_width=v[2])
        # Create entry widgets
        for num, v in enumerate(self.entries.values()):
            if v.label is None:
                continue
            v.label.configure(text=v.name, anchor='center')
            v.entry.configure(width=v.entry_width)
            v.label.grid(row=0, column=num)
            v.entry.grid(row=1, column=num, sticky=('W', 'E'))

        # Create buttons to manage the table and entry widgets
        btn_clear_row = ttk.Button(fr_command_btns, text='Clear', command=lambda: self.clear_entry_row())
        btn_add_row = ttk.Button(fr_command_btns, text='Add Row', command=lambda: self.add_table_row())
        # Create unselect button, call configure to assign command that hides btn_table_unselect
        self.fr_selected_row_commands = ttk.Frame(fr_command_btns)
        btn_table_unselect = ttk.Button(self.fr_selected_row_commands, text='Unselect Row')
        btn_table_unselect.configure(command=lambda: self.clear_selection())
        btn_table_row_update = ttk.Button(self.fr_selected_row_commands, text='Update Row', command=lambda: self.update_table_row())
        btn_table_delete_row = ttk.Button(self.fr_selected_row_commands, text='Delete Row', command=lambda: self.verify_delete_table_row())

        btn_table_unselect.grid(column=25, row=2)
        btn_table_row_update.grid(column=20, row=2, padx=(5, 20))
        btn_table_delete_row.grid(column=10, row=2, padx=(5, 100))

        btn_add_row.grid(row=2, column=90, sticky=('W', 'E'))
        btn_clear_row.grid(row=2, column=80, padx=(0, 5), sticky=('E'))

        # self.columnconfigure(0, weight=1)
        fr_command_btns.columnconfigure(0, weight=1)

        # Add Row number to self.entries and move it to beginning
        self.entries['ROWNUMBER'] = EntryCollection(None, None, 'Row\nNumber\n', 50, None)
        self.entries.move_to_end('ROWNUMBER', last=False)

        # Setup Table/Tree Information
        self.table = ttk.Treeview(fr_content, height=row_cnt)
        self.table.grid(column=0, row=0)

        # Bind selection to tree widget, call table_row_selected
        self.table.bind('<<TreeviewSelect>>', lambda event: self.table_row_selected())        # self.table.column('#0', width=0, stretch=tk.NO)  # Hide first (0th) column
        # Declare and configure columns
        self.table['show'] = 'headings'
        self.table['columns'] = list(self.entries.keys())  # (table_columns.keys())
        for k, v in self.entries.items():
            self.table.column(k, width=v.col_width, anchor=tk.CENTER)
            self.table.heading(k, text=v.name)
        ttk.Style().configure('Treeview', rowheight=30)

    # Methods for table widget ######################################
    #################################################################
    # Whenever a table row is selected, show the 'btn_unselect_row'
    def table_row_selected(self):
        if not self.table.selection():
            return
        row_data = self.table.set(self.table.focus())
        print(f'ROW NUMBER: {self.selected_row_num()}')
        self.set_entry_row_data(row_data)
        if self.table.selection():
            self.fr_selected_row_commands.grid(row=2, column=20)
            self.fr_selected_row_commands.tkraise()

    # Whenver btn_unselect_row is clicked, clear the selections from the
    # table, then hide the button
    def clear_selection(self):
        # for i in table.selection():
        #     table.selection_remove(i)
        self.table.selection_set('')
        self.fr_selected_row_commands.grid_forget()
        # btn_unselect_row.grid_forget()
        # btn_table_row_update.grid_forget()

    def add_table_row(self, table_index=None, row_num=None):
        if not self.validate_entry_row_data():
            return 0
        row_data = self.get_entry_row_data()
        
        # Setup values for data entry
        if row_num:
            row_data.insert(0, row_num)
        else:
            row_data.insert(0, self.get_table_last_row_number() + 1)
        
        if not table_index:
            table_index = tk.END
        # Add row number column to beginning of list of row_data
        print(row_num)
        self.table.insert('', table_index, values=row_data)
        # Reset table and entry
        self.clear_entry_row()
        self.clear_selection()

    def selected_row_iid(self):
        if self.table.selection():
            return self.table.selection()[0]

    def selected_row_index(self):
        if self.table.selection():
            return self.table.index(self.table.selection())

    def selected_row_num(self):
        if self.table.selection:
            return self.table.set(self.selected_row_iid())['ROWNUMBER']

    def update_table_row(self):
        # row_data = get_entry_row_data()
        selected_row = self.table.index(self.table.selection())
        row_num = self.selected_row_num()
        row_iid = self.selected_row_iid()
        self.add_table_row(selected_row, row_num=row_num)
        self.delete_table_row(row_iid)


    def get_table_last_row_id(self):
        num_id = self.table.get_children()
        if num_id:
            return self.table.get_children()[-1]
        else:
            return None

    def get_table_last_row_number(self):
        """Returns the row number from the "ROW" column of the last row
           returns as an int"""
        last_id = self.get_table_last_row_id()
        if not last_id:
            return 0
        return int(self.table.set(last_id)["ROWNUMBER"])

    def delete_table_row(self, row_iid):
        self.table.delete(row_iid)
        # Reset table and entry
        self.clear_entry_row()
        self.clear_selection()

    def verify_delete_table_row(self):
        if messagebox.askyesno(title='Warning! Deleting a table row...', message='This action will permamanently\
                                      delete the selected table row.\nAre you sure you want to proceed?', icon='warning'):
            print('going to delete...')
            self.delete_table_row(self.selected_row_iid())

    # Methods for entry widgets #####################################
    #################################################################
    def get_entry_row_data(self):
        return [v.entry.get() for v in self.entries.values() if v.entry is not None]

    def set_entry_row_data(self, row_data):
        self.clear_entry_row()
        for e, i in zip(self.entries.values(), row_data.values()):
            if e.entry is not None:
                e.entry.insert(0, i)

    def clear_entry_row(self):
        """Clear the entry widgets that are used to add data to table"""
        for v in self.entries.values():
            if v.entry is not None:
                v.entry.delete(0, tk.END)

    def validate_entry_row_data(self):
        """validate the row data"""
        for k, v in self.entries.items():
            if k is not 'ROWNUMBER' and not v.entry.get():
                print('EMPTY FOUND')
                return 0
        return 1


def main():
    root = tk.Tk()
    content = ttk.Frame(root)
    # table_columns = {'NAME': 'Name', 'COLOR': 'Color', 'SHAPE': 'Shape'}
    table_columns = {
                     'COLOR': ('Color', 200, 20),
                     'SHAPE': ('Shape', 200, 20),
                     'SIZE': ('Size', 200, 20),
                     }
    table = ReportDataEntryTable(content, table_columns, 5)
    # Layout widgets
    content.grid(column=0, row=0, sticky=('W', 'E'))
    table.grid(column=0, row=0, sticky=('W', 'E'))

    root.columnconfigure(0, weight=1)
    content.columnconfigure(0, weight=1)
    table.columnconfigure(0, weight=1)

    root.mainloop()

if __name__ == '__main__':
    main()
