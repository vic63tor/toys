#!/usr/bin/env python3
import os
import pathlib
import re
import csv
from dataclasses import dataclass
# from typing import List, Dict, Optional
from datetime import datetime

import itchat
from itchat.content import TEXT, RECORDING, VIDEO, PICTURE
# from dotenv import load_dotenv

import text_processing 
import image_processing
import audio_processing
import pythonrepl
import utils
# from errors import IrrelevantMsgError

tmp_dir = os.path.join(pathlib.Path(__file__).parent, 'tmp/')
chat_history_dir = os.path.join(pathlib.Path(__file__).parent, 'chatbot_history/')
pic_dir = os.path.join(tmp_dir, 'qr.png')
DEBUG = os.getenv('DEBUG', 0)


@dataclass
class Message:
    msg: str
    time: datetime
    sender: str


chat_cache = {}


class ChatSession:
    start_phrase = ['robot', '机器人', 'start']
    terminate_phrase = ['88', 'exit']

    def __init__(self, user_info: dict, chatroom):
        self.user_info: dict = user_info
        self.chatroom: str = chatroom
        self.current_state: str = "init"
        self.chat_history: list = []
        self.prev_msg: str = ''
        self.textbot = None  # GETTER AND SETTER FOR PROPERTY
        self.imagebot = None
        self.pythonbot = None

    def _prepare_prev_msg(self, msg):
        recv_text = None
        if msg.type == 'Text':
            recv_text = msg['Text']
        elif msg.type == 'Recording':
            path_to_recording = save(msg)
            recv_text = audio_processing.transcribe(path_to_recording).strip()
            print(f'audio transcribed text: {recv_text}')

        if recv_text:
            self.prev_msg = recv_text
        else:
            self.prev_msg = msg.type

    @property
    def modes(self):
        pass
    #@modes.setter

    def _initiate_modes(self):
        self.textbot_modes = list(text_processing.templates.keys())
        self.imagebot_modes = None
        self.pythonbot = None

    def initialize_textbot(self, mode: str, temperature=0.8):
        self.textbot = text_processing.LangchainBot(prompt_=mode, temperature=temperature)

    def initialize_imagebot(self):
        self.imagebot = image_processing.to_BW()

    def initialize_python(self):
        self.pythonbot = pythonrepl.PythonREPL()

    
    def get_modes_for_print(self):
        self._initiate_modes()
        textbot_modes = '\n'.join([f'{n}. {mode}' for n, mode in enumerate(self.textbot_modes)])
        imagebot_modes = 'NOT AVAILABLE'
        pythonbot_modes = 'not available'
        ret = f'''** textbot **
{textbot_modes}

** imagebot **
{imagebot_modes}

** pythonbot **
{pythonbot_modes}

[MODE] [OPTION] 
e.g. textbot 1
'''
        return ret

    def get_all_phrases(self):
        return [*self.start_phrase, *self.terminate_phrase]

    def save_chat_history(self):
        filepath = os.path.join(
            chat_history_dir,
            f'{self.user_info["nickname"]}_in_{self.chatroom}.csv'
            )  # filepath = os.path.join(chat_history_dir+f'{self.user_info["ID"]}_in_{self.chatroom}')
        if os.path.exists(filepath):
            with open(filepath, 'a', newline='') as f:
                writer = csv.writer(f)
                for message in self.chat_history:
                    writer.writerow([str(message.time), message.sender, message.msg])

        else:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer
                writer.writerow(['time', 'sender', 'msg'])
                for message in self.chat_history:
                    writer.writerow([str(message.time), message.sender, message.msg])


