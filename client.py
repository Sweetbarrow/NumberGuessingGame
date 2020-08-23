from socket import *
import pickle

sock = socket(AF_INET, SOCK_STREAM)

addr = '127.0.0.1'
port = 5050
player_nickname = ""


def register_nickname(server_socket):
    print(server_socket.recv(4096).decode('utf8'))
    nickname = input(">>> ")
    server_socket.send(nickname.encode('utf8'))
    print(server_socket.recv(4096).decode('utf8'))
    recv_nickname = server_socket.recv(4096).decode('utf8')
    if nickname in recv_nickname:
        return recv_nickname


def challenge(server_socket):
    response = server_socket.recv(4096)
    answers = pickle.loads(response)
    print(answers)
    print(f"이번 라운드 내 숫자는 {answers[player_nickname]}입니다.")
    my_turn = 0
    notice_output = 0
    response = server_socket.recv(4096).decode('utf8')
    if response.startswith(player_nickname):
        my_turn = 1
    else:
        print(response)
        answer = input(">>> ")
        answer_obj = (player_nickname, answer)
        pickled_obj = pickle.dumps(answer_obj)
        server_socket.send(pickled_obj)
        response = server_socket.recv(4096).decode('utf8')
        if response == "CORRECT":
            print("맞췄습니다!")
            return
        elif response == "WRONG":
            print("틀렸습니다.")
            return
        else:
            print("ERROR")
    while my_turn == 1:
        while notice_output == 0:
            print("다른 플레이어들이 내 숫자를 맞추고 있습니다. 잠시 기다려주세요.")
            answer = 0
            answer_obj = (player_nickname, answer)
            pickled_obj = pickle.dumps(answer_obj)
            server_socket.send(pickled_obj)
            notice_output = 1
            continue
        response = server_socket.recv(4096).decode('utf8')
        if response == "ENDTURN":
            print("턴이 종료되었습니다.")
            return
        elif response == "WINEND":
            print("다른 사람들이 맞추지 못했습니다. 1점을 득점하였습니다. 턴이 종료되었습니다.")
            return
        else:
            continue


try:
    sock.connect((addr, port))
except ConnectionRefusedError:
    print("서버에 연결할 수 없습니다. 나중에 다시 시도하세요.")
    exit()
else:
    print(sock.recv(4096).decode('utf8'))

if player_nickname == "":
    player_nickname = register_nickname(sock)

state = 0
notice_output = 0

while state == 0:
    sock.send("STATE".encode('utf8'))
    response = sock.recv(4096).decode('utf8')
    if response == "WAIT":
        while notice_output == 0:
            print("다른 플레이어들을 기다리고 있습니다.")
            notice_output = 1
        continue
    elif response == "OK":
        state = 1

print("게임을 시작합니다.")

while state == 1:
    challenge(sock)
    try:
        response = sock.recv(4096).decode('utf8')
    except Exception as e:
        print(e)
    else:
        if response == "FINISH":
            print("게임이 종료되었습니다.")
            state = 0
        else:
            continue
