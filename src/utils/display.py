from colorama import Fore, Style, init
import os

init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_ascii_art():
    ascii_art = """
    ╔══════════════════════════════════╗
    ║           🤖 CLI BOT 🤖         ║
    ║          Version 1.0.0           ║
    ║           by: H4INCE             ║
    ╚══════════════════════════════════╝    
    """
    print(Fore.CYAN + ascii_art + Style.RESET_ALL)

def get_user_input():
    return input(Fore.GREEN + "You: " + Style.RESET_ALL)

def display_bot_response(response):
    print(Fore.BLUE + "Bot: " + Style.RESET_ALL + response)
    print() 