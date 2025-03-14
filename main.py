import time  # Used for pausing the game with time.sleep()
import os  # Used for clearing the console with os.system('cls' or 'clear')
import random  # Used for shuffling lists (e.g., support_options in display_location)
import json  # Used for loading and saving JSON data (e.g., load_dialogue, save_game, load_game)
import platform  # Used for detecting the operating system (e.g., in install_library, clear_console)
import requests  # Used for making HTTP requests (e.g., in load_cn_tower_art, load_dialogue, get_user_country)
import subprocess  # Used for running shell commands (e.g., in install_library to run pip or pip3)
from art import text2art  # Used for generating ASCII art (in main to display "CN Tower")
from prompt_toolkit import PromptSession  # Used for creating a session with command history support

# GitHub Repository Details
# Replace 'cherrywheel' with your actual GitHub username if it's different
GITHUB_USERNAME = "cherrywheel"
GITHUB_REPO = "CN-Tower"
DIALOGUE_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/dialogue.json"  # URL to fetch dialogue data from GitHub
CN_TOWER_ART_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/cn_tower_art.txt"  # URL to fetch CN Tower ASCII art from GitHub

# List of countries where certain game features are restricted
RESTRICTED_COUNTRIES = [
    "Afghanistan", "Brunei", "Gambia", "Iran", "Iraq", "Jamaica", "Kenya",
    "Libya", "Malaysia", "Nigeria", "Pakistan", "Qatar", "Saudi Arabia",
    "Sudan", "Somalia", "Tanzania", "Uganda", "Yemen", "Zambia",
    "Zimbabwe", "Russia", "Hungary", "Georgia", "Bulgaria"
]

def clear_console():
    """Clears the console screen.

    Uses 'cls' command on Windows and 'clear' on other systems (like Linux or macOS).
    """
    if platform.system() == "Windows":
        os.system('cls')  # Clear console on Windows
    else:
        os.system('clear')  # Clear console on Linux/macOS

def install_library(library_name):
    """Installs a library using pip or pip3.

    Args:
        library_name (str): The name of the library to install.
    """
    print(f"Installing {library_name}...")
    if platform.system() == "Windows":
        subprocess.check_call(["pip", "install", library_name])  # Use pip on Windows
    else:  # Assume Linux or macOS
        subprocess.check_call(["pip3", "install", library_name])  # Use pip3 on Linux/macOS

def check_libraries():
    """Checks for required libraries and installs them if missing."""
    required_libraries = ["requests", "art"]  # List of required libraries
    for library in required_libraries:
        try:
            __import__(library)  # Try to import the library
        except ImportError:
            print(f"Missing library: {library}")
            install_library(library)  # Install the missing library

def load_cn_tower_art():
    """Loads CN Tower art from a remote URL.

    Returns:
        str: The CN Tower art as a string, or None if an error occurred.
    """
    try:
        response = requests.get(CN_TOWER_ART_URL)  # Send GET request to the art URL
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text  # Return the art as a string
    except requests.exceptions.RequestException as e:
        print(f"Error loading CN Tower art: {e}")
        return None

def display_cn_tower_art(art):
    """Displays the CN Tower art.

    Args:
        art (str): The CN Tower art to display.
    """
    if art:
        print(art)  # Print the art if it was loaded successfully
    else:
        print("Could not load CN Tower art.")

# Create a global session to preserve command history
session = PromptSession()

def get_player_input():
    """Gets input from the user with command history support."""
    try:
        return session.prompt("> ").lower()
    except EOFError:
        return "exit"

def has_item(inventory, item):
    """Checks if an item exists in the inventory.

    Args:
        inventory (dict): The player's inventory.
        item (str): The item to check for.

    Returns:
        bool: True if the item exists, False otherwise.
    """
    return item in inventory  # Returns True if item is a key in the inventory dictionary

def add_item(inventory, item, value=True):
    """Adds an item to the inventory.

    Args:
        inventory (dict): The player's inventory.
        item (str): The item to add.
        value (optional): The value associated with the item. Defaults to True.
    """
    inventory[item] = value  # Add the item to the inventory dictionary

def remove_item(inventory, item):
    """Removes an item from the inventory.

    Args:
        inventory (dict): The player's inventory.
        item (str): The item to remove.
    """
    if item in inventory:
        del inventory[item]  # Remove the item from the inventory dictionary

def display_inventory(inventory):
    """Displays the player's inventory.

    Args:
        inventory (dict): The player's inventory.
    """
    print("Inventory:", inventory)  # Print the inventory dictionary

def save_game(location, inventory, filename="savegame.json"):
    """Saves the game state to a JSON file.

    Args:
        location (str): The current location of the player.
        inventory (dict): The player's inventory.
        filename (str, optional): The name of the save file. Defaults to "savegame.json".
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:  # Specify encoding as UTF-8
            json.dump({"location": location, "inventory": inventory}, f)  # Save location and inventory to JSON file
        print("Game saved.")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game(filename="savegame.json"):
    """Loads the game state from a JSON file.

    Args:
        filename (str, optional): The name of the save file. Defaults to "savegame.json".

    Returns:
        tuple: The loaded location and inventory, or ("base", {"money": 40}) if no save file is found or an error occurs.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:  # Specify encoding as UTF-8
            data = json.load(f)  # Load location and inventory from JSON file
        print("Game loaded.")
        return data["location"], data["inventory"]  # Return the loaded location and inventory
    except (FileNotFoundError, json.JSONDecodeError):
        print("No saved game found. Starting new game.")
        return "base", {"money": 40}  # Return default values for a new game
    except Exception as e:
        print(f"Error loading game: {e}. Starting new game.")
        return "base", {"money": 40}  # Return default values for a new game

