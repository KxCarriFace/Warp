from src.path_src import ALIASES_FILE
from datetime import datetime, timezone
from pathlib import Path
import json
from rich.console import Console

class PathHandler:
    def __init__(self):
        self.aliases = self._load_json()
        self.abort_keywords = ['abort', 'x', 'exit', ':q', 'quit']
        self.cancel_process = "USER_REQ_CANCEL"

    ########### REUSABLE METHODS ###########
    def _load_json(self):
        #If json nonexistent, create it, otherwise load it up
        try:
            with open(ALIASES_FILE, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}
            with open(ALIASES_FILE, 'x') as f:
                json.dump(config, f, indent=4)
        return config
    

    def _get_alias_data(self, key):
        return [data[key] for data in self.aliases.values()]
    
 
    def _validate_input(self, msg):
        while True:
            user_input = input(msg).strip()
            if user_input in self.abort_keywords:
                raise KeyboardInterrupt()
            if user_input == "":
                print("Input cannot be empty, please try again. Type 'cancel' to exit")
                continue
            if user_input.lower() == "cancel":
                print("Cancelling...\n")
                return self.cancel_process
            break
        return user_input

    ###### CREATE METHODS ######
    def add_new_alias(self, alias_name, path=None):
        self.new_alias = self._new_alias_blueprint()
        self.new_alias_name = alias_name
        if alias_name in self.aliases:
            raise ValueError(f"\n{alias_name} already exists")
        if path:
            validated_path = str(self._validate_path(path))
        else:
            validated_path = str(Path.cwd().resolve())

        curr_paths = self._get_alias_data('path')

        if validated_path in curr_paths:
            raise ValueError(f"\nPath already is attached to an alias\n")
        
        self.new_alias['path'] = validated_path

    
    def _validate_path(self, path_str):
        path = Path(path_str).expanduser().resolve()
        if not path.exists():
            raise ValueError("Path does not exist")
        
        if not path.is_dir():
            raise ValueError("Path is not a directory")
        
        return path


    def add_description(self, desc):
        
        self.new_alias['description'] = desc


    def _new_alias_blueprint(self):
        return {
            "path": "",
            "description": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_used": None,
            "usage": 0,
            "tags": []
        }
    

    def complete_add_transaction(self):
        self.aliases[self.new_alias_name] = self.new_alias

        with open(ALIASES_FILE, 'w') as f:
            json.dump(self.aliases, f, indent=4)

        print("\nSuccessfully added new alias\n")
    

    ###### READ METHODS ######

    


    ###### UPDATE METHODS ######


    ###### DELETE METHODS ######