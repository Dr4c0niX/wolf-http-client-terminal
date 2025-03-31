import random
import os
import time

class SoloGame:
    """Classe qui gère une partie solo du jeu Loup-Garou (sans IA)"""
    
    def __init__(self, player_name, role_preference):
        """Initialise une nouvelle partie solo"""
        self.player_name = player_name
        self.role = role_preference.lower()
        
        # Configuration du plateau
        self.LIGNES = 5  
        self.COLONNES = 5  
        self.NOMBRE_OBSTACLES = 3
        
        # Initialisation des positions
        self.occupied_positions = set()
        self.initialiser_positions()
        
        # Statistiques de jeu
        self.turns = 0
        self.max_turns = 30
        self.game_over = False
        self.result = None

    def initialiser_positions(self):
        """Initialise les positions des joueurs et des obstacles"""
        # Position du joueur
        self.joueur_x, self.joueur_y = self.position_aleatoire(self.occupied_positions)
        self.occupied_positions.add((self.joueur_x, self.joueur_y))
        
        # Position du PNJ (statique)
        self.pnj_x, self.pnj_y = self.position_aleatoire(self.occupied_positions)
        self.occupied_positions.add((self.pnj_x, self.pnj_y))
        
        # Positions des obstacles
        self.obstacles = []
        for _ in range(self.NOMBRE_OBSTACLES):
            obs_x, obs_y = self.position_aleatoire(self.occupied_positions)
            self.obstacles.append((obs_x, obs_y))
            self.occupied_positions.add((obs_x, obs_y))

    def position_aleatoire(self, exclusions):
        """Génère une position aléatoire qui n'est pas dans la liste d'exclusions"""
        while True:
            pos = (random.randint(0, self.LIGNES - 1), random.randint(0, self.COLONNES - 1))
            if pos not in exclusions:
                return pos

    def clear_screen(self):
        """Efface l'écran du terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Affiche l'en-tête du jeu"""
        self.clear_screen()
        print("\n" + "=" * 60)
        print(f"                 JEU DU LOUP-GAROU - MODE SOLO")
        print("=" * 60 + "\n")
        print(f"Joueur: {self.player_name} | Rôle: {self.role.capitalize()} | Tour: {self.turns}/{self.max_turns}")
        print("-" * 60)

    def afficher_plateau(self):
        """Affiche le plateau de jeu"""
        self.print_header()
        print("Plateau de jeu :")
        for i in range(self.LIGNES):
            for j in range(self.COLONNES):
                if (i, j) == (self.joueur_x, self.joueur_y):
                    print("🐺" if self.role == "loup-garou" else "🙂", end=" ") 
                elif (i, j) == (self.pnj_x, self.pnj_y):
                    if self.role == "loup-garou": 
                        distance_x = abs(self.joueur_x - self.pnj_x)
                        distance_y = abs(self.joueur_y - self.pnj_y)
                        if distance_x <= 1 and distance_y <= 1:
                            print("🙂", end=" ")  
                        else:
                            print("⬜", end=" ")  
                    else:
                        print("🐺", end=" ")  
                elif (i, j) in self.obstacles:
                    print("🧱", end=" ")  
                else:
                    print("⬜", end=" ")  
            print()
        print()

        # Affichage vision loup
        if self.role == "loup-garou":
            print("Vision du loup :")
            vois_villageois = False
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = self.joueur_x + dx, self.joueur_y + dy
                if 0 <= nx < self.LIGNES and 0 <= ny < self.COLONNES:
                    if (nx, ny) == (self.pnj_x, self.pnj_y):
                        vois_villageois = True
            if vois_villageois:
                print("Le villageois est à proximité !")
            else:
                print("Aucun villageois à proximité.")
                
        # Affichage vision villageois
        else:
            print("Vision du villageois :")
            vois_loup = False
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = self.joueur_x + dx, self.joueur_y + dy
                if 0 <= nx < self.LIGNES and 0 <= ny < self.COLONNES:
                    if (nx, ny) == (self.pnj_x, self.pnj_y):
                        vois_loup = True
            if vois_loup:
                print("Le loup est à proximité ! Soyez prudent !")
            else:
                print("Aucun loup à proximité.")

        # Afficher la distance au personnage opposé
        dx = abs(self.joueur_x - self.pnj_x)
        dy = abs(self.joueur_y - self.pnj_y)
        distance = dx + dy  # Distance de Manhattan
        if self.role == "loup-garou":
            print(f"\nDistance au villageois: {distance} cases")
        else:
            print(f"\nDistance au loup-garou: {distance} cases")

    def deplacer_joueur(self, mouvement):
        """Déplace le joueur selon l'entrée utilisateur"""
        nouveau_x, nouveau_y = self.joueur_x, self.joueur_y 

        if mouvement == "z" and self.joueur_x > 0:
            nouveau_x -= 1
        elif mouvement == "s" and self.joueur_x < self.LIGNES - 1:
            nouveau_x += 1
        elif mouvement == "q" and self.joueur_y > 0:
            nouveau_y -= 1
        elif mouvement == "d" and self.joueur_y < self.COLONNES - 1:
            nouveau_y += 1
        elif mouvement == "":
            print("Tour passé.")
            self.turns += 1
            return True
        else:
            print("Déplacement invalide.")
            return False

        # Vérifier si la case cible contient un obstacle
        if (nouveau_x, nouveau_y) in self.obstacles:
            print("Déplacement impossible : obstacle !")
            return False
        else:
            self.joueur_x, self.joueur_y = nouveau_x, nouveau_y
            self.turns += 1
            return True

    def verifier_fin_jeu(self):
        """Vérifie si le jeu est terminé et définit le résultat"""
        # Vérification de la victoire ou défaite
        if (self.joueur_x, self.joueur_y) == (self.pnj_x, self.pnj_y):
            if self.role == "loup-garou":
                self.result = "Victoire ! Vous avez mangé le villageois !"
            else:
                self.result = "Défaite ! Le loup-garou vous a attrapé !"
            self.game_over = True
            
        # Vérification du nombre de tours maximal
        elif self.turns >= self.max_turns:
            if self.role == "loup-garou":
                self.result = "Défaite ! Vous n'avez pas réussi à trouver et manger le villageois dans le temps imparti."
            else:
                self.result = "Victoire ! Vous avez réussi à échapper au loup-garou pendant tous les tours !"
            self.game_over = True

    def jouer_tour(self):
        """Joue un tour complet"""
        self.afficher_plateau()
        
        # Vérifier la fin de la partie
        self.verifier_fin_jeu()
        if self.game_over:
            return False
            
        # Déplacement du joueur
        valid_move = False
        while not valid_move:
            mouvement = input("Déplacez-vous (z=haut, s=bas, q=gauche, d=droite, entrée=passer) : ").strip().lower()
            valid_move = self.deplacer_joueur(mouvement)
        
        # Vérifier à nouveau après déplacements
        self.verifier_fin_jeu()
        
        return not self.game_over

    def demarrer_partie(self):
        """Démarre la partie et gère la boucle principale du jeu"""
        try:
            print(f"\nDémarrage de la partie en mode solo pour {self.player_name}...")
            print(f"Votre rôle : {self.role.capitalize()}")
            
            # Instructions différentes selon le rôle
            if self.role == "loup-garou":
                print("Votre objectif : Trouvez et mangez le villageois immobile sur le plateau.")
                print(f"Vous avez {self.max_turns} tours pour le trouver.")
            else:
                print("Votre objectif : Échappez au loup-garou immobile sur le plateau.")
                print(f"Vous devez survivre pendant {self.max_turns} tours.")
            
            time.sleep(2)
            
            # Boucle principale du jeu
            while not self.game_over:
                if not self.jouer_tour():
                    break
                
            # Affichage du résultat final
            self.afficher_plateau()
            print("\n" + "=" * 40)
            print("FIN DE LA PARTIE")
            print("=" * 40)
            print(self.result)
            print(f"Nombre de tours joués : {self.turns}")
            print("=" * 40)
            
            input("\nAppuyez sur Entrée pour retourner au menu principal...")
            
        except KeyboardInterrupt:
            print("\n\nPartie interrompue par l'utilisateur.")
            input("Appuyez sur Entrée pour continuer...")

def start_solo_game_local():
    """Lance une partie en mode solo local (sans IA)"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "=" * 60)
    print("            CRÉATION D'UNE PARTIE SOLO LOCALE")
    print("=" * 60 + "\n")
    print("Dans ce mode, votre adversaire est statique et ne se déplace pas.")
    print("Selon votre rôle, vous devez soit trouver votre adversaire, soit lui échapper.")
    print("-" * 60)

    player_name = input("Entrez votre nom de joueur : ")
    if not player_name:
        print("Le nom du joueur est obligatoire.")
        input("\nAppuyez sur Entrée pour continuer...")
        return

    # Demander la préférence de rôle
    print("\nChoisissez votre préférence de rôle :")
    print("1 - Villageois (échappez au loup-garou pendant 30 tours)")
    print("2 - Loup-garou (trouvez le villageois)")
    role_choice = input("Votre choix (1 ou 2) : ")

    role = "villageois" if role_choice == "1" else "loup-garou"

    # Créer et démarrer la partie
    game = SoloGame(player_name, role)
    game.demarrer_partie()

# Test du module si exécuté directement
if __name__ == "__main__":
    start_solo_game_local()