@itchat.msg_register([TEXT, VIDEO, PICTURE, RECORDING], isFriendChat=True, isGroupChat=False, isMpChat=False)
def resp_handler(msg):
    #{'MsgId': '4408932538244882035', 'FromUserName': '@2ab1bc388bb8e329553e4e44e694a818aad8df0f3cb01b60fc2530d605fe2c31', 'ToUserName': 'filehelper', 'MsgType': 1, 'Content': 'djdjd', 'Status': 3, 'ImgStatus': 1, 'CreateTime': 1676613784, 'VoiceLength': 0, 'PlayLength': 0, 'FileName': '', 'FileSize': '', 'MediaId': '', 'Url': '', 'AppMsgType': 0, 'StatusNotifyCode': 0, 'StatusNotifyUserName': '', 'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 4408932538244882035, 'OriContent': '', 'EncryFileName': '', 'User': <User: {'UserName': 'filehelper', 'MemberList': <ContactList: []>}>, 'Type': 'Text', 'Text': 'djdjd'} 

    user = utils.compare_similarity(msg["FromUserName"], msg["ToUserName"], uid)
    contact = utils.compare_difference(msg["FromUserName"], msg["ToUserName"], uid)
    user_info = {'ID': user, 'nickname': itchat.search_friends(userName=user)['NickName']} 
    contact_info = {'ID': contact, 'nickname': 'filehelper' if contact == 'filehelper' else itchat.search_friends(userName=contact)['NickName']} # , 'nickname': itchat.search_friends(userName=contact)['NickName']
    chatroom= msg.user["UserName"] #problem
    isUserReceiving = True if msg["ToUserName"] == user else False

    if isUserReceiving:
        chat = cacheing_and_fetching(chatroom, contact_info)
    else:
        chat = cacheing_and_fetching(chatroom, user_info)

    chat._prepare_prev_msg(msg)
    chat.prev_msg = chat.prev_msg[:1].lower() + chat.prev_msg[1:] #lowercase the first letter

    if DEBUG:
        print(f'**** MESSAGE IN {msg.user["UserName"]} ****')
        print(f'MESSAGE: {chat.prev_msg}')
        print(f'IN CHATROOM: {chat.chatroom}')
        print(f'FROM USER: {chat.user_info["nickname"]}')
        print(chat.current_state)
        print(chat.prev_msg)
        for mes in chat.chat_history:
            print(str(mes))
        print('\n'*2)

    match chat.current_state:
        case 'init':
            if chat.prev_msg in chat.start_phrase:
                itchat.send(f'start phrase: {chat.start_phrase} \nend phrase: {chat.terminate_phrase}', toUserName=chat.chatroom)
                itchat.send(f'{chat.get_all_modes()}', toUserName=chat.chatroom)
                chat.current_state = 'await_mode'
        case 'await_mode':
            match re.split(r"\s+", chat.prev_msg):
                case ['textbot', n] if n.isdigit():
                    choice = int(n)
                    chat.initialize_textbot(chat.textbot_modes[choice])
                    itchat.send(f'initialized {chat.textbot_modes[choice]}', toUserName=chat.chatroom)
                    chat.current_state = 'textbot'
                case ['imagebot', n] if n.isdigit():
                    itchat.send('not implemented', toUserName=chat.chatroom)
                case ['pythonbot']: 
                    itchat.send('not implemented', toUserName=chat.chatroom)
                case _:
                    itchat.send('not acceptable [MODE] and/or [OPTION]\n MODE should be something-bot and OPTION should be a number\n Please refer to e.g.\n e.g. textbot 1', toUserName=chat.chatroom)
        case 'textbot':
            itchat.send('change # to change textbot mode\ne.g. change 2', toUserName=chat.chatroom)
            chat.chat_history.append(Message(msg=chat.prev_msg,time=str(datetime.fromtimestamp(msg.CreateTime)), sender=chat.user_info['nickname']))
            match re.split(r"\s+", chat.prev_msg):
                case prev_msg if utils.is_python_statement(' '.join(prev_msg)):
                    script = ' '.join(prev_msg)
                    itchat.send(f'{eval(script)}', toUserName=chat.chatroom)
                case prev_msg if prev_msg[0] in chat.terminate_phrase:
                    chat = hard_reset_ChatSession(chat)
                case['change', n] if n.isdigit():
                    chat.save_chat_history()
                    chat.chat_history = []
                    choice = int(chat.prev_msg)
                    del chat.textbot
                    chat.initialize_textbot(chat.modes[choice])
                    itchat.send(f'initialized {chat.modes[choice]}', toUserName=chat.chatroom)
                case['help']:
                    itchat.send(f'start phrase: {chat.start_phrase} \nend phrase: {chat.terminate_phrase}', toUserName=chat.chatroom)
                    itchat.send(f'{chat.format_modes_to_str()}', toUserName=chat.chatroom)
                case _:
                    send_message(chat=chat, message=f'🤖: {chat.textbot.respond(chat.prev_msg)}', toUserName=chat.chatroom)

        case 'imagebot':
            itchat.send('not implemented', toUserName=chat.chatroom)
            chat = hard_reset_ChatSession(chat)
        case 'pythonbot':
            chat.pythonrepl.push(chat.prev_msg)
            if chat.pythonrepl.ret_msg:
                itchat.send(chat.pythonrepl.ret_msg, toUserName=chat.chatroom)
            elif chat.pythonrepl.ret_err:
                itchat.send(chat.pythonrepl.ret_err, toUserName=chat.chatroom)
            chat = hard_reset_ChatSession(chat)
        case _:
            itchat.send('something is fucked...', toUserName=chat.chatroom)
            print('what the fuck')
                

