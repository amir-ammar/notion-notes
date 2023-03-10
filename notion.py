#!/usr/bin/env python3

import pdfannots.cli
import requests
import json
import os

class NotionClient: 

    def __init__(self, token, database_id):
        self.token = token
        self.database_id = database_id
        self.headers = {
            "authorization": "Bearer " + token,
            "Notion-Version": "2022-06-28",
            "content-type": "application/json"
        }

    
    def get_pages(self):
        response = requests.post(
            "https://api.notion.com/v1/databases/{}/query".format(self.database_id), 
            headers=self.headers,
        )

        response = response.json()['results']
        
        pages = map(
            lambda page: {
                "id": page['id'],
                "title": page['properties']['Title']['title'][0]['plain_text'],
            }
            , response)
        
        return list(pages)
        

    def page_already_exists(self, title):
        
        pages = self.get_pages()
        return title in map(lambda page: page['title'], pages)

        

    def get_page(self, page_id):
        response = requests.get(
            "https://api.notion.com/v1/pages/" + page_id, 
            headers=self.headers,
        )
        return response.json()

    def create_page(self, title):
        
        page_data = {
            "parent": {
                "database_id": self.database_id
            },
            "properties": {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        }

        response = requests.post(
            "https://api.notion.com/v1/pages", 
            headers=self.headers,
            data=json.dumps(page_data)
        )

        return response.json()
    

    def get_page_blocks(self, page_id):
        response = requests.get(
            "https://api.notion.com/v1/blocks/{}/children".format(page_id), 
            headers=self.headers,
        )
        return response.json()['results']
    
    
    def add_page_block(self, type, page_id, block_data):

        block_data = {
            "children": [
                {
                    "object": "block",
                    "type": type,
                    type: {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": block_data
                                }
                            }
                        ]
                    }
                }
            ]
        }

        if type == "divider":
            block_data = {
                "children": [
                    {
                        "object": "block",
                        "type": type,
                        type: {}
                    }
                ]
            }
        
        response = requests.patch(
            "https://api.notion.com/v1/blocks/{}/children".format(page_id), 
            headers=self.headers,
            data=json.dumps(block_data)
        )
        return response.json()
    
    
    def process_notes(self, title, notes):

        if not self.page_already_exists(title=title): 
            self.create_page(title=title)

        page_id = list(filter(lambda page: page['title'] == title, self.get_pages()))[0]['id']
        
        for note in notes:

            if "text" in note:
                self.add_page_block("callout", page_id, note['text'])

            if "contents" in note:
                self.add_page_block("paragraph", page_id, note['contents'])
            
            self.add_page_block("divider", page_id, {})


if __name__ == '__main__':

    notes = pdfannots.cli.main()
    
    meta_data = notes[len(notes) - 1].split(",")
    
    notion_token = meta_data[0].split(":")[1]
    database_id = meta_data[1].split(":")[1]
    title = meta_data[2].split(":")[1]
    
    notion_client = NotionClient(token=notion_token, database_id=database_id)
    notes = notes[:len(notes) - 1]
    notion_client.process_notes(title, notes)