def load_dialogue():
    """Loads dialogue data from a remote JSON file.

    Returns:
        dict: The dialogue data, or an empty dictionary if an error occurred.
    """
    try:
        response = requests.get(DIALOGUE_URL)  # Send GET request to the dialogue URL
        response.raise_for_status()
        return response.json()  # Return the dialogue data as a dictionary
    except requests.exceptions.RequestException as e:
        print(f"Error loading dialogue: {e}")
        return {}  # Return an empty dictionary if loading fails

rate_limited_apis = {}

def get_user_country():
    """Detects the user's country using multiple external APIs without API keys.
    
    If an API returns 429 (Too Many Requests), it is blocked for 5 minutes.
    After 5 minutes, that API is retried.
    
    Returns:
        str: The detected country name, or None if not determined.
    """
    apis = [
        "https://ipapi.co/json/",
        "https://ipwho.is/",
        "https://freegeoip.app/json/"
    ]
    now = time.time()
    for api_url in apis:
        # Skip API if it's still rate-limited
        if api_url in rate_limited_apis and now < rate_limited_apis[api_url]:
            continue

        try:
            response = requests.get(api_url, timeout=5)  # 5-second timeout

            if response.status_code == 429:
                # Block the API for 5 minutes without printing a notification
                rate_limited_apis[api_url] = now + 5 * 60
                continue

            response.raise_for_status()
            data = response.json()

            if "country_name" in data:
                return data.get("country_name", "")
            elif "country" in data:
                return data.get("country", "")
            else:
                print(f"Unexpected response format from {api_url}")

        except requests.exceptions.RequestException as e:
            print(f"Error with {api_url} (RequestException): {e}")

    print("Could not determine country from APIs. Trying timezone...")
    try:
        import pytz
        from datetime import datetime

        local_timezone = datetime.now().astimezone().tzinfo
        country_code = pytz.country_timezones.get(str(local_timezone))
        if country_code:
            return pytz.country_names.get(country_code[0].upper())
    except ImportError:
        print("Missing library: pytz. Please install it (pip install pytz)")
    except Exception as e:
        print(f"Error getting country from timezone: {e}")

    print("Could not determine user's country.")
    return None

def is_country_banned(user_country, banned_countries):
    """Checks if the user's country is in the banned list.

    Args:
        user_country (str): The user's country name.
        banned_countries (list): The list of banned countries.

    Returns:
        bool: True if the user's country is banned, False otherwise.
    """
    return user_country in banned_countries

def sweet_dialogue(text, location, sweet_mode, dialogue_data):
    """Modifies dialogue based on sweet+ mode and location using loaded dialogue data.

    Args:
        text (str): The original text.
        location (str): The current location in the game.
        sweet_mode (bool): Whether sweet+ mode is enabled.
        dialogue_data (dict): The loaded dialogue data.

    Returns:
        str: The modified text if sweet+ mode is enabled and a modification exists, otherwise the original text.
    """
    if not sweet_mode:
        return text  # Return the original text if sweet+ mode is off

    if location in dialogue_data:
        for key, value in dialogue_data[location].items():
            text = text.replace(key, value)  # Replace placeholders with sweet+ dialogue
    return text

def display_debug_menu(inventory, sweet_mode, is_restricted):
    """Displays the debug menu and handles debug commands.

    Args:
        inventory (dict): The player's inventory.
        sweet_mode (bool): Whether sweet+ mode is enabled.
        is_restricted (bool): Whether the user is in a restricted country.
    """
    valid_items = ["ticket", "mask", "edgewalk_ticket", "postcards", "souvenir", "bible", "alex_phone"]

    while True:
        print("\n--- Debug Menu ---")
        print("1. Add Money")
        print("2. Add Item")
        print("3. Remove Item")
        print("4. Set Location")
        print("5. View Inventory")
        print("6. Exit Debug Menu")
        if not is_restricted:
            print("7. Toggle Sweet+ Mode")

        choice = input("Enter choice: ")

        if choice == "1":
            amount = int(input("Enter amount of money to add: "))
            inventory["money"] += amount
            print(f"Added ${amount}. Current money: ${inventory['money']}")
        elif choice == "2":
            print("Available items:", ", ".join(valid_items))
            item = input("Enter item name to add: ")
            if item in valid_items:
                add_item(inventory, item)
                print(f"{item} added to inventory.")
            else:
                print("Invalid item name.")
        elif choice == "3":
            item = input("Enter item name to remove: ")
            remove_item(inventory, item)
            print(f"{item} removed from inventory.")
        elif choice == "4":
            location = input("Enter the location to set: ")
            return location, inventory, sweet_mode
        elif choice == "5":
            display_inventory(inventory)
        elif choice == "6":
            print("Exiting debug menu...")
            return None, inventory, sweet_mode
        elif choice == "7" and not is_restricted:
            sweet_mode = not sweet_mode
            print(f"sweet+ Mode {'enabled' if sweet_mode else 'disabled'}")
        else:
            print("Invalid choice.")

