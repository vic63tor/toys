from __future__ import annotations

import os
from typing import Optional, List, Mapping, Any, Dict, Type
from dotenv import load_dotenv
from abc import ABC, abstractmethod
import requests
import json
import asyncio

from youdotcom.init import Init
from youdotcom.youchat import Chat
from EdgeGPT import Chatbot
from pydantic import BaseModel, Extra
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import SimpleSequentialChain
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.llms.utils import enforce_stop_tokens
from langchain.chains.base import Chain
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.docstore.document import Document
from langchain.llms.base import BaseLLM
from langchain.prompts.base import BasePromptTemplate
from langchain.text_splitter import TextSplitter
from langchain.llms import OpenAI
from openai.error import OpenAIError



load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
YOU_API_KEY = os.environ.get("YOU_API_KEY")
WOLFRAMALPHA_API_KEY = os.environ.get("WOLFRAMALPHA_API_KEY")
with open('prompts.json') as f:
    templates = json.loads(f.read())


class BotTemplate(ABC):
    @abstractmethod
    async def process_message(self, message) -> str:
        pass

    @abstractmethod
    @classmethod
    def reinit(cls, changes: list) -> Type:
        pass


class LangchainChatBot(LLMChain, BotTemplate):
    def __init__(self, mode, temperature=0.8):
        self.templates = self._read_prompts()
        super().__init__(
            llm=OpenAI(temperature=temperature),
            prompt=PromptTemplate(input_variables=["chat_history","question"], template=self.templates[mode]),
            verbose=True,
            memory=ConversationBufferMemory(memory_key="chat_history"),
        )

    @staticmethod
    def _read_prompts():
        with open('prompts.json') as f:
            f = f.read()
            ret = json.loads(f)
        return ret

    @classmethod
    def init_with_settings(cls, settings):
        mode = settings['mode']
        temperature = settings['temperature']
        return cls(mode, temperature)
    
    @staticmethod
    def save_to_json(templates):
        with open('prompts.json', 'w') as f:
            json.dump(templates, f)

    async def process_message(self, message) -> str:
        try:
            ret = await self.apredict(question=f"{message}").strip()
        except OpenAIError as e:
            print(e)
            ret = 'I overheated, I am about to die, please help. Let me rest a second.'
        return ret


class BingBot(Chatbot, BotTemplate):
    def __init__(self):
        super().__init__()

    async def process_message(self, message) -> str:
        try:
            resp = await self.ask(prompt=message)
            ret = resp["item"]["messages"][1]['adaptiveCards'][0]['body'][0]['text']
        except Exception as e:
            print(e)
            ret = 'I overheated, I am about to die, please help. Let me rest a second.'

class YouBot(Chat, BotTemplate):
    def __init__(self):
        self.driver = Init().driver
    
    def process_message(self, message) -> str:
        chat = Chat.send_message(driver=self.driver, message=message)
        return chat

        #return await super().process_message(message)

class TextBots:
    def __init__(self, bots, modes):
        self.bots: list = []
        self.modes: list = []

    @classmethod
    def initiate_modes(cls, modes):
        bots = []
        for mode in modes:
            match mode.casefold().split():
                case 'binggpt':
                    appendable = BingBot()
                case []:
                    pass
            bots.append(appendable)
        return cls(bots, modes)

    def respond(self, message):
        ret = []
        for bot in self.bots:
            ret.append(bot.process_message(message))
        return ret

    def reset(self):
        for bot in self.bots:
            del bot
        self._initiate_modes()

class MapReduceChain(Chain, BaseModel):
    """Map-reduce chain."""

    combine_documents_chain: BaseCombineDocumentsChain
    """Chain to use to combine documents."""
    text_splitter: TextSplitter
    """Text splitter to use."""
    input_key: str = "input_text"  #: :meta private:
    output_key: str = "output_text"  #: :meta private:

    @classmethod
    def from_params(
        cls, llm: BaseLLM, prompt: BasePromptTemplate, text_splitter: TextSplitter
    ) -> MapReduceChain:
        """Construct a map-reduce chain that uses the chain for map and reduce."""
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        reduce_chain = StuffDocumentsChain(llm_chain=llm_chain)
        combine_documents_chain = MapReduceDocumentsChain(
            llm_chain=llm_chain, combine_document_chain=reduce_chain
        )
        return cls(
            combine_documents_chain=combine_documents_chain, text_splitter=text_splitter
        )


    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Return output key.

        :meta private:
        """
        return [self.output_key]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        # Split the larger text into smaller chunks.
        texts = self.text_splitter.split_text(inputs[self.input_key])
        docs = [Document(page_content=text) for text in texts]
        outputs, _ = self.combine_documents_chain.combine_docs(docs)
        return {self.output_key: outputs}


async def main():
    bot = Chatbot()
    while True:
        prompt = input("prompt: ")
        resp = await bot.ask(prompt=prompt)
        resp_msg = resp["item"]["messages"][1]['adaptiveCards'][0]['body'][0]['text']
        print(resp)
        print(resp_msg)
    await bot.close()




#def gpt(inp, ToUserName):
#    if ToUserName not in llm_cache.keys():
#        template = templates['chatgpt']
#        prompt_template = PromptTemplate(input_variables=["chat_history","question"], template=template)
#        memory = ConversationBufferMemory(memory_key="chat_history")
#        llm_chain = LLMChain(
#            llm=llm,
#            prompt=prompt_template,
#            verbose=True,
#            memory=memory,
#        )
#        llm_cache[ToUserName] = llm_chain
#    else:
#        llm_chain = llm_cache[ToUserName]
#
#    ret = llm_chain.predict(question=f"{inp}").strip()
#    return ret
#

if __name__ == '__main__':
    asyncio.run(main())