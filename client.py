import socket


class client:

    def __init__(self, ip):
        self.ip = ip

    # input details in sign up
    def input_sign(self, sign):
        print("Enter user name")
        user_name = input()
        print("Enter password")
        password = input()
        msg = "{}: {}, {}".format(sign, user_name, password)
        return msg

    # send a message and get a receive an answer
    def send_and_recv(self, msg, my_socket):
        msg = msg.encode()
        my_socket.send(msg)
        ans = my_socket.recv(1024)
        ans = ans.decode()
        return ans

    def main(self):
        my_socket = socket.socket()
        my_socket.connect((self.ip, 8820))

        print("Hello, my name is ____")
        print("If you have an user enter sign in, else enter sign up")
        sign = input()
        while sign != "sign up" and sign != "sign in":
            print("You have to enter sign up or sign in")
            sign = input()
        ser_ans = ""
        if sign == "sign up":
            while ser_ans != "You signed up":
                msg = self.input_sign("sign_up")
                ser_ans = self.send_and_recv(msg, my_socket)
                print(ser_ans)
        else:
            while ser_ans != "You signed in":
                msg = self.input_sign("sign_in")
                ser_ans = self.send_and_recv(msg, my_socket)
                print(ser_ans)

        print("Please enter the word you want to search")
        print("And I'll show you all the results")
        print("Enter the word quit when you want to quit the app")
        word = ""
        while word != 'quit':
            word = input()
            results = self.send_and_recv(word, my_socket)
            print(results)
        my_socket.close()


server_ip = '127.0.0.1'
client(server_ip).main()
