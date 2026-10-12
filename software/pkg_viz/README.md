# viz

Visualisation package (RVIZ + RQT)

## update rviz config

mount the config as read-write
```diff
- ./config/:/root/config:ro
+ ./config/:/root/config
```

restart the container,  
then press save in rviz

make sure to drop unnecessary changes!
The config also saves you display layout.

Once you are done switch back to the read-only mount.

## switch dark/light mode
edit the [qt5ct.conf](./config/qt5ct/qt5ct.conf):

```conf
[Appearance]
color_scheme_path=/root/.config/qt5ct/colors/gruvbox-light.conf
```

becomes

```conf
[Appearance]
color_scheme_path=/root/.config/qt5ct/colors/gruvbox-dark.conf
```

You can also add theme files [here](./config/qt5ct/colors/)
