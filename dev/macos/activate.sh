# sourced by pixi: makes the local colcon workspace visible if it was built
_georg_ws="${GEORG_WS:-$HOME/.cache/georg-ros-ws}"
if [ -f "$_georg_ws/install/setup.bash" ] && [ -n "$BASH_VERSION" ]; then
  . "$_georg_ws/install/setup.bash"
elif [ -f "$_georg_ws/install/setup.sh" ]; then
  . "$_georg_ws/install/setup.sh"
fi
unset _georg_ws
