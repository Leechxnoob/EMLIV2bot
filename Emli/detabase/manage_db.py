# (c) @JigarVarma2005
from pymongo import MongoClient
import asyncio
import sys
from Emli import MONGO_DB_URI
from confing import get_int_key, get_str_key

class manage_db():
    def __init__(self):
        self.db = MongoClient(get_str_key("MONGO_DB_URI")["captcha"]
        self.chats = self.db["Chats"]
        
    def chat_in_db(self, chat_id):
        chat = self.chats.find_one({"chat_id":chat_id})
        return chat
        
    def add_chat(self, chat_id, captcha):
        if self.chat_in_db(chat_id):
            return 404
        self.chats.insert_one({"chat_id":chat_id, "captcha": captcha})
        return 200
    
    def delete_chat(self,chat_id):
        self.chats.delete_many({"chat_id": chat_id})
        return True
