import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Remplacer par le nom de ton fichier CSV
FILE_NAME = str(input("Donne le nom du fichier: ")) 

try:
    # 1. Chargement des données
    print(f"Chargement de {FILE_NAME}...")
    df = pd.read_csv(FILE_NAME)
    
    # Normalisation du temps (t=0 au début de la capture)
    df['Temps_Relatif'] = df['Timestamp_s'] - df['Timestamp_s'].min()
    
    # Configuration de la figure (Taille A4 paysage environ)
    plt.figure(figsize=(16, 10))
    plt.suptitle(f"Analyse du Signal DJI Mini 4 Pro (Protocole O4) - {FILE_NAME}", fontsize=16)
    
    # --- GRAPHIQUE 1 : Le "Waterfall" (Temps vs Fréquence) ---
    plt.subplot(2, 2, 1)
    # Scatter plot : X=Temps, Y=Fréquence, Couleur=Puissance
    sc = plt.scatter(df['Temps_Relatif'], df['Frequence_MHz'], 
                     c=df['Puissance_dB_rel'], cmap='inferno', 
                     s=15, alpha=0.7, edgecolors='none')
    cbar = plt.colorbar(sc)
    cbar.set_label('Puissance (dB)')
    plt.title('1. Signature Temporelle (Saut de Fréquence / FHSS)')
    plt.xlabel('Temps écoulé (s)')
    plt.ylabel('Fréquence (MHz)')
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # --- GRAPHIQUE 2 : Occupation Spectrale (Histogramme) ---
    plt.subplot(2, 2, 2)
    # Compte combien de fois chaque fréquence est touchée
    plt.hist(df['Frequence_MHz'], bins=50, color='teal', alpha=0.8, edgecolor='black')
    plt.title('2. Densité d\'Occupation du Spectre')
    plt.xlabel('Fréquence (MHz)')
    plt.ylabel('Nombre de paquets (Hits)')
    plt.grid(True, linestyle='--', alpha=0.3)
    # Note : Les pics ici sont les fréquences à brouiller en priorité !
    
    # --- GRAPHIQUE 3 : Puissance vs Temps ---
    plt.subplot(2, 1, 2)
    # Points bruts en gris
    plt.plot(df['Temps_Relatif'], df['Puissance_dB_rel'], '.', color='gray', alpha=0.3, markersize=3, label='Mesures brutes')
    # Moyenne glissante (Rolling Mean) en rouge pour la tendance
    df_sorted = df.sort_values('Temps_Relatif')
    # Fenêtre de 50 échantillons pour lisser
    rolling_mean = df_sorted['Puissance_dB_rel'].rolling(window=50, center=True).mean()
    plt.plot(df_sorted['Temps_Relatif'], rolling_mean, color='red', linewidth=2, label='Puissance Moyenne (Lissée)')
    
    plt.title('3. Profil de Puissance au Démarrage')
    plt.xlabel('Temps écoulé (s)')
    plt.ylabel('Puissance Relative (dB)')
    plt.legend(loc='lower right')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Sauvegarde et Affichage
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Ajustement pour le titre principal
    output_file = 'dji_rapport_analyse.png'
    plt.savefig(output_file, dpi=200)
    print(f"Analyse terminée ! Graphique sauvegardé sous : {output_file}")
    plt.show()

except FileNotFoundError:
    print(f"Erreur : Le fichier {FILE_NAME} est introuvable. Vérifie le chemin.")
except Exception as e:
    print(f"Une erreur est survenue : {e}")
