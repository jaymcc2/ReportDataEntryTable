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
            self.entries[k].entry.bind('<Return>', lambda event: self._add_table_row())
        # Create entry widgets
        for num, v in enumerate(self.entries.values()):
            if v.label is None:
                continue
            v.label.configure(text=v.name, anchor='center')
            v.entry.configure(width=v.entry_width)
            v.label.grid(row=0, column=num)
            v.entry.grid(row=1, column=num, sticky=('W', 'E'))

        # Create buttons to manage the table and entry widgets
        btn_clear_row = ttk.Button(fr_command_btns, text='Clear', command=lambda: self._clear_entry_row())
        btn_add_row = ttk.Button(fr_command_btns, text='Add Row', command=lambda: self._add_table_row()) 
        # Create unselect button, call configure to assign command that hides btn_table_unselect
        self.fr_selected_row_commands = ttk.Frame(fr_command_btns)
        btn_table_unselect = ttk.Button(self.fr_selected_row_commands, text='Unselect Row')
        btn_table_unselect.configure(command=lambda: self._clear_selection())
        btn_table_row_update = ttk.Button(self.fr_selected_row_commands, text='Update Row', 
                                          command=lambda: self._update_table_row(self.selected_row_iid,
                                                                                self.selected_row_number))
        btn_table_delete_row = ttk.Button(self.fr_selected_row_commands, text='Delete Row',
                                          command=lambda: self._verify_delete_table_row())

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
        fr_table = ttk.Frame(fr_content)
        fr_table.grid(column=0, row=0, sticky=('W', 'N', 'E', 'S'))
        self.table = ttk.Treeview(fr_table, height=row_cnt)
        self.table.grid(column=0, row=0)
        # Add scrollbar function to table
        scrl_table = ttk.Scrollbar(fr_table, orient=tk.VERTICAL, command=self.table.yview)
        self.table['yscrollcommand'] = scrl_table.set
        scrl_table.grid(column=1, row=0, sticky=('N', 'S', 'E'))


        # Declare and configure columns
        self.table['show'] = 'headings'
        self.table['columns'] = list(self.entries.keys())  # (table_columns.keys())
        for k, v in self.entries.items():
            self.table.column(k, width=v.col_width, anchor=tk.CENTER)
            self.table.heading(k, text=v.name)
        ttk.Style().configure('Treeview', rowheight=30)

        # Bind selection to tree widget, call _table_row_selected
        self.table.bind('<<TreeviewSelect>>', lambda event: self._table_row_selected())

    # Methods for table widget ######################################
    #################################################################
    # Whenever a table row is selected, show the 'btn_unselect_row'
    def _table_row_selected(self):
        if not self.table.selection():
            return
        row_data = self.table.set(self.table.focus())
        print(f'INDEX: {self.selected_row_index} IID: {self.selected_row_iid}')
        self._set_entry_row_data(row_data)
        # When table selected, show the selected table row commands
        if self.table.selection():
            self.fr_selected_row_commands.grid(row=2, column=20)
            self.fr_selected_row_commands.tkraise()

    # Whenver btn_unselect_row is clicked, clear the selections from the
    # table, then hide the button
    def _clear_selection(self):
        self.table.selection_set('')
        self.fr_selected_row_commands.grid_forget()

    def _add_table_row(self): #table_index=None,
        if not self._validate_entry_row_data():
            return 0
        row_data = self._get_entry_row_data()
        row_data.insert(0, self.last_row_number + 1)
        # Add row number column to beginning of list of row_data
        self.table.insert('', tk.END, values=row_data)
        self.table.yview(tk.MOVETO, 1) # Scroll Y to see new entry
        # Reset table and entry
        self._clear_entry_row()
        self._clear_selection()

    def _update_table_row(self, iid, row_num):
        self.table.set(iid, 'ROWNUMBER', row_num)
        for k, v in self.entries.items():
            if k != 'ROWNUMBER':
                self.table.set(iid, k, v.entry.get())

    def _renumber_rows(self):
        for num, row in enumerate(self.get_table_iids()):
            self.table.set(row, 'ROWNUMBER', num + 1)

    def _delete_table_row(self, row_iid):
        self.table.delete(row_iid)
        # Reset table and entry
        self._renumber_rows()
        self._clear_entry_row()
        self._clear_selection()

    def _verify_delete_table_row(self):
        if messagebox.askyesno(title='Warning! Deleting a table row...', message='This action will permamanently\
                                      delete the selected table row.\nAre you sure you want to proceed?', icon='warning'):
            print('going to delete...')
            self._delete_table_row(self.selected_row_iid)

    @property
    def selected_row_iid(self):
        if self.table.selection():
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

    def get_rows(self):
        return [self.table.set(r) for r in self.get_table_iids()]



    # Methods for entry widgets #####################################
    #################################################################
    def _get_entry_row_data(self):
        return [v.entry.get() for v in self.entries.values() if v.entry is not None]

    def _set_entry_row_data(self, row_data):
        self._clear_entry_row()
        for e, i in zip(self.entries.values(), row_data.values()):
            if e.entry is not None:
                e.entry.insert(0, i)

    def _clear_entry_row(self):
        """Clear the entry widgets that are used to add data to table"""
        for v in self.entries.values():
            if v.entry is not None:
                v.entry.delete(0, tk.END)
        list(self.entries.values())[1].entry.focus_set()

    def _validate_entry_row_data(self):
        """validate the row data"""
        for k, v in self.entries.items():
            if k != 'ROWNUMBER' and not v.entry.get():
                print('EMPTY FOUND')
                return 0
        return 1


def main():
    root = tk.Tk()
    content = ttk.Frame(root, padding=(10, 10, 10, 10))
    # table_columns = {'NAME': 'Name', 'COLOR': 'Color', 'SHAPE': 'Shape'}
    table_columns = {
                     'STATE': ('State', 200, 20),
                     'CITY': ('City', 200, 20),
                     'ZIP': ('Zip', 200, 20),
                     }

    table = ReportDataEntryTable(content, table_columns, 5)

    close = ttk.Button(content, text='Close', command=root.destroy)
    get_rows = ttk.Button(content, text='Get Rows', command=lambda: print(table.get_rows()))

    # Layout widgets
    content.grid(column=0, row=0, sticky=('W', 'E'))
    table.grid(column=0, row=0, sticky=('W', 'E'))
    close.grid(row=99, column=0, sticky='E')
    get_rows.grid(row=98, column=0, sticky='E')

    root.columnconfigure(0, weight=1)
    content.columnconfigure(0, weight=1)
    table.columnconfigure(0, weight=1)

    root.mainloop()

if __name__ == '__main__':
    main()
