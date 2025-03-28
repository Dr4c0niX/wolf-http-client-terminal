import requests

BASE_URL = "http://localhost:8080"

def list_parties():
    try:
        response = requests.get(f"{BASE_URL}/list_parties")
        if response.status_code == 200:
            parties = response.json().get("id_parties", [])
            if not parties:
                print("Aucune partie disponible.")
                return []
            print("Liste des parties disponibles :")
            for party in parties:
                print(f"ID: {party['id_party']} | Lignes: {party['nb_rows']} | Colonnes: {party['nb_cols']} | Max Players: {party['max_players']}")
            return parties
        else:
            print("Erreur : Impossible de récupérer les parties.")
            return []
    except Exception as e:
        print(f"Erreur lors de la connexion au serveur : {e}")
        return []

def subscribe_to_party():
    parties = list_parties()
    if not parties:
        return
    try:
        party_id = int(input("Entrez l'ID de la partie à rejoindre : "))
    except ValueError:
        print("ID invalide.")
        return

    player = input("Entrez votre nom (laisser vide pour nom par défaut) : ")
    if not player:
        player = f"Player_{party_id}"

    data = {
        "player": player,
        "id_party": party_id
    }
    try:
        response = requests.post(f"{BASE_URL}/subscribe", json=data)
        if response.status_code == 200:
            result = response.json()["response"]
            print(f"Inscription réussie ! Rôle : {result['role']}, ID Joueur : {result['id_player']}")
        else:
            print("Erreur : Impossible de s'inscrire à la partie.")
    except Exception as e:
        print(f"Erreur lors de la connexion au serveur : {e}")

def main():
    while True:
        print("\nMenu :")
        print("1 - Lister les parties")
        print("2 - S'inscrire à une partie")
        print("3 - Quitter")
        choix = input("Votre choix : ")
        if choix == "1":
            list_parties()
        elif choix == "2":
            subscribe_to_party()
        elif choix == "3":
            print("Au revoir.")
            break
        else:
            print("Choix invalide, réessayez.")

if __name__ == "__main__":
    main()