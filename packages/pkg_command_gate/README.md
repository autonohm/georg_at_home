# pkg_command_gate

Second safety line for motor commands, see `docs/task_manager_plan.md`, section "Befehls-Gate".

```
packages --> cmd_vel --> [command_gate] --> cmd_vel/gated --> driver (pkg_drive, profile real only)
```

The gate forwards a `geometry_msgs/Twist` from `cmd_vel` to `cmd_vel/gated` only if **both** are true:

- the device mode is `real`: `/etc/georg/mode` inside the container, otherwise `GEORG_DEVICE_MODE`, which `projectctl.bash` reads from `/etc/georg/mode` on the host
- the started profile is `real` (`GEORG_PROFILE`, set by `projectctl.bash`)

Everything else is dropped and logged. The gate fails closed: a missing or unreadable mode closes it. The mode is re-checked every second.

It runs in every profile. The first safety line is that the driver container only exists in profile `real`.

Tests without ROS:

```bash
cd command_gate && python3 -m pytest test
```

Joint commands of the gestures are not gated yet (open question in `docs/OPEN_QUESTIONS.md`).
