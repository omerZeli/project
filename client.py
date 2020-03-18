import socket
import tkinter as tk
import webbrowser


class client:

    def __init__(self, ip):
        self.ip = ip
        self.my_socket = socket.socket()
        self.root = tk.Tk()
        self.text_box = tk.Text(self.root, height=30, width=150)
        self.entry = tk.Entry(self.root)

    # input details in sign up
    def input_sign(self, sign):
        user_name = self.input("Enter user name")
        password = self.input("Enter password")
        msg = "{}: {}, {}".format(sign, user_name, password)
        return msg

    # send a message and get a receive an answer
    def send_and_rec(self, msg):
        msg = msg.encode()
        self.my_socket.send(msg)
        ans = self.my_socket.recv(1024)
        ans = ans.decode()
        return ans

    def print_message(self, text):
        self.text_box.insert(tk.END, text + "\n")

    def input(self, text):
        self.print_message(text)
        var = tk.IntVar()
        button = tk.Button(self.root, text="enter", command=lambda: var.set(1))
        button.pack()
        button.wait_variable(var)
        output = self.entry.get()
        self.print_message(output)
        button.pack_forget()
        self.entry.delete(0, 'end')
        return output

    def delete_text_box(self):
        self.text_box.delete('1.0', tk.END)

    def show_sign(self, sign, su_botton, si_button):
        su_botton.pack_forget()
        si_button.pack_forget()
        self.entry.pack()
        self.delete_text_box()
        ser_ans = ""
        if sign == "sign_up":
            while ser_ans != "You signed up":
                msg = self.input_sign("sign_up")
                ser_ans = self.send_and_rec(msg)
                self.print_message(ser_ans)
        else:
            while ser_ans != "You signed in":
                msg = self.input_sign("sign_in")
                ser_ans = self.send_and_rec(msg)
                self.print_message(ser_ans)
        self.delete_text_box()
        self.show_search()

    def show_search(self):
        self.print_message("Now enter the word you want to search")
        self.print_message("And I'll show you all the results")
        self.print_message("Enter the word quit when you want to quit the app")
        word = self.input("")
        results = self.send_and_rec(word)
        self.show_results(results)
        self.entry.pack_forget()

    def show_results(self, results):
        self.text_box.pack_forget()
        self.text_box = tk.Text(self.root, height=4, width=150)
        self.text_box.pack()
        self.print_message("click the file name if you want to open the file")
        self.print_message("else keep searching")
        self.entry.pack_forget()
        results_list = results.split(', ')
        button_arr = []
        for button_text in results_list:
            button = tk.Button(self.root, text=button_text,
                               command=lambda name=button_text: self.show_file(name, button_arr), fg="blue")
            button.pack()
            button_arr.append(button)
        self.entry.pack()

    def show_file(self, file_name, button_arr):
        for button in button_arr:
            button.pack_forget()
        self.text_box.pack_forget()
        self.text_box = tk.Text(self.root, height=30, width=150)
        self.text_box.pack()
        self.rec_file(file_name)

    def rec_file(self, file_name):
        msg = "file_len: {}".format(file_name)
        length = self.send_and_rec(msg)
        length = int(length)
        msg = "send_file: {}".format(file_name)
        self.my_socket.send(msg.encode())
        text = ""
        for i in range(length):
            data = self.my_socket.recv(1024)
            data = data.decode()
            text += data
        self.print_message(text)

    def main(self):
        self.my_socket.connect((self.ip, 8820))

        self.root.geometry("1500x1500")

        self.text_box.pack()

        self.print_message("Hello, my name is ____")
        self.print_message("If you have an user enter sign in, else enter sign up")
        su_button = tk.Button(self.root, text="sign up", command=lambda: self.show_sign("sign_up", su_button, si_button))
        su_button.pack()
        si_button = tk.Button(self.root, text="sign in", command=lambda: self.show_sign("sign_in", su_button, si_button))
        si_button.pack()

        self.root.mainloop()


server_ip = '127.0.0.1'
client(server_ip).main()
