#wolf-http-client-terminal/httpclientterminal.py
import requests
import json
from tabulate import tabulate
import time
import os
from soloclient import start_solo_game_local

BASE_URL = "http://localhost:8080"

def clear_screen():
    """Efface l'écran du terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Affiche l'en-tête du jeu"""
    clear_screen()
    print("\n" + "=" * 60)
    print("                 JEU DU LOUP-GAROU")
    print("=" * 60 + "\n")

def list_parties():
    """Liste toutes les parties disponibles"""
    print_header()
    print("Récupération de la liste des parties...\n")

    try:
        response = requests.get(f"{BASE_URL}/list_parties")
        if response.status_code == 200:
            parties_info = response.json()

            if not parties_info.get("id_parties"):
                print("Aucune partie disponible.")
                return []

            print("PARTIES DISPONIBLES :")
            print("-" * 80)

            # Préparer les données pour l'affichage en tableau
            # Modifier les en-têtes du tableau
            headers = ["ID", "Nom de partie", "Grille", "Joueurs", "Villageois", "Loups-garous", "Tours Max", "Durée Tour"]
            
            # Initialiser table_data comme une liste vide
            table_data = []

            # Récupérer les détails de toutes les parties en une seule requête si possible
            try:
                party_details_response = requests.get(f"{BASE_URL}/all_parties_details")
                if party_details_response.status_code == 200:
                    all_parties_details = party_details_response.json()
                else:
                    all_parties_details = {}
            except:
                all_parties_details = {}

            for party_id in parties_info.get("id_parties", []):
                # Essayer d'abord d'obtenir les détails à partir de la réponse globale
                if all_parties_details and str(party_id) in all_parties_details:
                    party_details = all_parties_details[str(party_id)]
                # Sinon, faire une requête individuelle
                else:
                    party_details = get_party_details(party_id)

                # Formater les données
                title = party_details.get("title_party", f"Partie {party_id}")
                grid_rows = party_details.get('grid_rows', 10)
                grid_cols = party_details.get('grid_cols', 10)
                grid_display = f"{grid_rows}×{grid_cols}"
                max_players = f"{party_details.get('current_players', 0)}/{party_details.get('max_players', 8)}"
                villagers = party_details.get('villagers_count', 0)
                werewolves = party_details.get('werewolves_count', 0)
                max_turns = party_details.get('max_turns', 30)
                turn_duration = party_details.get('turn_duration', 60)

                table_data.append([party_id, title, grid_display, max_players, villagers, werewolves, max_turns, f"{turn_duration}s"])

            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print("-" * 80)
            return table_data
        else:
            print(f"Erreur : Impossible de récupérer les parties. Code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erreur lors de la connexion au serveur : {e}")
        return []

def get_party_details(party_id):
    """
    Récupère les détails d'une partie auprès du serveur.
    Si l'endpoint n'existe pas, renvoie des données simulées.
    """
    try:
        response = requests.get(f"{BASE_URL}/party_details/{party_id}")
        if response.status_code == 200:
            return response.json()
    except:
        pass

    # Si l'API de détails de partie n'est pas disponible, essayer de récupérer des informations de base
    try:
        response = requests.get(f"{BASE_URL}/party/{party_id}")
        if response.status_code == 200:
            return response.json()
    except:
        pass

    # Données simulées si le serveur ne fournit pas ces détails
    # return {
    #     "id_party": party_id,
    #     "title_party": f"Partie {party_id}",
    #     "grid_rows": 10,
    #     "grid_cols": 10,
    #     "max_players": 8,
    #     "current_players": 0,
    #     "max_turns": 30,
    #     "turn_duration": 60,
    #     "villagers_count": 0,
    #     "werewolves_count": 0
    # }

