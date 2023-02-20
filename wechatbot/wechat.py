#!/usr/bin/env python3
import os
import pathlib
import re
import json
import csv
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

import itchat
from itchat.content import TEXT, RECORDING, VIDEO, PICTURE

import text_processing 
import image_processing
import audio_processing
import utils
from errors import IrrelevantMsgError

chat_cache = {}
tmp_dir = os.path.join(pathlib.Path(__file__).parent, 'tmp/')
chat_history_dir = os.path.join(pathlib.Path(__file__).parent, 'chat_history/')
pic_dir = os.path.join(tmp_dir, 'qr.png')

DEBUG = os.getenv('DEBUG', 0)

#class wechatHandler:
#    def __init__(self):
#        chat_cache = {}
#        self.tmpDir = os.path.join(pathlib.Path(__file__).parent, 'tmp/')
#        picDir = os.path.join(tmpDir, 'qr.png')
#        itchat.auto_login(picDir=picDir)
#        itchat.run(debug=True, blockThread=True)
#

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

#@itchat.msg_register(RECORDING, isFriendChat=True, isGroupChat=False, isMpChat=False)
#def voice_handler(msg):
#    path_to_recording = save(msg)
#    recv_text = audio_processing.transcribe(path_to_recording)
#
#    if msg.user['UserName'] == msg["FromUserName"]: #run
#        try:
#            ret_text = text_processing.gpt(recv_text, msg.user["UserName"])
#            return '🤖: ' + ret_text
#        except: #text_processing.OpenAI.error.RateLimitError
#            return '🤖: ' + 'im overheating, help'
#
#    elif msg['ToUserName'] == 'filehelper': #test
#        ret_text = text_processing.gpt(recv_text, msg["ToUserName"])
#        itchat.send('🤖: ' + f'{ret_text}', toUserName='filehelper')

#new_message = {'sender': msg["FromUserName"], 'receiver': msg["ToUserName"], 'msgType': msg.type, 'chatname': msg.user['UserName'], 'timestamp': msg['CreateTime']}

@dataclass
class Message:
    msg: str
    time: datetime
    sender: str


