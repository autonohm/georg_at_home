"""Shared filesystem locations used by the voice-assistant package.

Deployments may relocate the package with ``VOICE_ASSISTANT_DIR``. The
constants below deliberately derive all secret and notification-audio paths
from that single root so callers do not need to duplicate layout knowledge.
"""

import os

# This default matches the directory layout in the target robot image.
VOICE_ASSISTANT_DIRECTORY = os.getenv(
    "VOICE_ASSISTANT_DIR", "/home/pib/ros_working_dir/src/voice_assistant"
)

# Paths used by the legacy Tryb token-encryption integration.
SALT_FILENAME = "salt.salt"
ENCRYPTED_TOKEN_FILENAME = "token.aes"
SECRETS_DIR = f"{VOICE_ASSISTANT_DIRECTORY}/secrets"

SALT_PATH = f"{SECRETS_DIR}/{SALT_FILENAME}"
TOKEN_PATH = f"{SECRETS_DIR}/{ENCRYPTED_TOKEN_FILENAME}"

# Audible cues played when the assistant starts and stops listening.
START_SIGNAL_FILE = (
    f"{VOICE_ASSISTANT_DIRECTORY}/audiofiles/assistant_start_listening.wav"
)
STOP_SIGNAL_FILE = (
    f"{VOICE_ASSISTANT_DIRECTORY}/audiofiles/assistant_stop_listening.wav"
)
