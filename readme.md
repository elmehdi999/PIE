# 🚁 Projet CyberSTAT : SDR Drone Analysis & Jamming PoC

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![SDR](https://img.shields.io/badge/Hardware-ADALM--PLUTO-orange)
![Status](https://img.shields.io/badge/Status-PoC-success)

**PIE Projet 8 - Section technique de l'Armée de terre (STAT) & ENSTA Paris**

Ce dépôt contient le code source de la Preuve de Concept (PoC) développée par l'équipe **CyberSTAT** pour l'analyse des communications radiofréquences et le test de vulnérabilités (déni de service / brouillage) sur des drones commerciaux de série.

## 🎯 Objectifs du Projet

1. **Reconnaissance SDR :** Intercepter et analyser les protocoles de communication modernes (ex: DJI OcuSync 4.0).
2. **Analyse Spectrale :** Identifier les bandes de fréquences actives, les schémas de saut de fréquence (FHSS) et l'occupation spectrale (OFDM).
3. **Brouillage (Jamming) :** Développer et tester théoriquement des attaques de déni de service ciblées (Spot Jamming) sur des liaisons statiques (Wi-Fi 2,4 GHz).

## 🧰 Matériel et Prérequis

### Hardware
* **ADALM-PLUTO (PlutoSDR)** d'Analog Devices.
* *Note : Le PlutoSDR doit être configuré (Hack AD9364) pour étendre sa plage de réception/émission jusqu'à 6 GHz afin de cibler les bandes 5,8 GHz.*

### Software
* Python 3.8 ou supérieur.
* Pilotes libiio et libad9361-iio installés sur le système hôte.

### Bibliothèques Python
Installez les dépendances requises via `pip` :
```bash
pip install pyadi-iio numpy pandas matplotlib
