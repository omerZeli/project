import socket
import sqlite3
import os
import select


class server:

    def __init__(self, data_base_path, imports_table_name, users_table_name, files_path):
        self.data_base_path = data_base_path
        self.imports_table_name = imports_table_name
        self.users_table_name = users_table_name
        self.files_path = files_path
        self.open_client_sockets = []
        self.messages_to_send = []

    # send messages
    def send_waiting_messages(self, wlist, messages_to_send):
        for message in messages_to_send:
            (client_socket, data) = message
            if client_socket in wlist:
                data = data.encode()
                client_socket.send(data)
                messages_to_send.remove(message)

    # create data base table
    def create_table(self, table_path, table_name, column1, column2):
        conn = sqlite3.connect(table_path)
        st = '''CREATE TABLE {}
                    (
                    {}  TEXT    NOT NULL,
                    {}   TEXT    NOT NULL
                    );'''.format(table_name, column1, column2)
        conn.execute(st)
        conn.close()

    # find files of codes (.py/.txt)
    def find_files(self):
        files_list = []
        for filename in os.listdir(self.files_path):
            if ".txt" in filename:
                files_list.append(self.files_path + "\\" + filename)
            if ".py" in filename:
                files_list.append(self.files_path + "\\" + filename)
        return files_list

    # find the lines imports in the files
    def find_imports(self):
        files_list = self.find_files()
        lines_list = []
        for path in files_list:
            file = open(path, "r")
            contents = file.read()
            lines = contents.split("\n")
            for line in lines:
                if "import" in line:
                    tup = self.cut_lines(line, path)
                    lines_list.append(tup)
            file.close()
        return lines_list

    # cut the import and the file name
    def cut_lines(self, line, path):
        split_line = line.split(" ")
        sec_line = split_line[1]
        split_path = path.split("\\")
        sec_path = split_path[-1]
        tup = (sec_line, sec_path)
        return tup

    # insert data to data base table
    def insert(self, table_name, column1, column2, data):
        conn = sqlite3.connect(self.data_base_path)
        st = "INSERT INTO {} ({},{}) VALUES ('{}', '{}')".format(table_name, column1, column2, data[0], data[1])
        conn.execute(st)
        conn.commit()
        conn.close()

    # insert the imports to the data base
    def insert_imports(self, column1, column2):
        lines_list = self.find_imports()
        for data in lines_list:
            self.insert(self.imports_table_name, column1, column2, data)

    # find the word in the data base
    def find_word(self, the_word, current_socket):
        conn = sqlite3.connect(self.data_base_path)
        cursor = conn.execute("SELECT * from {}".format(self.imports_table_name))
        names_lst = []
        cut_word = the_word.split(' ')
        for row in cursor:
            for word in cut_word:
                if word == row[0]:
                    names_lst.append(row[1])
        if len(names_lst) == 0:
            self.messages_to_send.append((current_socket, "no results"))
        else:
            str_names_lst = ""
            for i in names_lst:
                str_names_lst += i + ", "
            str_names_lst = str_names_lst[:-2]
            self.messages_to_send.append((current_socket, str_names_lst))

    # find the user name and the password from the message
    def cut_sign_msg(self, msg):
        data = msg.split(": ")
        profile = data[1]
        profile = profile.split(", ")
        profile = tuple(profile)
        return profile

    # if the user is in the table
    def in_table(self, profile):
        conn = sqlite3.connect(self.data_base_path)
        cursor = conn.execute("SELECT * from {}".format(self.users_table_name))
        exist = False
        for row in cursor:
            if row == profile:
                exist = True
        return exist

    # sign up an user
    def sing_up(self, column1, column2, the_word, current_socket):
        profile = self.cut_sign_msg(the_word)
        exist = self.in_table(profile)
        if exist:
            self.messages_to_send.append((current_socket, "This user is already exists"))
        else:
            self.insert(self.users_table_name, column1, column2, profile)
            self.messages_to_send.append((current_socket, "You signed up"))

    # sign in an user
    def sign_in(self, the_word, current_socket):
        profile = self.cut_sign_msg(the_word)
        exist = self.in_table(profile)
        if exist:
            self.messages_to_send.append((current_socket, "You signed in"))
        else:
            self.messages_to_send.append((current_socket, "You have a mistake in your user name or your password"))

    def main(self):
        print("server begin")
        server_socket = socket.socket()
        server_socket.bind(("0.0.0.0", 8820))
        server_socket.listen(1)
        imports_column1 = 'the_import'
        imports_column2 = 'the_file'
        users_column1 = 'user_name'
        users_column2 = 'password'

        while True:
            rlist, wlist, xlist = \
                select.select([server_socket] + self.open_client_sockets, self.open_client_sockets, [])
            for current_socket in rlist:
                if current_socket is server_socket:
                    (new_socket, address) = server_socket.accept()
                    self.open_client_sockets.append(new_socket)
                else:
                    # get the word
                    the_word = current_socket.recv(1024)
                    the_word = the_word.decode()
                    if the_word == 'quit':
                        self.open_client_sockets.remove(current_socket)
                        self.messages_to_send.append((current_socket, "end connection"))
                    elif "sign_up" in the_word:
                        try:
                            self.sing_up(users_column1, users_column2, the_word, current_socket)
                        except:
                            self.create_table(self.data_base_path, self.users_table_name, users_column1, users_column2)
                            print("Users data base created")
                            self.sing_up(users_column1, users_column2, the_word, current_socket)
                    elif "sign_in" in the_word:
                        try:
                            self.sign_in(the_word, current_socket)
                        except:
                            self.create_table(self.data_base_path, self.users_table_name, users_column1, users_column2)
                            print("Users data base created")
                            self.sign_in(the_word, current_socket)
                    elif "file_len" in the_word:
                        (command, file_name) = the_word.split(": ")
                        file = open(self.files_path + "\\" + file_name)
                        text = file.read()
                        length = len(text)
                        times = (length//1024)+1
                        times = str(times)
                        self.messages_to_send.append((current_socket, times))
                    elif "send_file" in the_word:
                        (command, file_name) = the_word.split(": ")
                        file = open(self.files_path + "\\" + file_name)
                        text = file.read()
                        self.messages_to_send.append((current_socket, text))
                    else:
                        try:
                            self.find_word(the_word, current_socket)
                        except:
                            self.create_table(self.data_base_path, self.imports_table_name, imports_column1,
                                              imports_column2)
                            self.insert_imports(imports_column1, imports_column2)
                            print("Imports data base created")
                            self.find_word(the_word, current_socket)
            self.send_waiting_messages(wlist, self.messages_to_send)


data_base_path = 'data_base.db'
imports_table_name = 'IMPORTS'
users_table_name = 'USERS'
files_path = 'files_data'
server(data_base_path, imports_table_name, users_table_name, files_path).main()