def display_location(location, inventory, sweet_mode, dialogue_data):
    """Displays a description of the current location, inventory, and available actions.

    Handles the display of dialogue, taking into account sweet mode and location-specific dialogue.

    Args:
        location (str): The current location in the game.
        inventory (dict): The player's inventory.
        sweet_mode (bool): Whether sweet+ mode is enabled.
        dialogue_data (dict): The loaded dialogue data.
    """
    print("\n---")
    if location == "base":
        # Display initial description of the base location
        text = "You're at the base of the CN Tower. It's huge!"
        text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
        print(text)
        text = "Entrance is North. Gift shop is East."
        text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
        print(text)
        if not inventory.get("met_alex", False):
            text = "You see a person who looks like they want to talk (West)."
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
        if "worker_task" not in inventory and not inventory.get("met_Patrick", False):
            text = "A worker is struggling with some boxes (South)."
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
        if inventory.get("met_Patrick", True):
            text = "You see a strange guy, he looks like a club member (West)"
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Go North', 'Go East', 'Go West', 'Go South', 'Look Around', 'Inventory', 'Help', 'Exit', 'Restart', 'Debug', 'Save', 'Load'."
        text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
        print(text)
    elif location == "alex_rivers":
        if not inventory.get("met_alex", False):
            # Initial interaction with Alex Rivers
            text = "You go to the person. They say their name is Alex Rivers."
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            text = '"Hey! Nice day to visit the CN Tower, right?"'
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            time.sleep(3)
            text = 'Alex checks their watch. "It\'s 17:46. I have 5 minutes to record a video for my social media channel."'
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            time.sleep(5)
            text = "Alex talks a lot about the weather, the view, and their love for the CN Tower."
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            for i in range(5):
                text = f"...blah, blah, blah! ({5 - i} minutes)"
                text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
                print(text)
                time.sleep(3)
            text = "...Alex looks at their watch."
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            text = '"Oh no! I lost track of time. Gotta run!"'
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            time.sleep(2)
            text = "You wasted a lot of time."
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            text = "You continue your tour."
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            inventory["met_alex"] = True
            if not has_item(inventory, "ticket"):
                text = "Also, you don't have much time, so you didn't buy a ticket."
                text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
                print(text)
                return "base"
            else:
                return "security"
        else:
            # Subsequent interaction with Alex Rivers
            text = "It's Alex Rivers again. Still talking about the CN Tower."
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            text = 'Alex: "Oh, it\'s you! Enjoying the tower? It\'s great, right?"'
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            text = "What do you want to do?"
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
            # Options for interacting with Alex
            support_options = [
                "This tower is truly a marvel of engineering!",
                "The view from up here is absolutely breathtaking!",
                "You're doing a great job promoting this place, Alex!",
                "I've never seen anything like this before!",
                "This is the best day of my life!"
            ]
            if sweet_mode:
                # Apply sweet_dialogue to each support option
                support_options = [sweet_dialogue(option, "alex_rivers", sweet_mode, dialogue_data) for option in support_options]

            random.shuffle(support_options)
            best_support = "You're doing a great job promoting this place, Alex!"
            if sweet_mode:
                best_support = sweet_dialogue(best_support, "alex_rivers", sweet_mode, dialogue_data)
            if best_support not in support_options:
                support_options[-1] = best_support

            print("Choose two ways to support Alex:")
            for i, option in enumerate(support_options):
                print(f"{i + 1}. {option}")

            choices = []
            while len(choices) < 2:
                try:
                    choice = int(input(f"Enter choice {len(choices) + 1}: ")) - 1
                    if 0 <= choice < len(support_options):
                        choices.append(support_options[choice])
                    else:
                        print("Invalid choice. Pick a number from the list.")
                except ValueError:
                    print("Invalid input. Enter a number, please.")

            print("You say:")
            for choice in choices:
                print(f"- {choice}")
                time.sleep(2)

            # Check if the best support option was chosen
            if best_support in choices:
                text = 'Alex: "Wow, you think so? That\'s awesome! Here, take $40. Also i\'ll give you a ticket and a mask"'
                text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
                print(text)
                inventory["money"] += 40
                add_item(inventory, "mask")
                add_item(inventory, "ticket")
            else:
                text = 'Alex: "Thanks! Every little bit helps."'
                text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
                print(text)
            text = "Hints: 'Compliment Alex', 'Ignore', 'Exit', 'Restart'."
            text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
            print(text)
    # (Continue with other locations in the same detailed manner)
    elif location == "Patrick":
        text = "You go to the strange guy. He says his name is Patrick."
        text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
        print(text)
        text = '"Hey! You look like you\'ve got energy. Join our quadrobics club?"'
        text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
        print(text)
        time.sleep(3)
        text = "Patrick shows some quadrobics moves."
        text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Join', 'Decline', 'Back', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
        print(text)
    elif location == "entrance":
        text = "You're at the entrance. There's a long line for tickets."
        text = sweet_dialogue(text, "entrance", sweet_mode, dialogue_data)
        print(text)  # Print after the sweet+ dialogue
        if has_item(inventory, "ticket"):
            text = "You have a ticket! Go to security check (North)."
            text = sweet_dialogue(text, "entrance", sweet_mode, dialogue_data)
            print(text)
        else:
            text = "You need a ticket. Buy one at the ticket booth (West)."
            text = sweet_dialogue(text, "entrance", sweet_mode, dialogue_data)
            print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "entrance", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Go North' (with ticket), 'Go West', 'Back', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "entrance", sweet_mode, dialogue_data)
        print(text)
    elif location == "ticket_booth":
        text = "You're at the ticket booth. Tickets are $40."
        text = sweet_dialogue(text, "ticket_booth", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "ticket_booth", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Buy Ticket', 'Back', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "ticket_booth", sweet_mode, dialogue_data)
        print(text)
    elif location == "security":
        text = "You're at the security check. They're checking bags and tickets."
        text = sweet_dialogue(text, "security", sweet_mode, dialogue_data)
        print(text)
        if has_item(inventory, "ticket"):
            text = "The guard checks your ticket and lets you through to the elevator (North)."
            text = sweet_dialogue(text, "security", sweet_mode, dialogue_data)
            print(text)
        else:
            text = "You need a ticket to go through."
            text = sweet_dialogue(text, "security", sweet_mode, dialogue_data)
            print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "security", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Go North' (with ticket), 'Back', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "security", sweet_mode, dialogue_data)
        print(text)
    elif location == "elevator":
        text = "You're in the elevator. The doors close."
        text = sweet_dialogue(text, "elevator", sweet_mode, dialogue_data)
        print(text)
        time.sleep(2)
        text = "Going up fast..."
        text = sweet_dialogue(text, "elevator", sweet_mode, dialogue_data)
        print(text)
        time.sleep(3)
        text = "Your ears pop."
        text = sweet_dialogue(text, "elevator", sweet_mode, dialogue_data)
        print(text)
        time.sleep(2)
        text = "Ding! LookOut level."
        text = sweet_dialogue(text, "elevator", sweet_mode, dialogue_data)
        print(text)
        return "lookout"
    elif location == "lookout":
        text = "You're on the LookOut level! Great view of Toronto."
        text = sweet_dialogue(text, "lookout", sweet_mode, dialogue_data)
        print(text)
        text = "You see the city, the lake, and Niagara Falls far away."
        text = sweet_dialogue(text, "lookout", sweet_mode, dialogue_data)
        print(text)
        text = "Stairs to Glass Floor (Down). Info booth (East)."
        text = sweet_dialogue(text, "lookout", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "lookout", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Go Down', 'Go East', 'Look Around', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "lookout", sweet_mode, dialogue_data)
        print(text)
    elif location == "glass_floor":
        text = "You're on the Glass Floor! It's scary to look down."
        text = sweet_dialogue(text, "glass_floor", sweet_mode, dialogue_data)
        print(text)
        text = "You see the ground 342 meters below."
        text = sweet_dialogue(text, "glass_floor", sweet_mode, dialogue_data)
        print(text)
        text = "Stairs up to LookOut level. EdgeWalk sign (West)."
        text = sweet_dialogue(text, "glass_floor", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "glass_floor", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Go Up', 'Go West', 'Look Down', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "glass_floor", sweet_mode, dialogue_data)
        print(text)
    elif location == "edgewalk_registration":
        text = "You're at the EdgeWalk desk."
        text = sweet_dialogue(text, "edgewalk_registration", sweet_mode, dialogue_data)
        print(text)
        if has_item(inventory, "edgewalk_ticket"):
            text = "You have a ticket! The guide is preparing the gear (North)."
            text = sweet_dialogue(text, "edgewalk_registration", sweet_mode, dialogue_data)
            print(text)
        else:
            text = "You need a ticket for EdgeWalk. It's $195. Buy one here."
            text = sweet_dialogue(text, "edgewalk_registration", sweet_mode, dialogue_data)
            print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "edgewalk_registration", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Buy Ticket', 'Go North' (with ticket), 'Back', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "edgewalk_registration", sweet_mode, dialogue_data)
        print(text)
    elif location == "edgewalk_preparation":
        text = "You're in the EdgeWalk prep area. The guide helps you put on a harness."
        text = sweet_dialogue(text, "edgewalk_preparation", sweet_mode, dialogue_data)
        print(text)
        text = "You're excited and nervous."
        text = sweet_dialogue(text, "edgewalk_preparation", sweet_mode, dialogue_data)
        print(text)
        time.sleep(5)
        text = "The guide checks your harness. Thumbs up!"
        text = sweet_dialogue(text, "edgewalk_preparation", sweet_mode, dialogue_data)
        print(text)
        return "edgewalk"
    elif location == "edgewalk":
        text = "You're outside on the EdgeWalk! Wind is blowing. You're walking around the CN Tower!"
        text = sweet_dialogue(text, "edgewalk", sweet_mode, dialogue_data)
        print(text)
        text = "It's the most exciting thing ever!"
        text = sweet_dialogue(text, "edgewalk", sweet_mode, dialogue_data)
        print(text)
        text = "Congrats! You did the EdgeWalk! (Win)"
        text = sweet_dialogue(text, "edgewalk", sweet_mode, dialogue_data)
        print(text)
        return "exit"
    elif location == "gift_shop":
        text = "You're in the gift shop. They have souvenirs, postcards, and CN Tower stuff."
        text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
        print(text)
        if not has_item(inventory, "mask"):
            text = "You see a disguise kit for $20."
            text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
            print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Buy Postcards', 'Buy Souvenir', 'Buy Mask' (with enough money), 'Back', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
        print(text)
    elif location == "information_booth":
        text = "You're at the info booth. Brochures about the CN Tower are here."
        text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
        print(text)
        text = "A staff member is answering questions."
        text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Ask About History', 'Ask About Building', 'Back', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
        print(text)
    elif location == "worker":
        text = "You go to the worker. He looks tired."
        text = sweet_dialogue(text, "worker", sweet_mode, dialogue_data)
        print(text)
        text = '"Hey, can you help me? I need to move these boxes to the storage room."'
        text = sweet_dialogue(text, "worker", sweet_mode, dialogue_data)
        print(text)
        time.sleep(2)
        text = "You start helping."
        text = sweet_dialogue(text, "worker", sweet_mode, dialogue_data)
        print(text)
        for i in range(1, 5):
            text = f"You carry box {i} to the storage room..."
            text = sweet_dialogue(text, "worker", sweet_mode, dialogue_data)
            print(text)
            time.sleep(2)
        text = "You pick up the 5th box. It's open a bit."
        text = sweet_dialogue(text, "worker", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "worker", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Look Inside', 'Continue', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "worker", sweet_mode, dialogue_data)
        print(text)
    elif location == "open_box":
        text = "You look inside. You see money, a book, and a mask."
        text = sweet_dialogue(text, "open_box", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "open_box", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Take Nothing', 'Take Money', 'Take Book', 'Take Mask', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "open_box", sweet_mode, dialogue_data)
        print(text)
    elif location == "caught_stealing":
        text = "The worker sees you!"
        text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
        print(text)
        text = 'Worker: "Hey! What are you doing?!"'
        text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
        print(text)
        time.sleep(2)
        text = "He calls security. You're taken to the police."
        text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Tell Truth', 'Bribe', 'Lie', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
        print(text)
    elif location == "police_station":
        text = "You're at the police station. The officer is asking you questions."
        text = sweet_dialogue(text, "police_station", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "police_station", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Tell Truth', 'Bribe', 'Lie', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "police_station", sweet_mode, dialogue_data)
        print(text)
    elif location == "storage_room":
        text = "You're in the storage room with the worker."
        text = sweet_dialogue(text, "storage_room", sweet_mode, dialogue_data)
        print(text)
        text = 'Worker: "Thanks a lot! Here\'s $20."'
        text = sweet_dialogue(text, "storage_room", sweet_mode, dialogue_data)
        print(text)
        inventory["money"] += 20
        add_item(inventory, "worker_task")
        text = "You got $20."
        text = sweet_dialogue(text, "storage_room", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "storage_room", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Back', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "storage_room", sweet_mode, dialogue_data)
        print(text)
    elif location == "just_a_chill_guy":
        text = "You see Just a Chill Guy. He's laughing, looking at a corner."
        text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
        print(text)
        if has_item(inventory, "mask") and has_item(inventory, "bible"):
            text = "You have a mask and a Bible. You're ready to scare Alex Rivers!"
            text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
            print(text)
            text = "Hints: 'Go West', 'Back', 'Exit', 'Restart'."
            text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
            print(text)
        elif has_item(inventory, "bible") and not has_item(inventory, "mask"):
             text = 'Just a Chill Guy: "Now that the quadrobists ran away, you can scare Alex using the mask."'
             text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
             print(text)
             text = "What do you want to do?"
             text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
             print(text)
             text = "Hints: 'Use Mask', 'Go Forward', 'Ask About Corner', 'Back', 'Exit', 'Restart'."
             text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
             print(text)
        elif inventory.get("used_bible", False):
             text = 'Just a Chill Guy: "You scared the quadrobists good, now you can scare Alex."'
             text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
             print(text)
             text = "What do you want to do?"
             text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
             print(text)
             text = "Hints: 'Use Mask',  'Go Forward', 'Ask About Corner', 'Back', 'Exit', 'Restart'."
             text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
             print(text)
        else:
             text = "What do you want to do?"
             text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
             print(text)
             text = "Hints: 'Use Mask', 'Use Bible', 'Go Forward', 'Ask About Corner', 'Back', 'Exit', 'Restart'."
             text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
             print(text)
    elif location == "corner":
        if has_item(inventory, "mask") and inventory.get("used_mask", False):
            text = "You use your mask and peek around the corner. You see quadrobists practicing."
            text = sweet_dialogue(text, "corner", sweet_mode, dialogue_data)
            print(text)
            text = "They don't see you. You go back to Just a Chill Guy."
            text = sweet_dialogue(text, "corner", sweet_mode, dialogue_data)
            print(text)
            return "just_a_chill_guy"
        else:
            text = "You go to the corner, and quadrobists see you!"
            text = sweet_dialogue(text, "corner", sweet_mode, dialogue_data)
            print(text)
            text = "They make you join their quadrobics training."
            text = sweet_dialogue(text, "corner", sweet_mode, dialogue_data)
            print(text)
            time.sleep(3)
            text = "Now you're a quadrobist. You must scare Alex Rivers."
            text = sweet_dialogue(text, "corner", sweet_mode, dialogue_data)
            print(text)
            return "quadrobics_base"
    elif location == "quadrobics_base":
        text = "You move like a quadrobist. Alex is West."
        text = sweet_dialogue(text, "quadrobics_base", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Go West', 'Exit', 'Restart'."
        text = sweet_dialogue(text, "quadrobics_base", sweet_mode, dialogue_data)
        print(text)
    elif location == "scare_alex":
        text = "You successfully scared Alex Rivers using the mask and the Bible!"
        text = sweet_dialogue(text, "scare_alex", sweet_mode, dialogue_data)
        print(text)
        text = "Alex runs away, dropping their phone. You see your chance!"
        text = sweet_dialogue(text, "scare_alex", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Take Phone', 'Leave Phone', 'Exit', 'Restart'"
        text = sweet_dialogue(text, "scare_alex", sweet_mode, dialogue_data)
        print(text)
    elif location == "phone_found":
        text = "You take the phone and run to the edge of the roof. There are no obstacles in front of you."
        text = sweet_dialogue(text, "phone_found", sweet_mode, dialogue_data)
        print(text)
        text = "What do you want to do?"
        text = sweet_dialogue(text, "phone_found", sweet_mode, dialogue_data)
        print(text)
        text = "Hints: 'Jump', 'Go Back' to the Glass Floor, 'Exit', 'Restart'"
        text = sweet_dialogue(text, "phone_found", sweet_mode, dialogue_data)
        print(text)
    elif location == "roof":
        text = "You jumped from the roof. The last thing you see is blue sky"
        text = sweet_dialogue(text, "roof", sweet_mode, dialogue_data)
        print(text)
        return "exit"
    else:
        print("Invalid location.")
    print("---")
    return location  # Return the current location

def process_command(command, current_location, inventory, sweet_mode, dialogue_data, is_restricted):
    """Processes the player's command and updates the location and inventory.

    Args:
        command (str): The player's command.
        current_location (str): The current location in the game.
        inventory (dict): The player's inventory.
        sweet_mode (bool): Whether sweet+ mode is enabled.
        dialogue_data (dict): The loaded dialogue data.
        is_restricted (bool): Whether the user is in a restricted country.

    Returns:
        tuple: The new location, updated inventory, and sweet_mode.
    """
    new_location = current_location

    if current_location == "base":
        if command == "go north":
            new_location = "entrance"
        elif command == "go east":
            new_location = "gift_shop"
        elif command == "go west":
            if not inventory.get("met_alex", False):
                new_location = "alex_rivers"
            else:
                new_location = "Patrick"
        elif command == "go south" and "worker_task" not in inventory and not inventory.get("met_Patrick", False):
            new_location = "worker"
        elif command == "look around":
            text = "You see people taking pictures and the tower."
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
        elif command == "help":
            text = "Use 'Go' + direction (North, South, East, West) to move."
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
            text = "Use 'Look Around' to see more."
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
            text = "Interact with things using commands like 'Buy Ticket', 'Ask About History'."
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
            text = "'Inventory' shows your items and money."
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
            text = "'Exit' - quit game, 'Restart' - start new game"
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        elif command == "debug":
            new_location, inventory, sweet_mode = display_debug_menu(inventory, sweet_mode, is_restricted)
            if new_location:
                return new_location, inventory, sweet_mode
        elif command == "save":
            save_game(current_location, inventory)
        elif command == "load":
            new_location, inventory = load_game()
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "base", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "alex_rivers":
        if inventory.get("met_alex", False):
            if command == "compliment alex":
                text = 'Alex: "You\'re too kind! It\'s always nice to meet a fan."'
                text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
                print(text)
                text = "Alex doesn't give you anything"
                text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
                print(text)
                new_location = "base"
            elif command == "ignore":
                text = "You ignore Alex and continue."
                text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
                print(text)
                new_location = "base"
            elif command == "exit":
                new_location = "exit"
            elif command == "restart":
                new_location = "restart"
            else:
                text = "Invalid command. Check the hints."
                text = sweet_dialogue(text, "alex_rivers", sweet_mode, dialogue_data)
                print(text)
        else:
            new_location = "base"
    elif current_location == "Patrick":
        if command == "join":
            text = "You join Patrick's quadrobics club."
            text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
            print(text)
            text = "You spend a year practicing, forgetting about the CN Tower."
            text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
            print(text)
            text = "One day, you're mistaken for a stray cat and taken to a shelter."
            text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
            print(text)
            text = "You're adopted and live a comfy but meaningless life."
            text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
            print(text)
            text = "You become useless. (Bad Ending)"
            text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
            print(text)
            new_location = "exit"
        elif command == "decline":
            text = "You decline Patrick's offer."
            text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
            print(text)
            new_location = "base"
        elif command == "back":
            new_location = "base"
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "Patrick", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "entrance":
        if command == "go north" and "ticket" in inventory:
            new_location = "security"
        elif command == "go west":
            new_location = "ticket_booth"
        elif command == "back":
            new_location = "base"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
             text = "Invalid command or no ticket. Check the hints."
             text = sweet_dialogue(text, "entrance", sweet_mode, dialogue_data)
             print(text)
    elif current_location == "ticket_booth":
        if command == "buy ticket":
            if "money" in inventory and inventory["money"] >= 40:
                inventory["money"] -= 40
                inventory["ticket"] = True
                text = "You bought a ticket for $40."
                text = sweet_dialogue(text, "ticket_booth", sweet_mode, dialogue_data)
                print(text)
            else:
                text = "Not enough money."
                text = sweet_dialogue(text, "ticket_booth", sweet_mode, dialogue_data)
                print(text)
        elif command == "back":
            new_location = "entrance"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
           text = "Invalid command. Check the hints."
           text = sweet_dialogue(text, "ticket_booth", sweet_mode, dialogue_data)
           print(text)
    elif current_location == "security":
        if command == "go north" and "ticket" in inventory:
            new_location = "elevator"
        elif command == "back":
            new_location = "entrance"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
           text = "Invalid command or no ticket. Check the hints."
           text = sweet_dialogue(text, "security", sweet_mode, dialogue_data)
           print(text)
    elif current_location == "elevator":
         pass
    elif current_location == "lookout":
        if command == "go down":
            new_location = "glass_floor"
        elif command == "go east":
            new_location = "information_booth"
        elif command == "look around":
            text = "You take in the view, taking pictures."
            text = sweet_dialogue(text, "lookout", sweet_mode, dialogue_data)
            print(text)
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
             text = "Invalid command. Check the hints."
             text = sweet_dialogue(text, "lookout", sweet_mode, dialogue_data)
             print(text)
    elif current_location == "glass_floor":
        if command == "go up":
            new_location = "lookout"
        elif command == "go west":
            new_location = "edgewalk_registration"
        elif command == "look down":
            text = "It's a long way down! You feel dizzy."
            text = sweet_dialogue(text, "glass_floor", sweet_mode, dialogue_data)
            print(text)
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "glass_floor", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "edgewalk_registration":
        if command == "buy edgewalk ticket":
            if "money" in inventory and inventory["money"] >= 195:
                inventory["money"] -= 195
                inventory["edgewalk_ticket"] = True
                text = "You bought an EdgeWalk ticket for $195."
                text = sweet_dialogue(text, "edgewalk_registration", sweet_mode, dialogue_data)
                print(text)
            else:
                text = "Not enough money."
                text = sweet_dialogue(text, "edgewalk_registration", sweet_mode, dialogue_data)
                print(text)
        elif command == "go north" and "edgewalk_ticket" in inventory:
            new_location = "edgewalk_preparation"
        elif command == "back":
            new_location = "glass_floor"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command or no EdgeWalk ticket. Check the hints."
            text = sweet_dialogue(text, "edgewalk_registration", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "edgewalk_preparation":
        pass
    elif current_location == "edgewalk":
        pass
    elif current_location == "gift_shop":
        if command == "buy postcards":
            if "money" in inventory and inventory["money"] >= 5:
                inventory["money"] -= 5
                inventory["postcards"] = True
                text = "You bought postcards for $5."
                text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
                print(text)
            else:
                text = "Not enough money."
                text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
                print(text)
        elif command == "buy souvenir":
            if "money" in inventory and inventory["money"] >= 15:
                inventory["money"] -= 15
                inventory["souvenir"] = True
                text = "You bought a CN Tower souvenir for $15."
                text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
                print(text)
            else:
                text = "Not enough money."
                text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
                print(text)
        elif command == "buy mask":
            if "money" in inventory and inventory["money"] >= 20:
                inventory["money"] -= 20
                inventory["mask"] = True
                text = "You bought a mask for $20"
                text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
                print(text)
            else:
                text = "Not enough money."
                text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
                print(text)
        elif command == "back":
            new_location = "base"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "gift_shop", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "information_booth":
        if command == "ask about history":
            art = load_cn_tower_art()
            display_cn_tower_art(art)
            text = "CN Tower: Built in 1976, once the tallest structure (553.3 m)."
            text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
            print(text)
            text = "Built by Canadian National Railway. Now a tourist spot."
            text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
            print(text)
            text = "It can handle earthquakes and winds. Has a core with elevators and stairs."
            text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
            print(text)
        elif command == "ask about building":
            art = load_cn_tower_art()
            display_cn_tower_art(art)
            text = "It took 40 months to build with work done 24/7."
            text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
            print(text)
            text = "A big helicopter lifted the antenna. Built with a 'slipform' method."
            text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
            print(text)
            text = "Foundation is 15 m deep, with 7,000 cubic meters of concrete."
            text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
            print(text)
        elif command == "back":
            new_location = "lookout"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "information_booth", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "worker":
        if command == "help worker":
            new_location = "open_box"
        elif command == "back":
            new_location = "base"
        elif command == "look inside":
            new_location = "open_box"
        elif command == "continue":
            new_location = "storage_room"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "worker", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "storage_room":
        if command == "back":
            new_location = "base"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "storage_room", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "just_a_chill_guy":
        if command == "use mask":
            if "mask" in inventory:
                inventory["used_mask"] = True
                new_location = "corner"
            else:
                text = "You don't have a mask."
                text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
                print(text)
        elif command == "use bible":
            if "bible" in inventory:
                text = "You wave the Bible. The quadrobists run away scared."
                text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
                print(text)
                inventory["bible"] = False
                inventory["used_bible"] = True
                new_location = "just_a_chill_guy"
            else:
                text = "You don't have a Bible."
                text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
                print(text)
        elif command == "go forward":
            new_location = "corner"
        elif command == "ask about corner":
            text = 'Just a Chill Guy: "Just quadrobists. No worries... unless you\'re scared."'
            text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
            print(text)
        elif command == "scare quadrobists":
            text = "You try to scare them from behind the wall."
            text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
            print(text)
            text = "It works! They run away."
            text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
            print(text)
        elif command == "go west" and "mask" in inventory and "bible" in inventory:
            new_location = "scare_alex"
        elif command == "back":
            new_location = "glass_floor"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "just_a_chill_guy", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "corner":
        if "mask" in inventory and inventory["used_mask"] == True:
            new_location = "just_a_chill_guy"
            inventory["used_mask"] = False
        else:
            pass
    elif current_location == "quadrobics_base":
        if command == "go west":
            new_location = "alex_rivers_quadrobics"
        elif command == "inventory":
            display_inventory(inventory)
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "quadrobics_base", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "alex_rivers_quadrobics":
        text = "You go to Alex Rivers, moving like a quadrobist."
        text = sweet_dialogue(text, "alex_rivers_quadrobics", sweet_mode, dialogue_data)
        print(text)
        text = "Alex gets scared, drops their phone, and ruins their recording."
        text = sweet_dialogue(text, "alex_rivers_quadrobics", sweet_mode, dialogue_data)
        print(text)
        text = "You ruined their day. (Bad Ending)"
        text = sweet_dialogue(text, "alex_rivers_quadrobics", sweet_mode, dialogue_data)
        print(text)
        new_location = "exit"
    elif current_location == "open_box":
        if command == "take nothing":
            text = "You leave the box alone and continue helping."
            text = sweet_dialogue(text, "open_box", sweet_mode, dialogue_data)
            print(text)
            new_location = "storage_room"
        elif command == "take money":
            inventory["money"] += 40
            text = "You take the money."
            text = sweet_dialogue(text, "open_box", sweet_mode, dialogue_data)
            print(text)
            new_location = "caught_stealing"
        elif command == "take book":
            inventory["bible"] = True
            text = "You take the book. It's a Bible."
            text = sweet_dialogue(text, "open_box", sweet_mode, dialogue_data)
            print(text)
            new_location = "storage_room"
        elif command == "take mask":
            inventory["mask"] = True
            text = "You take the mask."
            text = sweet_dialogue(text, "open_box", sweet_mode, dialogue_data)
            print(text)
            new_location = "storage_room"
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "open_box", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "caught_stealing":
        if command == "tell truth":
            text = "You tell the truth."
            text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
            print(text)
            text = "The police let you go with a warning."
            text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
            print(text)
            inventory["met_alex"] = True
            inventory["met_Patrick"] = True
            text = "Next day, you go to the CN Tower again, but missed Alex Rivers and a chance for a free ticket."
            text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
            print(text)
            text = "You see a strange guy near the entrance."
            text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
            print(text)
            new_location = "base"
        elif command == "bribe":
            if "money" in inventory and inventory["money"] >= 50:
                text = "You bribe the officer."
                text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
                print(text)
                text = 'Officer: "Alright, get back to the CN Tower."'
                text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
                print(text)
                inventory["money"] -= 50
                new_location = "base"
            else:
                text = "Not enough money to bribe."
                text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
                print(text)
        elif command == "lie":
            text = "You lie, but the police don't believe you."
            text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
            print(text)
            text = "You're deported. No more CN Tower. (Bad Ending)"
            text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
            print(text)
            new_location = "exit"
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "caught_stealing", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "scare_alex":
        if command == "take phone":
            text = "You took Alex's phone. It's yours now!"
            text = sweet_dialogue(text, "scare_alex", sweet_mode, dialogue_data)
            print(text)
            inventory["alex_phone"] = True
            new_location = "phone_found"
        elif command == "leave phone":
            text = "You leave the phone. What were you thinking?"
            text = sweet_dialogue(text, "scare_alex", sweet_mode, dialogue_data)
            print(text)
            text = "(Bad Ending)"
            text = sweet_dialogue(text, "scare_alex", sweet_mode, dialogue_data)
            print(text)
            new_location = "exit"
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "scare_alex", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "phone_found":
        if command == "jump":
            text = "You jump from the roof"
            text = sweet_dialogue(text, "phone_found", sweet_mode, dialogue_data)
            print(text)
            new_location = "roof"
        elif command == "go back":
            new_location = "glass_floor"
        elif command == "exit":
            new_location = "exit"
        elif command == "restart":
            new_location = "restart"
        else:
            text = "Invalid command. Check the hints."
            text = sweet_dialogue(text, "phone_found", sweet_mode, dialogue_data)
            print(text)
    elif current_location == "roof":
        pass  # This is an ending state, nothing more happens

    if new_location is None:
        new_location = current_location

    return new_location, inventory, sweet_mode  # Return the updated location, inventory, and sweet_mode

def save_age(age, filename=None):
    """Automatically saves the player's age to a file in the same folder as main.py."""
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), "age.json")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"age": age}, f)
        print("Age saved automatically.")
    except Exception as e:
        print(f"Error saving age: {e}")

def load_age(filename=None):
    """Loads the player's age from a file in the same folder as main.py if it exists."""
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), "age.json")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("age")
    except Exception:
        return None

def main():
    """Main game loop."""
    check_libraries()  # Check for and install missing libraries
    dialogue_data = load_dialogue()  # Load dialogue data from GitHub
    sweet_mode = False  # Initialize sweet+ mode to off
    is_restricted = False  # Initialize is_restricted to False

    try:
        # Generate and display CN Tower ASCII art
        from art import text2art
        cn_tower_ascii = text2art("CN Tower")
        print(cn_tower_ascii)
    except ImportError:
        print("Missing library: art")
        install_library("art")  # Install 'art' library if missing
        from art import text2art
        cn_tower_ascii = text2art("CN Tower")
        print(cn_tower_ascii)

    user_country = get_user_country()  # Detect user's country

    if user_country:
        print(f"Detected user country: {user_country}")  # Display detected country
        if user_country in RESTRICTED_COUNTRIES:
            print("Some game features are not available in your country.")
            is_restricted = True  # Set the is_restricted flag to True
            sweet_mode = False  # Ensure sweet+ mode is disabled
        else:
            print("All in-game content is available in your country. Enjoy!")  # Display availability message
    else:
        print("Could not determine user country. Proceeding with caution.")
        user_country = "Unknown"  # Set a default value

    # Try to load the saved age automatically
    age = load_age()
    if age is None:
        # Age verification loop
        while True:
            try:
                age = int(input(f"Enter your age (in {user_country}): "))
                if age >= 16:
                    save_age(age)  # Automatically save age after valid input
                    break
                else:
                    print("Sorry, you must be 16 or older to play this game.")
                    return
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        print(f"Welcome back! Your age ({age}) was loaded automatically.")

    while True:
        current_location = "base"
        inventory = {"money": 40}  # Start with some money

        clear_console()  # Clear the console at the beginning of each loop iteration
        print("Welcome to the CN Tower Experience Simulator!")
        print('Type "Help" for commands.')

        while True:  # Location loop
            current_location = display_location(current_location, inventory, sweet_mode, dialogue_data)
            if current_location == "exit":
                print("Thanks for playing!")
                return  # Exit the game completely
            elif current_location == "restart":
                print("Restarting the game...")
                break  # Break out of the inner loop to restart

            command = get_player_input()

            # Process the command and update the location, inventory, and sweet_mode
            new_location, inventory, sweet_mode = process_command(command, current_location, inventory, sweet_mode, dialogue_data, is_restricted)
            current_location = new_location

if __name__ == "__main__":
    main()