def subscribe_to_party():
    """S'inscrire à une partie existante"""
    print_header()
    parties = list_parties()

    if not parties:
        input("\nAppuyez sur Entrée pour continuer...")
        return

    try:
        party_id = int(input("\nEntrez l'ID de la partie à rejoindre : "))

        # Vérifier que l'ID de partie existe dans la liste
        party_ids = [party[0] for party in parties]
        if party_id not in party_ids:
            print("ID de partie invalide.")
            input("\nAppuyez sur Entrée pour continuer...")
            return
    except ValueError:
        print("ID invalide. Veuillez entrer un nombre.")
        input("\nAppuyez sur Entrée pour continuer...")
        return

    player_name = input("Entrez votre nom de joueur : ")
    if not player_name:
        print("Le nom du joueur est obligatoire.")
        input("\nAppuyez sur Entrée pour continuer...")
        return

    # Demander la préférence de rôle
    print("\nChoisissez votre préférence de rôle :")
    print("1 - Villageois")
    print("2 - Loup-garou")
    role_choice = input("Votre choix (1 ou 2) : ")

    role = "villageois" if role_choice == "1" else "loup-garou"

    data = {
        "player": player_name,
        "id_party": party_id,
        "role_preference": role
    }

    try:
        print(f"\nConnexion au serveur pour s'inscrire à la partie {party_id}...")
        response = requests.post(f"{BASE_URL}/subscribe", json=data)

        if response.status_code == 200:
            result = response.json()["response"]
            print("\n===== INSCRIPTION RÉUSSIE =====")
            print(f"Rôle attribué : {result['role']}")
            print(f"ID Joueur : {result['id_player']}")
        else:
            print(f"\nErreur : Impossible de s'inscrire à la partie. Code: {response.status_code}")
    except Exception as e:
        print(f"\nErreur lors de la connexion au serveur : {e}")

    input("\nAppuyez sur Entrée pour continuer...")

def start_solo_game():
    """Lance une partie en mode solo (contre des IA)"""
    print_header()
    print("=== CRÉATION D'UNE PARTIE SOLO ===\n")

    player_name = input("Entrez votre nom de joueur : ")
    if not player_name:
        print("Le nom du joueur est obligatoire.")
        input("\nAppuyez sur Entrée pour continuer...")
        return

    # Demander la préférence de rôle
    print("\nChoisissez votre préférence de rôle :")
    print("1 - Villageois")
    print("2 - Loup-garou")
    role_choice = input("Votre choix (1 ou 2) : ")

    role = "villageois" if role_choice == "1" else "loup-garou"

    try:
        # Requête pour créer une nouvelle partie solo
        data = {
            "player_name": player_name,
            "role_preference": role,
            "solo_mode": True
        }

        print("\nCréation de la partie solo en cours...")
        response = requests.post(f"{BASE_URL}/create_solo_game", json=data)

        if response.status_code == 200:
            result = response.json()
            print("\n===== PARTIE SOLO CRÉÉE =====")
            print(f"ID Partie : {result.get('id_party')}")
            print(f"ID Joueur : {result.get('id_player')}")
        else:
            print(f"\nErreur : Impossible de créer une partie solo. Code: {response.status_code}")
    except Exception as e:
        print(f"\nErreur lors de la connexion au serveur : {e}")

    input("\nAppuyez sur Entrée pour continuer...")


def main():
    """Fonction principale qui affiche le menu et gère les interactions"""
    while True:
        print_header()
        print("MENU PRINCIPAL :")
        print("-" * 30)
        print("1 - Lister les parties")
        print("2 - S'inscrire à une partie")
        print("3 - Jouer en mode solo local")
        print("4 - Quitter")
        print("-" * 30)

        choix = input("Votre choix : ")

        if choix == "1":
            list_parties()
            input("\nAppuyez sur Entrée pour continuer...")
        elif choix == "2":
            subscribe_to_party()
        elif choix == "3":
            start_solo_game_local()
        elif choix == "4":
            print("\nMerci d'avoir joué au Loup-Garou. À bientôt !")
            break
        else:
            print("\nChoix invalide, veuillez réessayer.")
            time.sleep(1)
if __name__ == "__main__":
    main()
