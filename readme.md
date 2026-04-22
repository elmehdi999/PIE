🚁 Projet CyberSTAT : SDR Drone Analysis & Jamming PoC
PIE Projet 8 - Section technique de l'Armée de Terre (STAT) & ENSTA Paris

Ce dépôt contient le code source de la Preuve de Concept (PoC) développée par l'équipe CyberSTAT pour l'analyse des communications radiofréquences et l'étude des vulnérabilités (déni de service / brouillage) sur des drones commerciaux de série.

🎯 Objectifs du Projet
Reconnaissance SDR : Intercepter et analyser les protocoles de communication modernes (ex: DJI OcuSync 4.0).

Analyse Spectrale : Identifier les bandes de fréquences actives et l'occupation spectrale (OFDM/FHSS).

Brouillage (Jamming) : Développer et tester théoriquement des attaques de déni de service ciblées (Spot Jamming) sur des liaisons statiques (Wi-Fi 2,4 GHz).

🧰 Matériel et Prérequis
Hardware
ADALM-PLUTO (PlutoSDR) d'Analog Devices.

Note : Le PlutoSDR doit être configuré (Hack AD9364) pour étendre sa plage de fréquences jusqu'à 6 GHz afin de couvrir la bande 5,8 GHz.

Software & Bibliothèques
Python 3.8+

Pilotes libiio et libad9361-iio.

Dépendances Python : pyadi-iio, numpy, pandas, matplotlib.

🚀 Utilisation et Résultats Attendus
1. Script de Reconnaissance : scanner_5ghz.py
Utilisation : Configure l'oscillateur local du PlutoSDR pour scanner la bande des 5,8 GHz. Il réalise une acquisition des échantillons I/Q et applique une FFT pour isoler les pics d'énergie.

Résultats attendus :

Détection en temps réel des fréquences actives affichées en console.

Génération d'un fichier journal dji_scan_*.csv contenant les timestamps, fréquences (MHz), puissances (dB) et largeurs de bande (kHz).

2. Script de Visualisation : plot_dji.py
Utilisation : Analyse le fichier CSV généré précédemment pour reconstituer le comportement du drone.

Résultats attendus :

Création d'un tableau de bord graphique (dji_rapport_analyse.png) montrant :

Le Spectrogramme (Waterfall) confirmant le verrouillage des canaux.

L'Occupation spectrale identifiant les pics (ex: 5785 MHz et 5814 MHz).

Le Profil de puissance montrant le pic d'allumage suivi de la stabilisation.

3. Script d'Attaque (PoC) : wifi_jammer_poc.py
Utilisation : Génère un signal de bruit blanc gaussien (AWGN) sur un canal Wi-Fi spécifique (ex: Canal 6 à 2437 MHz).

Résultats attendus (théoriques) :

Saturation du rapport signal-sur-bruit (SNR) du récepteur cible.

Sur un drone type Furtif IRDRONE, cela entraîne la perte du flux vidéo puis le déclenchement de la procédure de sécurité (Return to Home ou atterrissage d'urgence).

📂 Structure du projet
📦 CyberSTAT
 ┣ 📂 data                   # Dossiers des logs CSV
 ┣ 📜 scanner_5ghz.py        # Script d'interception principale
 ┣ 📜 plot_dji.py            # Génération des graphiques d'analyse
 ┣ 📜 wifi_jammer_poc.py     # PoC de brouillage Wi-Fi (2.4GHz)
 ┣ 📜 requirements.txt       # Dépendances Python
 ┗ 📜 README.md              # Documentation
📊 Analyse des Écarts (DJI Mini 4 Pro)
L'analyse spectrale a révélé que le protocole DJI OcuSync 4.0 utilise une redondance sur deux canaux fixes. Le brouillage avec un PlutoSDR seul est limité par :

La division de puissance : Cibler deux canaux divise l'énergie du SDR par deux.

L'asymétrie de puissance : Le drone émet beaucoup plus fort que le SDR non amplifié.

Complexité : L'utilisation probable de l'OFDM nécessite une puissance de saturation élevée ou l'ajout d'un amplificateur de puissance externe (+20 dB).

⚠️ Avertissement Légal (Disclaimer)
L'émission de signaux de brouillage (Jamming) est strictement interdite par la loi en espace ouvert (Article L39-1 du CPCE). Ce projet a été réalisé à des fins éducatives. Les scripts d'attaque n'ont pas été testés en conditions réelles et ne doivent être exécutés que dans un environnement électromagnétiquement isolé (cage de Faraday).
