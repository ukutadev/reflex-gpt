#import time
#import asyncio
import reflex as rx
import sqlmodel
#from reflex_gpt.models import ChatSession as Chatmodel
from reflex_gpt.models import ChatSession,ChatSessionMessageModel
from typing import List, Optional
from . import ai

class ChatMessage(rx.Base):
    message: str
    is_bot: bool = False

class ChatState(rx.State):
    chat_session: ChatSession = None
    not_found: Optional [bool] = None
    did_submit: bool = False
    messages: List[ChatMessage] = []

    @rx.var
    def user_did_submit(self) -> bool:
        return self.did_submit
    
    #@rx.var
    def get_session_id(self) -> int:
        try:
            my_session_id = int (self.router.page.params.get
            ('session_id'))
        except:
            my_session_id = None
        return my_session_id
       # return self.router.page.params.get('session_id', '-1')
    
    def create_new_chat_session(self):
        with rx.session() as db_session:
            obj = ChatSession()
            db_session.add(obj)#adding to session, prepare to save
            db_session.commit()# saving it, acually write to database
            db_session.refresh(obj)#refresh the object with new data from database
            print(obj, obj.id)
            self.chat_session = obj
            return obj
        #return rx.redirect('/chat/{self.chat_session.id}')
    #clearing UI - at any moment in time you go next tab
    def clear_ui(self):
        self.chat_session = None
        self.not_found = None
        self.did_submit = False
        self.messages = []

    def create_new_and_redirect(self):
        self.clear_ui()
        new_chat_session = self.create_new_chat_session()
        return rx.redirect(f"/chat/{new_chat_session.id}")


    def clear_and_start_new_chat(self):
        #self.chat_session = None
        self.clear_ui()
        self.create_new_chat_session()
        self.messages = []
        yield
    
    def get_session_from_db(self,session_id=None):
        if session_id is None:
            session_id = self.get_session_id
        #ChatSession.id == session_id
        with rx.session() as db_session:
            sql_statement = sqlmodel.select(
                ChatSession                
            ).where (
                ChatSession.id == session_id
            )
            
            #sql_statement2 = sqlmodel.select(
                #ChatSessionMessageModel               
            #).where (
                #ChatSessionMessageModel.session_id == session_id
            #)
            result = db_session.exec(sql_statement).one_or_none()
            #result2 = db_session.exec(sql_statement2).all()
            if result is None:
                self.not_found = True
            else:
                self.not_found = False
            self.chat_session = result
            messages = result.messages
            #print(messages)
            for msg_obj in messages:
                msg_txt = msg_obj.content
                is_bot = False if msg_obj.role == "user" else True
                self.append_message_to_ui(msg_txt, is_bot=True)
            #if not isinstance(result, ChatSession):
                #return

    

    def on_detail_load(self):
        #print(self.router.page.params)
        #print(self.get_session_id(), type(self.get_session_id()))
        session_id = self.get_session_id()
        reload_detail = False
        if not self.chat_session:
            reload_detail = True
        else:
            """"has a session"""
            if self.chat_session.id != session_id:
                reload_detail = True
         
            
        if reload_detail:
            self.clear_ui()
            if isinstance(session_id, int):
                self.get_session_from_db(session_id=session_id)
                #self.invalid_lookup = True


    def on_load(self):
        print("running on load")
        self.clear_ui() #once done chat session will be none to start a new chat
        #if self.chat_session is None:
        self.create_new_chat_session()
            
            

        #with rx.session() as session:
            #results = session.exec(
            #   Chatmodel.select()
            #).all()
            #print(results) 
    def insert_message_to_db(self,content, role='unknown'):
        print("Insert Message Data to DB")
        if self.chat_session is None:
            return
        if not isinstance(self.chat_session,ChatSession):
            return
        with rx.session() as db_session:
            data = {
                #"chat_session_id": self.chat_session.id,
                "session_id": self.chat_session.id,
                "content": content,
                "role": role
            }
            obj = ChatSessionMessageModel(**data)
            db_session.add(obj)#adding to session, prepare to save
            db_session.commit()# saving it, acually write to database
            

    def append_message_to_ui(self, message, is_bot:bool=False):
       
        #if self.chat_session is not None:
            #print(self.chat_session.id)
        #adding to Database
        #if not is_bot:
            #with rx.session() as session:
                #obj = Chatmodel(
                    #title=message,
                #)
                #session.add(obj)
                #session.commit()
        #adding to user interface
        self.messages.append(
            ChatMessage(
                message=message, 
                is_bot=is_bot
            )
        )
    def get_gpt_messages(self):
        gpt_messages = [
            {
              "role": "system",
              "content": "You are an expert at creating recipes like an elite chef.Respond in markdown."
            }
        ]
        for chat_message in self.messages:
            role = "user" #default role
            if chat_message.is_bot:
                role = "system"
            gpt_messages.append({
                "role": role,
                "content": chat_message.message})
        return gpt_messages


    async def handle_submit(self, form_data:dict):
        print('here is our form data', form_data)
        user_message = form_data.get('message')
        if user_message:
            self.did_submit = True
            self.append_message_to_ui(user_message,is_bot=False)
            #self.message.append(
            #ChatMessage(
            #message=user_message, 
            #is_bot=False))
            #using yied to create a delay
            self.insert_message_to_db(user_message,role='user')
            yield
            gpt_messages = self.get_gpt_messages()
            #print('gpt messages', gpt_messages)
            bot_response = ai.get_llm_response(gpt_messages)
            #time.sleep(2)#2 seconds delay
            #await asyncio.sleep(2)
            self.did_submit = False
            self.append_message_to_ui(bot_response,is_bot=True)
            self.insert_message_to_db(user_message,
            role='system')
            yield
