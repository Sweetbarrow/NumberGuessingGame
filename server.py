from socket import *
import pickle
import random
import threading

sock = socket(AF_INET, SOCK_STREAM)

addr = '127.0.0.1'
port = 5050

try:
    sock.bind((addr, port))
except error as e:
    print("서버 오류 발생:", e)

sock.listen(5)

player_list = []
answers = {}
scores = {}


def register_nickname(client_socket):
    client_socket.send("닉네임을 입력하세요:".encode('utf8'))
    while True:
        nickname = client_socket.recv(4096).decode('utf8')
        nickname = nickname + "#" + f"{random.randint(0, 9999):04}"
        if nickname in player_list:
            client_socket.send("이미 존재하는 닉네임입니다. 다른 닉네임을 입력하세요.".encode('utf8'))
            continue
        else:
            client_socket.send(f"환영합니다, {nickname}님".encode('utf8'))
            client_socket.send(nickname.encode('utf8'))
            return nickname


def score_init():
    for player in player_list:
        scores[player] = 0
    return


def answer_init():
    for player in player_list:
        answers[player] = random.randint(1, 3)
    return


def challenge(client_socket):
    answer_init()
    current_player = ""
    wrong_count = 0
    response = None
    answer = None
    send_obj = pickle.dumps(answers)
    client_socket.send(send_obj)
    for player in player_list:
        try:
            client_socket.send(f"{player}님의 숫자를 맞춰주세요.".encode('utf8'))
            response = client_socket.recv(4096)
        except ConnectionResetError:
            raise ConnectionResetError
        except OSError:
            print(client_socket, response)
            raise OSError
        else:
            print(answers)
            try:
                answer = pickle.loads(response, encoding='utf8')
            except TypeError:
                print(client_socket, response)
                raise TypeError
            if int(answer[1]) == 0:
                print(answers[player])
                client_socket.send("ENDTURN".encode('utf8'))
            elif int(answer[1]) == answers[player]:
                print(answers[player])
                client_socket.send("CORRECT".encode('utf8'))
                scores[answer[0]] += 1
            else:
                print(answers[player])
                client_socket.send("WRONG".encode('utf8'))
                wrong_count += 1

            if wrong_count == (len(player_list) - 1):
                scores[current_player] += 1
                client_socket.send("WINEND".encode('utf8'))
            else:
                client_socket.send("ENDTURN".encode('utf8'))


def client_handler(client_socket, client_address):
    client_socket.send("서버에 연결되었습니다.".encode('utf8'))
    client_nickname = register_nickname(client_socket)
    player_list.append(client_nickname)
    try:
        while True:
            message = client_socket.recv(4096).decode('utf8')
            if message == "STATE" and len(player_list) >= 3:
                client_socket.send("OK".encode('utf8'))
                score_init()
                break
            elif message == "STATE" and len(player_list) < 3:
                client_socket.send("WAIT".encode('utf8'))
                continue
    except ConnectionResetError:
        print("클라이언트 연결 종료:", client_address)
        client_socket.close()
        try:
            player_list.remove(client_nickname)
        except ValueError:
            pass
    while True:
        try:
            challenge(client_socket)
        except ConnectionResetError as cre:
            print(cre)
            print("클라이언트 연결 종료:", client_address)
            client_socket.close()
            try:
                player_list.remove(client_nickname)
            except ValueError as ve:
                print("ValueError 오류 발생:", ve)
        except OSError as ose:
            print("OSError 오류 발생:", ose, client_address)
        except TypeError as te:
            print("TypeError 오류 발생:", te, client_address)
        except Exception as e:
            print(e)


print("서버를 시작합니다.")


while True:
    client_sock, client_addr = sock.accept()
    print("클라이언트 접속:", client_addr)
    threading.Thread(target=client_handler, args=(client_sock, client_addr)).start()
