import os
from typing import Optional, List, Mapping, Any
from dotenv import load_dotenv
import requests
import json

#import wolframalpha
#from wolframclient.evaluation import WolframLanguageSession
#from wolframclient.language import wl, wlexpr

from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import SimpleSequentialChain
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.llms.utils import enforce_stop_tokens

from langchain.llms import OpenAI

#llm = OpenAI(model_name="text-ada-001", n=2, best_of=2)

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WOLFRAMALPHA_API_KEY = os.environ.get("WOLFRAMALPHA_API_KEY")
with open('prompts.json') as f:
    templates = json.loads(f.read())



#wa_session = WolframLanguageSession()
#def wa():
#    # Taking input from user
#    question = input('Question: ')
#    
#    client = wolframalpha.Client(WOLFRAMALPHA_API_KEY)
#    res = client.query(question)
#    ret = next(res.results).text
#    
#    return ret

#def wa_client():
#    ocean = wlexpr('GeoNearest[Entity["Ocean"], Here]')
#    return wa_session.evaluate(ocean)

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
        return self.predict(question=f"{inp}").strip()
    
    def _reset(self):
        with open('prompts.json') as f:
            self.templates = json.load(f)
        self.cache = {}













    



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