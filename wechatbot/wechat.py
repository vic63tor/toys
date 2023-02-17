#!/usr/bin/env python3
import os
import pathlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import datetime

import itchat
from itchat.content import TEXT, RECORDING, VIDEO, PICTURE

import text_processing 
import image_processing
import audio_processing

chat_cache = {}
tmpDir = os.path.join(pathlib.Path(__file__).parent, 'tmp/')
picDir = os.path.join(tmpDir, 'qr.png')

#class wechatHandler:
#    def __init__(self):
#        chat_cache = {}
#        self.tmpDir = os.path.join(pathlib.Path(__file__).parent, 'tmp/')
#        picDir = os.path.join(tmpDir, 'qr.png')
#        itchat.auto_login(picDir=picDir)
#        itchat.run(debug=True, blockThread=True)
#

def clean():
    for f in os.listdir(tmpDir):
        os.remove(os.path.join(tmpDir, f))
    #for file in files:
        #os.remove(file)


def save(msg):
    if not os.path.exists(tmpDir):
        os.mkdir(tmpDir)
    path = os.path.join(tmpDir, f'{msg["FileName"]}')
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
    time: datetime.datetime
    sender: str


class ChatSession:
    start_phrase = ['Hello robot', 'Robot', '机器人']
    quit_phrase = ['Goodbye robo', 'goodbye robot', '886']
    options = f'🤖: Gib number pls: number option\n 1. Chatbot {text_processing.templates.keys()}\n 2. Picture editing '

    def __init__(self, sender: str, receiver: str, chatname: str): #instead of sender and receiver, determine who you are and define the other person as other.
        self.sender = sender
        self.receiver = receiver
        self.chatname = chatname
        self.current_state = "init"
        self.chat_history: List[Message] = []
        self.prev_msg: str
        self.textbot_state: text_processing.ConversationBot
    
    def _update_chat_history(self, msg):
        if msg.type == 'Text':
            recv_text = msg['Text']
        elif msg.type == 'Recording':
            path_to_recording = save(msg)
            recv_text = audio_processing.transcribe(path_to_recording).strip()

        if recv_text:
            self.chat_history.append(Message(msg=recv_text, time=msg.CreateTime, sender=self.sender))
            self.prev_msg = recv_text
        else:
            self.chat_history.append(Message(msg=msg.type, time=msg.CreateTime, sender=self.sender))
            self.prev_msg = None






    #def append_history()

@itchat.msg_register([TEXT, VIDEO, PICTURE, RECORDING], isFriendChat=True, isGroupChat=False, isMpChat=False)
def resp_handler(msg):
    '''
    {'MsgId': '4408932538244882035', 'FromUserName': '@2ab1bc388bb8e329553e4e44e694a818aad8df0f3cb01b60fc2530d605fe2c31', 'ToUserName': 'filehelper', 'MsgType': 1, 'Content': 'djdjd', 'Status': 3, 'ImgStatus': 1, 'CreateTime': 1676613784, 'VoiceLength': 0, 'PlayLength': 0, 'FileName': '', 'FileSize': '', 'MediaId': '', 'Url': '', 'AppMsgType': 0, 'StatusNotifyCode': 0, 'StatusNotifyUserName': '', 'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 4408932538244882035, 'OriContent': '', 'EncryFileName': '', 'User': <User: {'UserName': 'filehelper', 'MemberList': <ContactList: []>}>, 'Type': 'Text', 'Text': 'djdjd'} 
    if new_message['msgType'] == 'Text':
        recv_text = msg['Text']
    elif new_message['msgType'] == 'Recording':
        path_to_recording = save(msg)
        recv_text = audio_processing.transcribe(path_to_recording).strip()
'''

    try:
        chat = chat_cache[msg.user["UserName"]]
        chat._update_chat_history(msg)
    except KeyError:
        chat_cache[msg.user["UserName"]] = ChatSession(msg["FromUserName"], msg["ToUserName"], msg.user['UserName'])
        chat = chat_cache[msg.user["UserName"]]

    print('-'*8)
    print(msg, '\n')
    print(chat.current_state)
    print(chat.prev_msg)
    print('-'*8, '\n')



    


    if chat.prev_msg in chat.start_phrase and chat.current_state == 'init':


        itchat.send('fuck', toUserName=chat.name)
        chat.state = 'await_inst'
    elif chat.state == 'await_inst':
        recv_text
        print(recv_text.split())






    




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
    uid = itchat.login(picDir=picDir)
    print(uid)
    itchat.run(debug=True, blockThread=True)
    itchat.s
    
    #itchat.dump_login_status(fileDir=tmpDir+'dump')
    '''
    self.loginInfo['InviteStartCount'] = int(dic['InviteStartCount'])
    self.loginInfo['User'] = wrap_user_dict(utils.struct_friend_info(dic['User']))
    self.memberList.append(self.loginInfo['User'])
    self.loginInfo['SyncKey'] = dic['SyncKey']
    self.loginInfo['synckey'] = '|'.join(['%s_%
    '''