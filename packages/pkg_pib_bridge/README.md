# pkg_pib_bridge

Brücke zwischen Georgs Stack und [pib-backend](https://github.com/pib-rocks/pib-backend) für
Sprache (Sprechen, Zuhören), mit fester Freigabeliste. Optional: `GEORG_WITH_PIB_BACKEND=1 ./projectctl.bash up sim|real`
(braucht das Docker-Netz `pib-network` von pib-backend).

Ein Prozess, zwei ROS-Domains: Stack (`ROS_DOMAIN_ID`, 30 in sim, 0 am Roboter) und pib-backend
(`PIB_BACKEND_DOMAIN_ID`, 0). Der Container hängt als **einziger** in beiden Docker-Netzen. Es
geht nichts anderes durch – insbesondere keine Fahr- oder Motorbefehle.

| Stack-Seite | pib-backend |
| --- | --- |
| Action `speech/say` (`georg_speech_msgs/Say`) | Service `/play_audio_from_speech` (`join=true`), Stimme `M1`/`de` |
| Action `audio/listen` (`georg_speech_msgs/Listen`), SPEECH | `/speech_detected` (Bool), Text aus `/chat_messages` (`is_user`) |
| Action `audio/listen`, DOORBELL | `PIB_DOORBELL_TOPIC` (Bool), Standard keins → „nicht erkannt“ |

`PIB_SAY_JOIN=false`: nicht auf das Satzende warten – nur für Rechner ohne Lautsprecher (sonst
hängt pib-backends `audio_player`, Q37). Am Roboter `true` lassen, sonst hört Greeting Georgs
eigene Stimme.

**Keine Sensordaten** (Kamera, Erkennungen, Gelenkwinkel) gehen über die Brücke: In `sim`
sieht der Roboter nur die Simulation – wie er auch nur simulierte Motoren bewegt. Am
Roboter teilen Stack und pib-backend Domain 0; in `mcap` kommt das Bild aus der Aufnahme.

Test: `tests/stack/bridge_check.py` (Speak, Listen aus Sicht des Stacks).

## Offen
- Am Roboter läuft pib-backend auf dem Pi im LAN, nicht im Docker-Netz dieses Rechners → dort
  braucht der Container Zugang zum Roboternetz (z. B. Host-Netz oder macvlan).
- Türklingel: keine Quelle (pib-backend kennt keine; evtl. Home Assistant).
