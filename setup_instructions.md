# Instructions for setting up a new rpi

## Install prereqs

``` sh
sudo apt update
sudo apt install python3-pip
sudo pip3 install flask --break-system-packages
```

## Set up git

```sh
sudo apt install git
ssh-keygen -t ed25519 -C "cking0987@gmail.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
# Now log in to Github and add a new SSH key. To get the public key:
cat ~/.ssh/id_ed25519.pub
# Once the SSH key has been added to Github...
git clone git@github.com:cking0987/pi-jellyfish-controller.git
cd pi-jellyfish-controller
```

## Setting up the service

```sh
sudo cp jellyfish.service /etc/systemd/system/jellyfish.service
sudo systemctl daemon-reload
sudo systemctl start jellyfish
sudo systemctl enable jellyfish # enable the service to start of boot
sudo systemctl status jellyfish # verify that the service is running 
```