class ChatSession:
    start_phrase = ['robot', '机器人', 'start']
    end_phrase = ['goodbye', '88', 'end']
    terminate_phrase = ['fuck']

    def __init__(self, user: str, contact: str): 
        self.user_info = {'ID': user, 'nickname': itchat.search_friends(user)['NickName']} # , 'nickname': itchat.search_friends(userName=user)['NickName']
        self.contact_info = {'ID': contact, 'nickname': 'filehelper' if contact == 'filehelper' else itchat.search_friends(contact)['NickName']} # , 'nickname': itchat.search_friends(userName=contact)['NickName']
        self.current_state = "init"
        self.chat_history = []
        self.prev_msg: str
        self.textbot = None
        self.imagebot = None
        #self.pythonrepl = None need a python session here
        self.modes = [*text_processing.templates.keys()] # and picture modes
    
    def _update_chat_history(self, msg):
        recv_text = None
        if msg.type == 'Text':
            recv_text = msg['Text']
        elif msg.type == 'Recording':
            path_to_recording = save(msg)
            recv_text = audio_processing.transcribe(path_to_recording).strip()
            print(f'audio transcribed text: {recv_text}')

        sender = self.contact_info if msg['FromUserName'] == self.contact_info['ID'] else self.user_info

        if recv_text:
            self.chat_history.append(Message(msg=recv_text, time=datetime.fromtimestamp(msg.CreateTime), sender=sender))
            self.prev_msg = recv_text
        else:
            self.chat_history.append(Message(msg=msg.type, time=datetime.fromtimestamp(msg.CreateTime), sender=sender))
            self.prev_msg = None

    def initialize_textbot(self, mode: str, temperature=0.8):
        with open("prompts.json", "r") as f:
            f = f.read()
            templates = json.loads(f)
        prompt = templates[mode]
        self.textbot = text_processing.ConversationBot(prompt_=prompt, temperature=temperature)

    def initialize_imagebot(self):
        self.imagebot = image_processing.to_BW()

    def initialize_python(self):
        pass #initialize repl
    
    def format_modes_to_str(self):
        return '\n'.join([f'{n}. {mode}' for n, mode in enumerate(self.modes)])
    def get_all_phrases(self):
        return [*self.end_phrase, *self.start_phrase, *self.terminate_phrase]
    def save_chat_history(self):
        filepath = os.path.join(chat_history_dir+f'{self.contact_info["ID"]}.csv')
        with open(filepath, 'a+', newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(['time', 'sender', 'msg'])
            for message in self.chat_history:
                writer.writerow([str(message.time), message.sender, message.msg])









    #def append_history()

@itchat.msg_register([TEXT, VIDEO, PICTURE, RECORDING], isFriendChat=True, isGroupChat=False, isMpChat=False)
def resp_handler(msg):
    #{'MsgId': '4408932538244882035', 'FromUserName': '@2ab1bc388bb8e329553e4e44e694a818aad8df0f3cb01b60fc2530d605fe2c31', 'ToUserName': 'filehelper', 'MsgType': 1, 'Content': 'djdjd', 'Status': 3, 'ImgStatus': 1, 'CreateTime': 1676613784, 'VoiceLength': 0, 'PlayLength': 0, 'FileName': '', 'FileSize': '', 'MediaId': '', 'Url': '', 'AppMsgType': 0, 'StatusNotifyCode': 0, 'StatusNotifyUserName': '', 'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 4408932538244882035, 'OriContent': '', 'EncryFileName': '', 'User': <User: {'UserName': 'filehelper', 'MemberList': <ContactList: []>}>, 'Type': 'Text', 'Text': 'djdjd'} 
    try:
        chat = chat_cache[msg.user["UserName"]]
    except KeyError:
        user = utils.compare_similarity(msg["FromUserName"], msg["ToUserName"], uid)
        contact = utils.compare_difference(msg["FromUserName"], msg["ToUserName"], uid)
        isReceiving = True if msg["ToUserName"] == user else False
        if contact != 'filehelper':
            contact_nickname = itchat.search_friends(contact)['NickName']
        else:
            contact_nickname = contact
        user_nickname = itchat.search_friends(user)['NickName']
        chat_cache[msg.user["UserName"]] = ChatSession(user=user, contact=contact)
        chat = chat_cache[msg.user["UserName"]]

    chat._update_chat_history(msg)

    if DEBUG:
        print(f'**** MESSAGE IN {msg.user["UserName"]} ****')
        print(f'MESSAGE: {chat.prev_msg}')
        print(chat.current_state)
        print(chat.prev_msg)
        for mes in chat.chat_history:
            print(str(mes))
        print(msg)
        print('\n'*2)

    # should start with a match case to be able to use this as a python interpreter.

    match chat.current_session:
        case 'init':
            if chat.prev_msg.lower() in chat.start_phrase:
                itchat.send(f'start phrase: {chat.start_phrase} \nend phrase: {chat.terminate_phrase}', toUserName=chat.contact_info['ID'])
                itchat.send(f'{chat.format_modes_to_str()}', toUserName=chat.contact_info['ID'])
                chat.current_state = 'await_mode'
        case 'await_mode':
            choice = int(chat.prev_msg)
            chat.initialize_textbot(chat.modes[choice])
            itchat.send(f'initialized {chat.modes[choice]}', toUserName=chat.contact_info['ID'])
            chat.current_state = 'textbot'
        case 'textbot':
            chat.prev_msg = chat.prev_msg[:1].lower() + chat.prev_msg[1:] #lowercase the first letter
            match re.split(r"\s+", chat.prev_msg):
                case prev_msg if utils.is_python_statement(' '.join(prev_msg)):
                    script = ' '.join(prev_msg)
                    itchat.send(f'{eval(script)}', toUserName=chat.contact_info['ID'])
                case prev_msg if prev_msg[0] in chat.terminate_phrase:
                    chat = hard_reset_ChatSession(chat)
                case['change', n] if n.isdigit():
                    choice = int(chat.prev_msg)
                    del chat.textbot
                    chat.initialize_textbot(chat.modes[choice])
                    itchat.send(f'initialized {chat.modes[choice]}', toUserName=chat.contact_info['ID'])
                case['help']:
                    itchat.send(f'start phrase: {chat.start_phrase} \nend phrase: {chat.terminate_phrase}', toUserName=chat.contact_info['ID'])
                    itchat.send(f'{chat.format_modes_to_str()}', toUserName=chat.contact_info['ID'])

                    

                

        

        
        case _:
            print('what the fuck')

    match re.split(r"\s+", chat.prev_msg):
        case ['python']:
            pass #init python repl and change chat.current_session = 'py_repl'

        case prev_msg if utils.is_python_statement(' '.join(prev_msg)):
            script = ' '.join(prev_msg)
            itchat.send(f'{eval(script)}', toUserName=chat.contact_info['ID'])

        case prev_msg if len(prev_msg) == 1 and prev_msg[0].lower() in chat.start_phrase and chat.current_state == 'init':
            itchat.send(f'start phrase: {chat.start_phrase} \nend phrase: {chat.terminate_phrase}', toUserName=chat.contact_info['ID'])
            itchat.send(f'{chat.format_modes_to_str()}', toUserName=chat.contact_info['ID'])
            chat.current_state = 'await_mode'
        
        case prev_msg if chat.current_state == 'await_mode': #currently only textbot
            choice = int(chat.prev_msg)
            chat.initialize_textbot(chat.modes[choice])
            itchat.send(f'initialized {chat.modes[choice]}', toUserName=chat.contact_info['ID'])
            chat.current_state = 'textbot'
        
        case prev_msg if prev_msg[0].lower() not in chat.get_all_phrases() and chat.current_state == 'textbot':
            send_message(chat=chat, message=f'🤖: {chat.textbot.respond(chat.prev_msg)}', toUserName=chat.contact_info['ID'])
        
        case ['Change', 'to', mode] if chat.current_state == 'textbot':
            chat = soft_reset_ChatSession(chat, mode)


        case prev_msg if ' '.join(prev_msg) in chat.end_phrase:
            match chat.current_state:
                case 'textbot':
                    chat = soft_reset_ChatSession(chat, mode)

        case prev_msg if ' '.join(prev_msg) in chat.terminate_phrase:
            chat = hard_reset_ChatSession(chat)

        case _:
            match chat.current_state:
                case 'init':
                    print(chat.prev_msg)
                    #raise IrrelevantMsgError(message=chat.prev_msg)
                case 'await_mode':
                    itchat.send('not a proper mode', toUserName=chat.contact_info['ID'])
                case _:
                    itchat.send(f'fuck you {uid}', toUserName=chat.contact_info['ID'])


                




    '''
    if chat.current_state == 'init':
        match chat.prev_msg:
            case prev_msg if prev_msg in chat.start_phrase:
                itchat.send(f'start phrase: {chat.start_phrase} \nend phrase: {chat.end_phrase}', toUserName=chat.contact_info['ID'])
                itchat.send(f'{chat.format_modes_to_str()}', toUserName=chat.contact_info['ID'])
                chat.current_state = 'await_mode'
    elif chat.current_state == 'await_mode':
        try:
            choice = int(chat.prev_msg)
            itchat.send(f'initialized {chat.modes[choice]}', toUserName=chat.contact_info['ID'])
            chat.initialize_textbot(chat.modes[choice])
            chat.current_state = 'textbot'
        except:
            itchat.send('Not a number. Only give number. 🤖 want number', toUserName=chat.contact_info['ID'])
    elif chat.current_state == 'textbot':
        match chat.prev_msg.split():
            case prev_msg if ' '.join(prev_msg) in chat.end_phrase:
                #end session?
                chat.current_state == 'init'
            case prev_msg if utils.is_python_statement(prev_msg):
                eval(prev_msg)
            case _:
                itchat.send(f'🤖: {chat.textbot.respond(chat.prev_msg)}', toUserName=chat.contact_info['ID'])

    '''
                
                

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
    




    




#@itchat.msg_register(VIDEO, isFriendChat=True, isGroupChat=False, isMpChat=False)
#def video_handler(msg):
#    print(msg)
#
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
#@itchat.msg_register(TEXT, isFriendChat=True, isGroupChat=False, isMpChat=False)
#def text_handler(msg):
#    assert msg.type == 'Text'
#    "{'MsgId': '996602409339740894', 'FromUserName': '@961fa75be5c4dda00a2859825008e077140d125f4acf7f2d349be116ff2272d7', 'ToUserName': '@4b50fbae07ee174f7b948676d1cc540b9bf0655deb2a5e8601234cebd041f5dd', 'MsgType': 1, 'Content': '', 'Status': 3, 'ImgStatus': 1, 'CreateTime': 1674491144, 'VoiceLength': 0, 'PlayLength': 0, 'FileName': '', 'FileSize': '', 'MediaId': '', 'Url': '', 'AppMsgType': 0, 'StatusNotifyCode': 0, 'StatusNotifyUserName': '', 'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 996602409339740894, 'OriContent': '', 'EncryFileName': '', 'User': <User: {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': '@961fa75be5c4dda00a2859825008e077140d125f4acf7f2d349be116ff2272d7', 'NickName': ',', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=806684198&username=@961fa75be5c4dda00a2859825008e077140d125f4acf7f2d349be116ff2272d7&skey=@crypt_26bb3c43_357694c3946b0173623209d6a77f19e8', 'ContactFlag': 3, 'MemberCount': 0, 'RemarkName': '', 'HideInputBarFlag': 0, 'Sex': 0, 'Signature': '', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': '', 'PYQuanPin': '', 'RemarkPYInitial': '', 'RemarkPYQuanPin': '', 'StarFriend': 0, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 236325, 'Province': '', 'City': '', 'Alias': '', 'SnsFlag': 257, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}>, 'Type': 'Text', 'Text': '如果对方相信很多事'}"
#    "{'MsgId': '2943387513538162683', 'FromUserName': '@4b50fbae07ee174f7b948676d1cc540b9bf0655deb2a5e8601234cebd041f5dd', 'ToUserName': '@961fa75be5c4dda00a2859825008e077140d125f4acf7f2d349be116ff2272d7', 'MsgType': 1, 'Content': '', 'Status': 3, 'ImgStatus': 1, 'CreateTime': 1674491150, 'VoiceLength': 0, 'PlayLength': 0, 'FileName': '', 'FileSize': '', 'MediaId': '', 'Url': '', 'AppMsgType': 0, 'StatusNotifyCode': 0, 'StatusNotifyUserName': '', 'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 2943387513538162683, 'OriContent': '', 'EncryFileName': '', 'User': <User: {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': '@961fa75be5c4dda00a2859825008e077140d125f4acf7f2d349be116ff2272d7', 'NickName': ',', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=806684198&username=@961fa75be5c4dda00a2859825008e077140d125f4acf7f2d349be116ff2272d7&skey=@crypt_26bb3c43_357694c3946b0173623209d6a77f19e8', 'ContactFlag': 3, 'MemberCount': 0, 'RemarkName': '', 'HideInputBarFlag': 0, 'Sex': 0, 'Signature': '', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': '', 'PYQuanPin': '', 'RemarkPYInitial': '', 'RemarkPYQuanPin': '', 'StarFriend': 0, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 236325, 'Province': '', 'City': '', 'Alias': '', 'SnsFlag': 257, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}>, 'Type': 'Text', 'Text': '不对'}"
#    #print(msg)
#
#
#    recv_text = msg['Text']
#    #print(msg.user['UserName'])
#    #print(msg['FromUserName'])
#
#    if msg.user['UserName'] == msg["FromUserName"]: #run
#        try:
#            ret_text = text_processing.gpt(recv_text, msg.user["UserName"])
#            return '🤖: ' + ret_text
#        except: #text_processing.OpenAI.error.RateLimitError
#            return '🤖: ' + 'im overheating, help'
#
#    elif msg['ToUserName'] == 'filehelper': #test
#        ret_text = text_processing.gpt(recv_text, msg["ToUserName"])
#        itchat.send('🤖: ' + f'{ret_text}', toUserName='filehelper')
#
#
#






if __name__ == '__main__':
    #save('hi')
    uid = itchat.login(picDir=pic_dir)
    itchat.run(debug=True, blockThread=True)
    
    #itchat.dump_login_status(fileDir=tmpDir+'dump')
    '''
    self.loginInfo['InviteStartCount'] = int(dic['InviteStartCount'])
    self.loginInfo['User'] = wrap_user_dict(utils.struct_friend_info(dic['User']))
    self.memberList.append(self.loginInfo['User'])
    self.loginInfo['SyncKey'] = dic['SyncKey']
    self.loginInfo['synckey'] = '|'.join(['%s_%
    '''