def cacheing_and_fetching(chatroom, user_info):
    try:
        chat = chat_cache[f'{user_info["ID"]}_in_{chatroom}']
    except KeyError:
        chat_cache[f'{user_info["ID"]}_in_{chatroom}'] = ChatSession(user_info=user_info, chatroom=chatroom)
        chat = chat_cache[f'{user_info["ID"]}_in_{chatroom}']
    return chat
    
                
def clean():
    for f in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, f))
    #for file in files:
        #os.remove(file)


def save(msg):
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    path = os.path.join(tmp_dir, f'{msg["FileName"]}')
    #path = f'/tmp/{msg["FileName"]}'
    msg['Text'](path)
    print('file saved at ' + path)
    return path


def send_message(chat:ChatSession, message: str, toUserName):
    itchat.send(message, toUserName=toUserName)
    chat.chat_history.append(Message(msg=message,time=datetime.now(), sender=uid))

def hard_reset_ChatSession(ChatSession):
    if ChatSession.textbot is not None:
        del ChatSession.textbot
        ChatSession.textbot = None
    ChatSession.save_chat_history()
    ChatSession.chat_history = []
    ChatSession.current_state = 'init'
    return ChatSession

def soft_reset_ChatSession(ChatSession, mode): #need to implement for fast switching
    raise NotImplementedError
    




    




#@itchat.msg_register(PICTURE, isFriendChat=True, isGroupChat=False, isMpChat=False)
#def img_handler(msg):
#    print(msg)
#    assert msg.type == 'Picture'
#    path_to_photo = save(msg)
#    path_to_edited_photo = f'/tmp/edited_{msg["FileName"]}'
#    image_processing.toBlackAndWhite(path_to_photo, path_to_edited_photo)
#    print('edited file saved at ' + path_to_edited_photo)
#
#    if msg.user['UserName'] == msg["FromUserName"]: #run
#        itchat.send_image(path_to_edited_photo, toUserName=f'{msg.user["UserName"]}')
#    elif msg['ToUserName'] == 'filehelper': #test
#        print(itchat.send_image(path_to_edited_photo, toUserName='filehelper'))
#    
#
#        
#
#    #msg.Content
#    #msg.download
#
#





if __name__ == '__main__':
    uid = itchat.login(picDir=pic_dir)
    itchat.run(debug=True, blockThread=True)