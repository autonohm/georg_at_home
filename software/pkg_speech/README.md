# pkg_speech

This package implements an offline tts-model. So Georg can talk without needing internet connection :)

It is based on [the existing  voice assistent of pib_backend](https://github.com/pib-rocks/pib-backend/commit/a4d091e965e774a66e8db1c6566586bf553588ed), and stripped of everything that is not necessary for the voice_assistent and any feature that requires an internet connection.


### Docker

```bash
docker compose --profile voice_assistant up -d --build
```

`password.env` required to run the voice assistant:

```
TRYB_URL_PREFIX=<BASE_URL_Tryb>
```


### REDE
Run the following command in the container to test out the tts:

```
ros2 service call /play_audio_from_speech datatypes/srv/PlayAudioFromSpeech \
  "{speech: 'Hallo, ich bin Geeorg. Aber du darfst mich auch Schorsch nennen.', gender: 'M1', language: 'de', join: true}"
```

This model cannot pronounce "Georg" correctly, however "Geeorg" works great. This fix will work for now.


### Known issue
If you want to run this on your laptop, and not on the pib itsself, change the environment configurations in 'docker-compose.yaml':

```
ros-voice-assistant:
    image: ros_voice_assistant

    # ...

    environment:
      # - ALSA_CARD=ArrayUAC10 #  <-- remove this line
      - PULSE_SERVER=unix:${XDG_RUNTIME_DIR:-/run/user/1000}/pulse/native
      - # ...
    volumes:
      - ${XDG_RUNTIME_DIR:-/run/user/1000}/pulse/native:${XDG_RUNTIME_DIR:-/run/user/1000}/pulse/native
      - # ...
```

Otherwise the connection to your speakers will not work.