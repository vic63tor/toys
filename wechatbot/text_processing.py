from __future__ import annotations

import os
from typing import Optional, List, Mapping, Any, Dict
from dotenv import load_dotenv
import requests
import json

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


load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WOLFRAMALPHA_API_KEY = os.environ.get("WOLFRAMALPHA_API_KEY")
with open('prompts.json') as f:
    templates = json.loads(f.read())

class ConversationBot(LLMChain):
    def __init__(self, prompt_, temperature=0.8):
        super().__init__(
            llm=OpenAI(temperature=temperature),
            prompt=PromptTemplate(input_variables=["chat_history","question"], template=prompt_),
            verbose=True,
            memory=ConversationBufferMemory(memory_key="chat_history"),
        )
        #self.name = None
        #template = self.tempaltes[self.default] if self.name == None else self.tempaltes[self.name]


    

    @staticmethod
    def _read_prompts():
        with open('prompts.json') as f:
            f = f.read()
            ret = json.loads(f)
        return ret
    @classmethod
    def init_new_template(cls, name, prompt):
        cls.templates[name] = prompt
    
    @classmethod
    def del_template(self, name):
        del self.templates[name]
    
    @staticmethod
    def save_to_json(templates):
        with open('prompts.json', 'w') as f:
            json.dump(templates, f)
    

    def respond(self, inp):
        '''
  File "/opt/homebrew/lib/python3.11/site-packages/openai/api_requestor.py", line 620, in _interpret_response
    self._interpret_response_line(
  File "/opt/homebrew/lib/python3.11/site-packages/openai/api_requestor.py", line 663, in _interpret_response_line
    raise error.ServiceUnavailableError(
openai.error.ServiceUnavailableError: The server is overloaded or not ready yet.
        '''
        try:
            ret = self.predict(question=f"{inp}").strip()
        except Exception as e:
            print(e)
            ret = 'I overheated, I am about to die, please help. Let me rest a second.'
        return ret

    def _reset(self):
        with open('prompts.json') as f:
            self.templates = json.load(f)
        self.cache = {}






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
    with open('prompts.json') as f:
        my_templates = json.loads(f.read())
    my_templates = my_templates['chatgpt']
    bot1 = ConversationBot(prompt_=my_templates)



    #print('gpt response: ', gpt("tell me a story in 10 words", 'retard'))
    #print('gpt response: ', gpt("what was the first word from your previous response", 'retard'))
    #print('gpt response: ', gpt("what was the first word from your previous response", 'not_retard'))