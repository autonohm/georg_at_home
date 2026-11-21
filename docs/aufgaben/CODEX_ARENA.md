# Aufgabe für Codex: Simulationswelt „Arena“ für Georg

Ziel: eine realistische Wohnung als Simulationswelt, nach Vorbild der RoboCup@Home-Arena.
Unabhängig vom Rest bauen, **eigener Branch** (`sim_arena_world`, abgezweigt von
`pkg_task_manager_burr`), dann übergeben. Nur Dateien unten anlegen/ändern.

## Vorbild
- RoboCup@Home-Arena, 9 × 9 m, vier Räume: Wohnzimmer, Büro, Küche, Schlafzimmer; ein Eingang.
- Referenz (nicht in Git): `packages/pkg_sim/assets/arena/Competition_Arena_AtHome.usdc`
  (USD, Meter, z oben) und `.blend`. Möbelliste und Lage stehen in der USD-Szene.
- Bisheriger einfacher Stand zum Vergleich: `packages/pkg_sim/tools/build_world.py` →
  `packages/pkg_slam/maps/Wohnung.yaml` (Format-Vorlage).

## Anforderungen
1. **Echte Räume:** geschlossene Wände, **2,4 m hoch**, Türöffnungen ≥ 0,9 m, Böden/Wände mit
   Farbe oder Textur, Möbel in sinnvoller Größe und Farbe (Sofa, Couchtisch, TV, Esstisch mit
   Stühlen, Küchenzeile, Kühlschrank, Bett, Schrank, Schreibtisch, Regale, Pflanzen, Türen),
   2–4 Personen (stehend/sitzend).
2. **Georgs Basis passt überall durch:** Radius 0,35 m; Planer bläht Hindernisse um 0,25 m auf.
3. **Leicht genug für den Jetson:** gesamt ≤ 300 000 Dreiecke, Meshes als OBJ/STL.
4. **Lizenz:** keine Geometrie aus der USD/Blend kopieren (Lizenz ungeklärt). Eigene einfache
   Meshes oder Primitive bauen; freie Assets nur mit Lizenz CC0 und Quellenangabe.

## Liefern (genau diese Schnittstellen)
| Datei | Inhalt |
| --- | --- |
| `packages/pkg_slam/maps/Arena.yaml` | Karte im Format von `Wohnung.yaml`: `map` (resolution 0.05, origin, Größe), `polygons` (Typ `obstacle`, Grundrisse aller Wände/Möbel/Personen unter 1 m Höhe, Typ `boundary` für den Rand), `objects`: Zielorte (Typ `place`, **freie Standplätze** vor Möbeln/Personen, ≥ 0,4 m von jedem Hindernis) und genau ein `Start` (Typ `sim_start`) |
| `packages/pkg_slam/maps/Arena_visuals.xml` | MJCF-Ausschnitt `<mujocoinclude><asset>…</asset><worldbody>…</worldbody></mujocoinclude>` für das Kamerabild; alle Geoms `contype="0" conaffinity="0"`; Mesh-Pfade relativ zur Datei, Meshes unter `packages/pkg_slam/maps/arena_meshes/` |
| `packages/pkg_sim/tools/build_arena.py` | Skript, das beides reproduzierbar erzeugt |
| `packages/pkg_sim/test/test_arena.py` | Tests: alle Zielorte frei (0,4 m) und vom Start erreichbar (Raster 5 cm, Aufblähung 0,25 m); Dreiecksgrenze; MJCF lädt in MuJoCo 3.16 |

Zielorte mindestens: `Eingang`, `Sofa`, `Couchtisch`, `Fernseher`, `Esstisch`, `Kuehlschrank`,
`Spuele`, `Bett`, `Kleiderschrank`, `Schreibtisch`, `Regal`, `Mitte`, und je Person
`Person_<Raum>`.

## Prüfen (so nehmen wir ab)
```bash
GEORG_MAP=Arena.yaml ./projectctl.bash up sim
tests/stack/run.sh sim                        # muss weiter grün sein (nutzt Nav_Test)
# Rundgang durch alle Räume: Mission arena_tour (missions/Sim_Test.py) auf die neuen Ortsnamen
```
Kamera: Lichtblick, Image-Panel `/oak/rgb/image_raw/compressed` – Wände, Möbel, Personen sichtbar.

## Nicht anfassen
Task Manager, Navigation, Brücken, Compose-Dateien außer nötigen Pfaden. `main` nie ändern.
