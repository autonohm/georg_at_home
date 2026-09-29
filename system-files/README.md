# Georg system files
*This directory contains the configuration files and setup guide for georg's system setup.*  
Versioning these files helps keep track of changes, and prevents deletion scenarios.

## Install configuration
Files are laid out in the same way that they would be in the system.
> e.g. `etc/NetworkManager/xyz` → `/etc/NetworkManager/xyz`

## PC Installation
*set up this repo on your personal computer*  
`./setup-PC.sh` provided here automatically sets everything up.

```shell
mkdir ~/Code #change this however you like
cd ~/Code
git clone https://github.com/autonohm/georg_at_home.git
cd georg_at_home/system-files
./setup-PC.sh
```

## Robot Installation
*set up this repo on the jetson*  
`./setup-PC.sh` provided here automatically sets everything up.

```shell
# install dependencies
sudo apt update && sudo apt install ca-certificates curl git

mkdir ~/app
cd ~/app
git clone https://github.com/autonohm/georg_at_home.git
cd georg_at_home/system-files
./setup-PC.sh
```