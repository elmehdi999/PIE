import os 
# PATCH WINDOWS
path_to_lib = r"C:\Program Files\IIO Oscilloscope\bin"

if os.path.exists(path_to_lib):
    os.add_dll_directory(path_to_lib)
    os.environ['PATH'] = path_to_lib + ';' + os.environ['PATH']
else:
    print(f"ERREUR : Le dossier {path_to_lib} est introuvable.")


import adi
import numpy as np
import time
import csv
import datetime

SDR_IP = "ip:192.168.2.1"
CAPTURE_DURATION = 60      # Durée du scan en secondes
FILENAME = f"dji_scan_{int(time.time())}.csv" # Nom du fichier

# CONFIGURATION RADIO (AD9364) 
CENTER_FREQ = 2440000000   # Bande 2.4 GHz
CENTER_FREQ = 5800000000 # Bande 5.8 GHz (Nécessite le Hack)

SAMPLE_RATE = 30720000     # 30.72 MHz de vision
GAIN_DB = 30              # Gain Manuel (si possible, 25-35 conseillé)
THRESHOLD_OFFSET = 15      # Seuil de détection (Bruit + 15dB)

# Paramètres supplémentaires
MIN_SIGNAL_SEP_HZ = 200_000   # regrouper bins séparés de moins de 200 kHz
MIN_BINS_FOR_SIGNAL = 5       # ignorer groupes < 5 bins
PSD_SMOOTH_ALPHA = 0.15       # 0 = pas de lissage, 0.15 = lissage léger

def run_capture():
    # 1. Connexion au PlutoSDR
    print(f"[INIT] Connexion au PlutoSDR ({SDR_IP})...")
    try:
        sdr = adi.Pluto(uri=SDR_IP)
    except Exception as e:
        print(f"[ERREUR] Impossible de connecter le SDR. Vérifie l'IP et le câble.\n{e}")
        return

    sdr.rx_enabled_channels = [0]
    
    # 2. Application des réglages
    sdr.rx_lo = int(CENTER_FREQ)
    sdr.rx_samp_rate = int(SAMPLE_RATE)
    # rx_rf_bandwidth parfois doit être un peu plus petit ; on essaier telle quelle et fallback
    try:
        sdr.rx_rf_bandwidth = int(SAMPLE_RATE)
    except Exception:
        sdr.rx_rf_bandwidth = int(SAMPLE_RATE * 0.9)
    # forcer manuel si possible
    try:
        sdr.gain_control_mode_chan0 = 'manual'
        sdr.rx_hardwaregain_chan0 = int(GAIN_DB)
    except Exception:
        # certains wrappers ont d'autres noms d'attributs ; on ignore si échec
        pass
    sdr.rx_rf_port_select = "A_BALANCED"
    sdr.rx_buffer_size = 1024 * 16

    # 3. Préparation du fichier de sauvegarde
    print(f"[INFO] Création du fichier : {FILENAME}")
    with open(FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp_s", "Date_Heure", "Frequence_MHz", "Puissance_dB_rel", "Largeur_kHz"])

        # 4. Préparation mathématique (Axe X des fréquences)
        N = int(sdr.rx_buffer_size)
        freqs = np.linspace(CENTER_FREQ - SAMPLE_RATE/2, CENTER_FREQ + SAMPLE_RATE/2, N)
        freqs_mhz = freqs / 1e6
        bin_width_hz = SAMPLE_RATE / N
        min_sep_bins = max(1, int(MIN_SIGNAL_SEP_HZ / bin_width_hz))

        print(f"[START] Démarrage de la capture pour {CAPTURE_DURATION} secondes...")
        print(f"         CENTER {CENTER_FREQ/1e6:.3f} MHz | SAMPLE_RATE {SAMPLE_RATE/1e6:.3f} MSps | bin ≈ {bin_width_hz/1e3:.2f} kHz")
        start_time = time.time()
        detection_count = 0
        psd_smooth = None

        # --- BOUCLE PRINCIPALE (Durée limitée) ---
        while (time.time() - start_time) < CAPTURE_DURATION:
            try:
                raw = sdr.rx()  # peut lever exception si timeout/device disconnect
            except Exception as e:
                print(f"[WARN] erreur lecture SDR (retry): {e}")
                time.sleep(0.1)
                continue

            # Robustesse : s'assurer d'un vecteur 1D
            samples = np.asarray(raw).flatten()
            if samples.size == 0:
                continue

            # Fenêtre + FFT (normalisation pour comparer entre tailles)
            N_s = len(samples)
            win = np.hanning(N_s)
            fft_vals = np.fft.fftshift(np.fft.fft(samples * win, n=N_s))
            psd = 10.0 * np.log10((np.abs(fft_vals) ** 2) / (N_s ** 2) + 1e-16)

            # Lissage exponentiel pour stabiliser la détection
            if psd_smooth is None:
                psd_smooth = psd
            else:
                psd_smooth = (1 - PSD_SMOOTH_ALPHA) * psd_smooth + PSD_SMOOTH_ALPHA * psd

            # Estimation robuste du plancher de bruit (médiane)
            noise_floor = float(np.median(psd_smooth))
            threshold = noise_floor + THRESHOLD_OFFSET

            # Identification des bins au-dessus du seuil
            peak_indices = np.where(psd_smooth > threshold)[0]
            if peak_indices.size == 0:
                continue

            # Regroupement des pics adjacents en tenant compte de min_sep_bins
            groups = np.split(peak_indices, np.where(np.diff(peak_indices) > min_sep_bins)[0] + 1)

            current_t = time.time()
            readable_t = datetime.datetime.fromtimestamp(current_t).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            for g in groups:
                if g.size < MIN_BINS_FOR_SIGNAL:
                    continue  # ignorer petits blobs
                idx_peak = g[np.argmax(psd_smooth[g])]
                freq_val_mhz = freqs_mhz[idx_peak]
                max_power_db = float(np.max(psd_smooth[g]))
                bw_khz = (freqs_mhz[g[-1]] - freqs_mhz[g[0]]) * 1000.0

                # Sauvegarde & flush (pratique si interruption)
                writer.writerow([f"{current_t:.3f}", readable_t, f"{freq_val_mhz:.6f}", f"{max_power_db:.2f}", f"{bw_khz:.0f}"])
                file.flush()

                print(f"  -> Détection : {freq_val_mhz:.3f} MHz | {max_power_db:.2f} dB (rel) | bw {bw_khz:.0f} kHz")
                detection_count += 1

            # petite pause pour éviter boucle trop serrée (ajuste si besoin)
            # time.sleep(0.001)

    # 5. Fin du programme
    print("-" * 40)
    print(f"[FIN] Capture terminée.")
    print(f"      Temps écoulé : {CAPTURE_DURATION}s")
    print(f"      Signaux détectés : {detection_count}")
    print(f"      Données sauvegardées dans : {FILENAME}")

if __name__ == "__main__":
    run_capture()
