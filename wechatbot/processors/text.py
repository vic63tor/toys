from __future__ import annotations

import os
from typing import Optional, List, Mapping, Any, Dict, Type
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from collections import defaultdict
import requests
import json
import asyncio
import aiohttp

from youdotcom.init import Init
from youdotcom.youchat import Chat
from EdgeGPT import Chatbot
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from openai.error import OpenAIError
from langchain.llms import OpenAIChat

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
YOU_API_KEY = os.environ.get("YOU_API_KEY")
WOLFRAMALPHA_API_KEY = os.environ.get("WOLFRAMALPHA_API_KEY")
with open('../prompts.json') as f:
  templates = json.loads(f.read())


class BotTemplate(ABC):
  name = None

  @abstractmethod
  async def process_message(self, name, message) -> str:
    pass



class ChatGPTBot(OpenAIChat, BotTemplate):
  name = 'ChatGPT'
  def __init__(self):
    super().__init__(model_name="gpt-3.5-turbo")

  async def process_message(self, name, message) -> str:
    try: 
      ret = await super().agenerate([message])
      ret = ret.generations[0][0].text
      ret = f'**{name}**\n{ret}'
    except OpenAIError as e:
      print(name, e)
      ret = 'I overheated, I am about to die, please help. Let me rest a second.'
    return ret




class LangchainBot(LLMChain, BotTemplate):
  def __init__(self, mode, temperature=0.8):
    with open('../prompts.json') as f:
      templates = json.loads(f.read())
    super().__init__(
        llm=OpenAI(temperature=temperature),
        prompt=PromptTemplate(input_variables=["chat_history","question"], template=templates[mode]),
        verbose=True,
        memory=ConversationBufferMemory(memory_key="chat_history"),
    )

  @classmethod
  def init_with_settings(cls, mode, temperature):
    return cls(mode, temperature)

  async def process_message(self, name, message) -> str:
    try:
      ret = await self.apredict(question=f"{message}")
      ret = f'**{name}**\n{ret}'
    except OpenAIError as e:
      print(name, e)
      ret = 'I overheated, I am about to die, please help. Let me rest a second.'
    return ret


class BingBot(Chatbot, BotTemplate):
  name = 'BingGPT'
  def __init__(self):
    super().__init__()

  async def process_message(self, name, message) -> str:
    try:
      resp = await self.ask(prompt=message)
      ret = resp["item"]["messages"][1]['adaptiveCards'][0]['body'][0]['text']
      ret = f'**{name}**\n{ret}'
    except Exception as e:
      print(name, e)
      ret = 'I overheated, I am about to die, please help. Let me rest a second.'
    return ret

#class AsyncChat(Chat):
#    async def send_message_async(message: str, context=None, context_form_file=None, debug=False, webdriver_path=None, headless=True, keep=False, api_key: str = str(os.environ.get("BETTERAPI_API_KEY"))):
#        if api_key == "" or None:
#            raise ValueError("Chat.api_key must be set before making a request. Don't have an api key? get one on https://api.betterapi.net/")
#        response = await requests.get(f"https://api.betterapi.net/youdotcom/chat?message={message}&key={api_key}")
#        data = response.json()
#        return data

#class YouBot(AsyncChat, BotTemplate):
#    def __init__(self):
#        self.driver = Init().driver
#
#    def process_message(self, message) -> str:
#        chat = Chat.send_message(driver=self.driver, message=message)
#        return chat

    #return await super().process_message(message)

def get_modes() -> dict:
    with open('../prompts.json') as f:
      prompt_names = ['langchain '+i for i in json.loads(f.read()).keys()]
    return {n:mode for n,mode in enumerate(["ChatGPT", "BingGPT", *prompt_names])}


class TextBots:
  modes = get_modes()
  def __init__(self, active_bots):
    self.active_bots: dict = active_bots

  @classmethod
  def initiate_bots(cls, modes: dict, selection: List[int]):
    bots = defaultdict(str)
    for bot in selection:
      match modes[bot].split():
        case ['ChatGPT']:
          bot_inst = ChatGPTBot()
        case ['BingGPT']:
          bot_inst = BingBot()
        case ['langchain', *rest]:
          bot_inst = LangchainBot(' '.join(rest))
      bots[modes[bot]] = bot_inst
    return cls(bots)

  async def respond(self, message):
    tasks = []
    for name, bot in self.active_bots.items():
      task = asyncio.create_task(bot.process_message(name, message))
      tasks.append(task)
    ret = await asyncio.gather(*tasks)
    print('gathering done')
    for r in ret:
      print(r)
    print('print done')

  def reset(self):
    for bot in self.active_bots.values():
      del bot
    self.initiate_bots()


if __name__ == '__main__':
  #asyncio.run(main())
  modes = get_modes()
  select = [0,1,3,4,5]
  t = TextBots.initiate_bots(modes, select)
  asyncio.run(t.respond(""))