from __future__ import annotations

from typing import Optional, List, Mapping, Any, Dict, Type, ClassVar, Union
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
import os
import requests
import json
import asyncio
import aiohttp
import inspect
import sys
from multiprocessing import Pool
from dataclasses import dataclass

from EdgeGPT import Chatbot
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
import openai
import llamacpp
from openai.error import OpenAIError
from langchain.llms import OpenAIChat

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class BotTemplate(ABC):
  is_available: ClassVar[bool]
  is_local: ClassVar[bool]
  require_template: ClassVar[bool] = False

  @abstractmethod
  async def aprocess_message(self, message: str) -> str:
    pass


@dataclass
class BotBuffer:
  bot: BotTemplate
  mode: str = None
  prompt: str = None
  temperature: float = None

  @property
  def name(self) -> str: return f'{self.bot.__name__} {self.mode}' if self.mode else self.bot.__name__
  def __repr__(self) -> str: return self.name
  def summon(self) -> BotTemplate: return self.bot(self.prompt) if self.mode else self.bot()






    


class ChatGPTBot(ChatOpenAI, BotTemplate):
  is_available: ClassVar[bool]= True if os.getenv("OPENAI_API_KEY") else False
  is_local: ClassVar[bool] = False

  def __init__(self):
    super(ChatOpenAI, self).__init__(model_name="gpt-3.5-turbo")


  async def aprocess_message(self, message) -> str:
    try: 
      ret = await super().agenerate([message])
      ret = ret.generations[0][0].text
    except OpenAIError as e:
      print(e)
      ret = 'I overheated, I am about to die, please help. Let me rest a second.'
    return ret




class LangchainBot(LLMChain, BotTemplate):
  is_available: ClassVar[bool] = True if os.getenv("OPENAI_API_KEY") else False
  is_local: ClassVar[bool] = False
  require_template: ClassVar[bool] = True

  def __init__(self, prompt, temperature=0.8):
    super().__init__(
        llm=OpenAI(temperature=temperature),
        prompt=PromptTemplate(input_variables=["chat_history","question"], template=prompt),
        verbose=False,
        memory=ConversationBufferMemory(memory_key="chat_history")
    )

  @classmethod
  def init_with_settings(cls, mode, temperature):
    return cls(mode, temperature)

  async def aprocess_message(self, message) -> str:
    try:
      ret = await self.apredict(question=f"{message}")
    except OpenAIError as e:
      print(e)
      ret = 'I overheated, I am about to die, please help. Let me rest a second.'
    return ret


class BingBot(Chatbot, BotTemplate):
  is_available = True if Path('settings/cookie.json').exists() else False
  is_local = False

  def __init__(self):
    print('initialized')
    super().__init__(cookiePath='settings/cookie.json')


  async def aprocess_message(self, message) -> str:
    try:
      resp = await self.ask(prompt=message)
      ret = resp["item"]["messages"][1]['adaptiveCards'][0]['body'][0]['text']
    except Exception as e:
      print(e)
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

class TextBotController:
  available_bots: List[BotBuffer] = None

  def __init__(self):
    if self.available_bots is None:
      self.load_bots()
    self.active_bots: Union[None, dict[str, BotTemplate]] = {}

  def activate_bots(self, selection: List[int]):
    for sel in selection:
      self.active_bots[sel] = self.available_bots[sel].summon()


  async def arespond(self, message: str) -> List[str]:
    ...
    # tasks = [asyncio.create_task(bot.aprocess_message(message=message)) for _, bot in self.active_bots.items() if bot.is_available]
    # return await asyncio.gather(*tasks)
  
  def respond(self, message: str) -> List[str]:
    ...


  def kill_bots(self):
    del self.active_bots

  @classmethod
  def load_bots(cls) -> List:
    with open('settings/prompts.json') as f:
      templates: Dict[str, str] = json.load(f)
    bots = []
    for _, bot in inspect.getmembers(sys.modules[__name__]):
      if inspect.isclass(bot) and issubclass(bot, BotTemplate) and bot != BotTemplate:
        bot: BotTemplate
        if bot.require_template:
          for mode, prompt in templates.items():
            bots.append(BotBuffer(bot=bot, mode=mode, prompt=prompt))
        else:
          bots.append(BotBuffer(bot=bot))
    cls.available_bots = bots
  
  def __str__(self): return f'available: {[[n, bot] for n, bot in enumerate(self.available_bots)]} active: {self.active_bots}'

# Print the list of subclasses

if __name__ == '__main__':
  t = TextBotController()
  t.activate_bots([1])
  import os
  import openai
  openai.organization = "org-NdwlPI1zbabscm4v19upumJn"
  openai.api_key = os.getenv("OPENAI_API_KEY")
  print(openai.Model.list())
  llm = OpenAI(temperature=0.9)
  text = "What would be a good company name for a company that makes colorful socks?"
  print(llm(text))
  # print(asyncio.run(t.arespond("what's the last word in the english language")))
  # import subprocess

  # completed_process = subprocess.run(['/llama.cpp/main -m ./models/7B/ggml-model-q4_0.bin -n 128'], capture_output=True)
  # print(completed_process.stdout.decode())

  #asyncio.run(main())
  '''
  modes = get_modes()
  print(modes)
  select = [0,1,3,4,5]
  t = TextBotController.summon_bots(select)
  '''