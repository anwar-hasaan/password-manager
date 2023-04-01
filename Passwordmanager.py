#!copyright: https://github.com/anwar-hasaan

# last added feture:
# added login protection system

from tkinter import Menu, ttk, messagebox
from encryptor import Encryptor
from datetime import datetime
from customtkinter import *
import sqlite3

set_appearance_mode("dark")
set_default_color_theme('blue')

#local database
class Database():
    def __init__(self, db_name=None):
        self.db_name = db_name
        self.table_name = None
        self.connection = None
        self.cursor = None
        self.key = Encryptor.KeyLike().replace(b'encryptor', b'=')
    
    #encrypt data
    def encrypt(self, data=[]):
        try:
            if data:
                encrypted_data = []
                for item in data:
                    if not Encryptor.is_encrypted(item):
                        encrypted = Encryptor.encrypt(self.key, item)
                        encrypted_data.append(encrypted)

                return encrypted_data
            return False
        except Exception as e:
            return None

    #decrypt
    def decrypt(self, data=[]):
        # data = [(1,2,3), ]
        try:
            if data:
                decrypted_data = []
                for nested_data in data:
                    temp = []
                    for item in nested_data:
                        if Encryptor.is_encrypted(item):
                            decrypted = Encryptor.decrypt(self.key, item)
                            temp.append(decrypted)
                        else:
                            temp.append(item)
                    decrypted_data.append(temp)
                    temp = []

                return decrypted_data
            return False
        except Exception as e:
            return None

    #create connections
    def open_connection(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        except:
            return False

    #create a table name if not already exists
    def check_or_create_table(self, table_name=None):
        if table_name:
            self.open_connection()
            self.cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    updated_at TEXT)''')
            
            #authUser table to save user login password
            self.cursor.execute(f'CREATE TABLE IF NOT EXISTS AuthUser (id INTEGER PRIMARY KEY, password TEXT NOT NULL )')
            self.table_name = table_name
            self.connection.close()
            return True
        return False
    
    def manageAuthUser(self, id=1, status=None, password=None):
        if not status in ('get', 'set', 'update'):
            return False
        
        self.open_connection()
        if status == 'get':
            self.cursor.execute(f'SELECT password FROM AuthUser WHERE id=?', (id, ))
            password = self.cursor.fetchone()
            secret = password[0] if type(password) == tuple else None
            
            #decrypt 
            if Encryptor.is_encrypted(secret):
                secret = Encryptor.decrypt(self.key, secret)
            return secret


        elif status == 'set':
            #encrypt before save to db
            if password and not Encryptor.is_encrypted(password):
                password = Encryptor.encrypt(self.key, password)

            self.cursor.execute(f'INSERT INTO AuthUser (id, password) VALUES (?, ?)', (id, password))
            self.connection.commit()
            return True
        
        elif status == 'update':
            #encrypt before save to db
            if password and not Encryptor.is_encrypted(password):
                password = Encryptor.encrypt(self.key, password)

            self.cursor.execute(f'UPDATE AuthUser SET password=? WHERE id=?', (password, id))
            self.connection.commit()
            return True

        self.connection.close()
        return False

    #get all data with the table_name
    def get_all_data(self):
        if self.table_name:
            self.open_connection()
            self.cursor.execute(f'SELECT * FROM {self.table_name}')
            data = self.cursor.fetchall()
            self.connection.close()

            decrypted_data = self.decrypt(data=data)
            return decrypted_data
        return False
    
    #get a single data with the given id
    def get(self, id=None):
        if id:
            self.open_connection()
            self.cursor.execute(f'SELECT * FROM {self.table_name} WHERE rowid={id}')
            data = self.cursor.fetchone()
            self.connection.close()

            decrypted = self.decrypt(data=[data]) #self.decrypt() takes [(1, 2, 3), ]
            return decrypted[0] if len(decrypted) == 1 else decrypted #get return only 1 tuple 
        return False

    #add data
    def add(self, url=None, username=None, password=None):
        try:
            encrypted = self.encrypt([url, username, password])
            if encrypted:
                url = encrypted[0]
                username = encrypted[1]
                password = encrypted[2]

            updated_at = f'{datetime.now()}'[:-7]
            self.open_connection()

            self.cursor.execute(f'''INSERT INTO {self.table_name} 
                (url, username, password, updated_at) 
                VALUES (?, ?, ?, ?)''', (url, username, password, updated_at))

            id = self.cursor.lastrowid
            self.connection.commit()
            self.connection.close()
            return id
        except Exception as e:
            self.connection.close()
            return False

    #update 
    def update(self, id, url, username, password):
        if id and url and username and password:
            try:
                encrypted = self.encrypt([url, username, password])
                if encrypted:
                    url = encrypted[0]
                    username = encrypted[1]
                    password = encrypted[2]

                self.open_connection()
                updated_at = f'{datetime.now()}'[:-7]

                self.cursor.execute(
                    f'''UPDATE {self.table_name} SET url=?, username=?, password=?, updated_at=? WHERE id=?''',
                    (url, username, password, updated_at, id)
                )
                self.connection.commit()
                self.connection.close()
                return True
            except:
                return False
        return False

    def delete_item(self, id=None):
        try:
            if id:
                self.open_connection()
                self.cursor.execute(
                    f'DELETE FROM {self.table_name} WHERE id={id}'
                )
                self.connection.commit()
                self.connection.close()
                return True
            return False
        except:
            return False

    def search(self, q):
        if q:
            # self.open_connection()
            # self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE url LIKE ? OR username LIKE ?", (f'%{q}%', f'%{q}%'))
            # data = self.cursor.fetchall()
            # self.connection.close()
            # return data

            decrypted_db_data = self.get_all_data()
            q = q.lower()
            data = []
            
            for row in decrypted_db_data:
                if q in row[1].lower() or q in row[2].lower():
                    data.append(row)
            return data
        else:
            return []
db = Database('pass_manager.db')
db.check_or_create_table('password_manager')


class ViewSavedLoginFrame(CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_item = None
        self.toplevel_window = None
        
        CTkLabel(self, text='', height=25).pack() #preventing to disapper search box :disapper for some weired reason
        #site url search entry
        self.search_entry = CTkEntry(self, width=220, height=25, corner_radius=0, border_width=1, placeholder_text='search by site name or username')
        self.search_entry.place(x=6, y=2)
        
        #search button
        search_btn = CTkButton(self, text='Search', height=25, width=80, corner_radius=0, border_width=1, command=self.search)
        search_btn.place(x=221, y=2)

        X = 440
        width = 80
        #view all btn
        view_all_btn = CTkButton(self, text='View all', height=25, width=width, corner_radius=0, command=self.populate_table)
        view_all_btn.place(x=X+width, y=2)

        #edit btn
        self.edit_btn = CTkButton(self, text='Edit', height=25, width=width, corner_radius=0, command=self.edit_data)
        self.edit_btn.place(x=X+(width*2)+2, y=2)

        #delete btn
        self.delete_btn = CTkButton(self, text='Delete', height=25, width=width, corner_radius=0, command=self.delete_row)
        self.delete_btn.place(x=X+(width*3)+4, y=2)

        #initializing treeview
        self.tree = self.CustomTreeView(
                self, columns=('url', 'username', 'password', 'updated', 'id'), 
                height=15 ) #parent is a custom data pass
        self.tree.pack(padx=5, pady=5)

        def selectItemData(a):
            app.info_label.configure(text='')
            current_item = self.tree.focus()
            data = self.tree.item(current_item)
            self.selected_item = data['values']
        self.tree.bind('<<TreeviewSelect>>', selectItemData)


    def populate_single_table(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.tree.insert(parent='', index='end', text=f'{1}', tags='odd',values=(
                    data[1], #data[1] = url
                    data[2], #data[2] = username
                    data[3], #data[3] = password
                    data[4], #data[4] = updated_at
                    data[0], #data[0] = id
                ))

    #populate table data from db
    def populate_table(self):
        #clear the treeview first
        for row in self.tree.get_children():
            self.tree.delete(row)

        data_list = db.get_all_data()
        if data_list:
            for idx, data in enumerate(data_list):
                tag = 'even' if idx % 2 == 0 else 'odd'
                self.tree.insert(parent='', index='end', text=f'{idx+1}', tags=tag,values=(
                    data[1], #data[1] = url
                    data[2], #data[2] = username
                    data[3], #data[3] = password
                    data[4], #data[4] = updated_at
                    data[0], #data[0] = id
                ))
        else:
            self.tree.insert(parent='', index='end', values=('No saved logins', 'No saved logins', 'No saved logins',))

    class CustomTreeView(ttk.Treeview):
        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)
            ttk.Style().configure('Treeview', rowheight=25)
            
            #set column name heading
            self.heading('#0', text='SL NO')
            self.heading('#1', text='URL')
            self.heading('#2', text='USERNAME')
            self.heading('#3', text='PASSWORD')
            self.heading('#4', text='UPDATED')
            self.heading('#5', text='ID')

            #customize the columns
            self.column('#0', width=50)
            self.column('#1', anchor='center')
            self.column('#2', anchor='center', width=180)
            self.column('#3', anchor='center', width=180)
            self.column('#4', anchor='center', width=120)
            self.column('#5', anchor='center', width=30)
            
            self.tag_configure('odd', background='skyblue', foreground='black')
            self.tag_configure('even', background='cyan', foreground='black')

            self.bind("<Double-1>", self.OnDoubleClick)
        
        def OnDoubleClick(self, event):
            app.info_label.configure(text='')
            region = self.identify_region(event.x, event.y) #return :str: 'cell' or 'heading'
            if region in ('cell', 'tree'):
                column = self.identify_column(event.x) #return column number like #1, #2
                iid = self.focus()

                selected_row = self.item(iid).get('values')
                if column in ('#1', '#2', '#3'):
                    column_index = int(column[1:]) -1  #return from #0 or #1 to 0 or 1 and then -1
                    column_box = self.bbox(iid, column) #retun coordinates
                    
                    try: #copy to clipboard
                        selected_text = selected_row[column_index]
                        self.clipboard_clear()
                        self.clipboard_append(selected_text)
                        app.info_label.configure(text='Text copied to clipboard')
                    except: pass

                    #create a temp entry box 
                    entry_edit = CTkEntry(self, width=column_box[2], corner_radius=0, justify='center')
                    entry_edit.place(x=column_box[0], y=column_box[1], w=column_box[2], h=column_box[3])
                    entry_edit.insert(0, selected_text)
                    entry_edit.focus()
                    entry_edit.select_range(0, 'end')
                    def onFocusOut(event):
                        entry_edit.destroy()
                    entry_edit.bind('<FocusOut>', onFocusOut)
                    

    def search(self):
        app.info_label.configure(text='')
        query = self.search_entry.get()
        if query:
            searched_data = db.search(q=query)
            if searched_data:
                for row in self.tree.get_children():
                    self.tree.delete(row)

                for idx, data in enumerate(searched_data):
                    self.tree.insert(parent='', index='end', text=f'{idx+1}', values=(
                        data[1], #data[1] = url
                        data[2], #data[2] = username
                        data[3], #data[3] = password
                        data[4], #data[4] = updated_at
                        data[0], #data[0] = id
                ))
            else:
                app.info_label.configure(text=f'No data found with ("{query}") this query.')

    def edit_data(self):
        app.info_label.configure(text='')
        if self.selected_item:
            if not type(self.selected_item[-1]) == type(1): 
                return None
            self.open_toplevel(self.selected_item)
        else:
            app.info_label.configure(text='Select a row to perform edit.')
    
    def open_toplevel(self, data):
        parent = self
        #custom top lavel window class
        class UpdateInfoWindow(CTkToplevel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.title('Update?')
                self.w, self.h = 200, 28
                
                w_height = 400
                w_width = 400
                x_coordinates = self.winfo_screenwidth() - (w_width+200)
                y_coordinates = 160
                winsize_and_coordinates = f"{w_width}x{w_height}+{x_coordinates}+{y_coordinates}"
                self.geometry(winsize_and_coordinates)
                # self.geometry("400x400")

                CTkLabel(self, text='Update Login Info', font=('san-sarif', 24, 'bold')).pack(pady=25)

                CTkLabel(self, text='URL').pack()
                self.url = CTkEntry(self, width=self.w, height=self.h)
                self.url.insert('end', data[0])
                self.url.pack()

                CTkLabel(self, text='Username').pack()
                self.username = CTkEntry(self, width=self.w, height=self.h)
                self.username.insert('end', data[1])
                self.username.pack(pady=5)

                CTkLabel(self, text='Password').pack()
                self.password = CTkEntry(self, width=self.w, height=self.h)
                self.password.insert('end', data[2])
                self.password.pack()

                btn = CTkButton(self, text='Submit', command=self.on_update)
                btn.pack(pady=8)

            def on_update(self):
                update_url = self.url.get()
                update_username = self.username.get()
                update_password = self.password.get()
                
                id = data[-1]
                if id and update_url and update_username and update_password:
                    if db.update(id, update_url, update_username, update_password):
                        app.info_label.configure(text='Updated successfully.')
                        
                        #show updated data into treeview
                        updated_data = db.get(id=id)
                        parent.populate_single_table(updated_data)
                        self.after(500, self.destroy())
                    else:
                        app.info_label.configure(text='Something went wrong while updating. \nTry again')
                else:
                    app.info_label.configure(text='Can not update empty data.')

        #TopLavel window logic start here
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = UpdateInfoWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()

    def delete_row(self):
        app.info_label.configure(text='')
        if self.selected_item:
            id = self.selected_item[-1]
            if not type(id) == type(1): 
                return None

            try:
                confirmation = messagebox.askyesno(
                    title='Delete?', 
                    message=f'Do you want to delete login info of ("{self.selected_item[0]}") this site?'
                )
                if confirmation:
                    db.delete_item(id=id)
                    self.populate_table()
                    app.info_label.configure(text='Deleted successful')
                
            except:
                app.info_label.configure(text='Deletion Failed')
        else:
            app.info_label.configure(text='Select a row to perform delete.')


class SaveLoginsFrame(CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initializing the constant value
        self.Font = CTkFont(family="san-sarif", size=15, weight='normal')
        self.corner_radius = 5
        self.border_width = 0.6
        self.width, self.height = 400, 40
        self.padx = 40
        
        #header name
        self.header = CTkLabel(self, text='Save Login Credential', font=('san-sarif', 28, 'bold'))
        self.header.grid(row=0, column=0, padx=self.padx, pady=30)

        #url input label
        url_inp_label = CTkLabel(self, text='Enter the site url', font=self.Font)
        url_inp_label.grid(row=1, column=0)

        #url input entry
        self.url_entry = CTkEntry(
            self, width=self.width, height=self.height, 
            corner_radius=self.corner_radius, 
            border_width=self.border_width, font=self.Font,
            placeholder_text='Link'
        )
        self.url_entry.grid(row=2, column=0, padx=self.padx, pady=5)

        #username input label
        username_label = CTkLabel(self, text='Enter Username', font=self.Font)
        username_label.grid(row=3, column=0)
        
        #username input entry
        self.username_entry = CTkEntry(
            self, width=self.width, height=self.height, 
            corner_radius=self.corner_radius, 
            border_width=self.border_width, font=self.Font,
            placeholder_text='Username'
        )
        self.username_entry.grid(row=4, column=0, padx=self.padx, pady=5)

        #password input label
        password_label = CTkLabel(self, text='Enter Password', font=self.Font)
        password_label.grid(row=5, column=0)

        #on click event on password entry
        def show_or_hide_pass(event=None):
            if self.password_entry.cget('show') == '*':
                self.password_entry.configure(show='')
            else:
                self.password_entry.configure(show='*')

        def show_pass(event):
            if self.password_entry.cget('show') == '*':
                self.password_entry.configure(show='')
            
        #password input entry
        self.password_entry = CTkEntry(
            self, width=self.width, height=self.height, 
            corner_radius=self.corner_radius,
            border_width=self.border_width, font=self.Font,
            placeholder_text='Password', show='*'
        )
        self.password_entry.grid(row=6, column=0, padx=self.padx, pady=5)
        self.password_entry.bind("<Button-1>", show_or_hide_pass)
        # self.password_entry.bind("<Control_L><c>", show_pass)
        
        # switch = CTkCheckBox(self, text='show password', border_width=0.5, checkbox_height=20, checkbox_width=20, command=show_or_hide_pass)
        # switch.place(relx=0.66, rely=0.75)

        #submit button
        submit_btn = CTkButton(
            self, text='Submit', width=200, height=self.height, 
            corner_radius=self.corner_radius, border_width=self.border_width, 
            font=self.Font, command=self.OnSubmit
        )
        submit_btn.grid(row=7, column=0, padx=self.padx, pady=30)
    
    def OnSubmit(self):
        app.info_label.configure(text='')
        url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if url and username and password:
            newly_added_id = db.add(url=url, username=username, password=password)
            app.info_label.configure(text='Login Info Added Successful')
            
            #empty input entry
            self.url_entry.delete(0, 'end')
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')

            #show newly added data into table
            if newly_added_id:
                data = db.get(id=newly_added_id)

                app.show_data_btn.invoke()
                app.saved_login_frame.populate_single_table(data=data)
        else:
            app.info_label.configure(text='Can not add empty credential.')

#no need 
class MyTabView(CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # create tabs
        self.add("Save Logins")
        self.add("View Logins")

        SaveLoginsFrame(self.tab('Save Logins')).grid(row=0, column=0, padx=100, pady=60)
        ViewSavedLoginFrame(self.tab('View Logins')).grid(row=0, column=0, padx=100, pady=60)


#login form
class LoginFrame(CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initializing the constant value
        self.Font = CTkFont(family="san-sarif", size=14, weight='normal')
        self.corner_radius = 5
        self.border_width = 0.6
        self.width, self.height = 250, 40
        self.padx = 60
        
        self.userPassword = db.manageAuthUser(status='get')
        #header name
        Header = 'Welcome \nSet Secret Key \nYou will need it everytime you enter in this app.'
        if self.userPassword:
            Header = 'User Login'
            self.header = CTkLabel(self, text='Type the secret key and press Enter to continue...', font=self.Font)
            self.header.place(relx=0.5, rely=0.35, anchor='center')

        self.Header = CTkLabel(self, text=Header, font=('san-sarif', 28, 'bold'))
        self.Header.grid(row=0, column=0, padx=self.padx, pady=20)

        #on click event on password entry
        def show_or_hide_pass(event=None):
            if self.password_entry.cget('show') == '*':
                self.password_entry.configure(show='')
            else:
                self.password_entry.configure(show='*')

        #password input entry
        self.password_entry = CTkEntry(
            self, width=self.width, height=self.height, 
            corner_radius=self.corner_radius, justify='center',
            border_width=self.border_width, font=self.Font,
            placeholder_text='Type the secret key to continue...', show='*'
        )
        self.password_entry.grid(row=6, column=0, padx=self.padx, pady=40)
        self.password_entry.bind("<Button-1>", show_or_hide_pass)
        
        if self.userPassword:
            self.password_entry.bind("<Return>", self.onEnter)
        else:
            #set user password
            def setPassword(event):
                secret = event.widget.get()
                if len(secret) >= 4:
                    if db.manageAuthUser(status='set', password=secret):
                        app.info_label.configure(text='Password seted successful')
                        self.after(250, app.continue_browse())
                    else:
                        app.info_label.configure(text='Failed to set password.')
                else:
                    app.info_label.configure(text='Password must contain atleast 4 charecters')
            self.password_entry.bind("<Return>", setPassword)

    def onEnter(self, event):
        app.info_label.configure(text='')
        secret_key = event.widget.get()
        
        #update password
        checkUpdate = secret_key.split('::')
        if len(checkUpdate) > 1:
            if checkUpdate[0] == self.userPassword and len(checkUpdate[1]) >= 4:
                db.manageAuthUser(status='update', password=checkUpdate[1])
                app.info_label.configure(text='Password update successful')
                app.continue_browse()
            else:
                app.info_label.configure(text='Failed to update password')
        else:
            #login section
            if secret_key == self.userPassword:
                self.after(250, app.continue_browse())
            else:
                app.info_label.configure(text='Incorrect Password!')
 

class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title('Password Manager')
        w_height = self.winfo_screenheight()-75
        w_width = 800
        x_coordinates = self.winfo_screenwidth() - (w_width+10)
        y_coordinates = 1
        winsize_and_coordinates = f"{w_width}x{w_height}+{x_coordinates}+{y_coordinates}"
        self.geometry(winsize_and_coordinates)
        # self.geometry('800x650')

        # //////////////////////////////////////////////////////////////////////////////
        #Context menu to perform copy, paste, cut and select all in entry widget
        the_menu = Menu(self, tearoff=0)
        the_menu.add_command(label="Cut")
        the_menu.add_command(label="Copy")
        the_menu.add_command(label="Paste")
        the_menu.add_separator()
        the_menu.add_command(label="Select all")

        def show_textmenu(event):
            the_menu.tk.call("tk_popup", the_menu, event.x_root, event.y_root)

            entry = event.widget
            entry.focus()
            entry.select_range(0, 'end')

            if entry.cget('show') == '*':
                entry.configure(show='')

            the_menu.entryconfigure("Cut",command=lambda: entry.event_generate("<<Cut>>"))
            the_menu.entryconfigure("Copy",command=lambda: entry.event_generate("<<Copy>>"))
            the_menu.entryconfigure("Paste",command=lambda: entry.event_generate("<<Paste>>"))
            the_menu.entryconfigure("Select all",command=lambda: entry.select_range(0, 'end'))
        
        self.bind_class("Entry", "<Button-3><ButtonRelease-3>", show_textmenu)
        # //////////////////////////////////////////////////////////////////////////////
        # MyTabView(self).place(relx=0.5, rely=0.5, anchor='center')
        
        self.login = LoginFrame(self)
        self.login.place(relx=0.5, rely=0.5, anchor='center')

        #info label
        self.info_label = CTkLabel(self, text='', font=('san-sarif', 18), text_color='green')
        self.info_label.place(relx=0.5, rely=0.1, anchor='n')

    def continue_browse(self):
        self.login.destroy()
        
        #add login form section frame
        self.create_login_frame = SaveLoginsFrame(self)
        self.create_login_frame.place(relx=0.5, rely=0.5, anchor='center')

        #view saved lon=gin section frame
        self.saved_login_frame = ViewSavedLoginFrame(self)
        self.saved_login_frame.place(relx=0.5, rely=0.5, anchor='center')
        self.saved_login_frame.place_forget()


        def show_login_form():
            self.saved_login_frame.place_forget()
            self.create_login_frame.place(relx=0.5, rely=0.5, anchor='center')
        def show_saved_section():
            self.saved_login_frame.populate_table()
            self.create_login_frame.place_forget()
            self.saved_login_frame.place(relx=0.5, rely=0.5, anchor='center')
        #show form btn
        self.show_create_btn = CTkButton(self, text='Add Login', width=100, corner_radius=2, command=show_login_form)
        self.show_create_btn.pack(side='left', anchor='ne', expand=True, padx=1, pady=20)

        #show detail view btn
        self.show_data_btn = CTkButton(self, text='Show Logins', width=100, corner_radius=2, command=show_saved_section)
        self.show_data_btn.pack(side='right', anchor='nw', expand=True, padx=1, pady=20)


app = App()
app.mainloop()