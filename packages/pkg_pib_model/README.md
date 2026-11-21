# pkg_pib_model

Der bewegliche pib auf Georg – in Lichtblick sichtbar, in der Simulation steuerbar.

```
pib-backend /joint_states (Motornamen, Centigrad)      Sim: fake_pib_motors (gleiche Schnittstelle)
        │
        ▼
pib_model_node ── pib/joint_states (URDF-Gelenke, rad) ──► robot_state_publisher (ns pib) ──► /tf
        │  static tf pib_waist_link → root (Montage auf Georg)
        └─ /robot_description (Georg, pkg_urdf) → /georg_full/robot_description (Georg ohne starren
           pib_4S.stl + beweglicher pib) → Lichtblick
```

## Modell

Quelle ist das Web-Modell von [pib-3d](https://github.com/pib-rocks/pib-3d) (das, was Cerebra
anzeigt), Release `v0.11.6` mit SHA-256 – dieselbe Pinnung wie `pib-backend/robot_model_version.txt`.
Es wird **beim Image-Build geladen** und nicht ins Repo kopiert: Die Lizenz ist unklar (Repo
AGPL-3.0, `package.xml` „Proprietary“), und eine neue Modellversion braucht nur eine neue Pinnung
(`PIB_MODEL_VERSION`/`PIB_MODEL_SHA256` im `Dockerfile` und in `pkg_viz/Dockerfile.bridge`).

`model.json` ist schon ein URDF als JSON (47 Links mit je einem GLB, 48 Gelenke);
`pib_model/convert.py` wandelt es um. Das volle `pib.urdf` von pib-3d (351 Links, Einzelteile)
wäre für Lichtblick zu schwer.

## Gelenkwinkel

Wie Cerebra (`@pib/robot-view`): URDF-Winkel [°] = Motorwinkel [Centigrad/100] · `gearRatio` ·
`direction` − `zeroOffsetDeg`; gekoppelte Gelenke (Finger) folgen ihrem Leitgelenk · `factor`,
passive (Service-Klappen) bleiben 0. Quelle: `mapping.json` des Releases.

## Montage auf Georg

`mount_xyz` / `mount_rpy` (Parameter von `pib_model_node`): +90° um z (pib schaut in −y, Georg
in +x) und (0,103 | 0,065 | 0,613) m ab `pib_waist_link`. Geschätzt aus den Bounding-Boxen des
starren `pib_4S.stl` (Kopfoberkante, Schulterhöhe). **In Lichtblick nachprüfen** und ggf. hier
anpassen.

## Simulation

`fake_pib_motors` (nur Profil `sim`) verhält sich wie `motor_control` von pib-backend:
`/joint_states` (Centigrad, 10 Hz), `/joint_trajectory` (Rückmeldung), Service
`/apply_joint_trajectory` – Letzterer erst, wenn das `datatypes` von pib-backend im Basis-Image
ist (Plan Phase 5). Bis dahin: Topic `fake_motors/command` (`trajectory_msgs/JointTrajectory`,
Motornamen, rad).

## Lichtblick

Layout `pkg_viz/lichtblick_layouts/georg_sim.json` zeigt `/georg_full/robot_description` und
blendet `/robot_description` (starrer pib) und `/pib/robot_description` aus. Die Meshes liefert
`foxglove_bridge` (`pkg_viz`), die dafür `georg_description` und `pib_model` enthält.

## Tests

`cd pib_model_pkg && python3 -m pytest test` (ohne ROS); mit `PIB_MODEL_DIR=<konvertiertes Modell>`
zusätzlich gegen das echte `mapping.json`.
