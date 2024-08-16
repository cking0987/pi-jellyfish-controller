# pi-jellyfish-controller

This project allows a Raspberry Pi to be used to control a motor to raise and lower an artificial jellyfish.

## swim_on_boot

To allow the motor to start automatically when the pi boots...

```sh
sudo cp jellyfish.service /etc/systemd/system/jellyfish.service
```

```sh
sudo systemctl daemon-reload
```

```sh
sudo systemctl start jellyfish
```

```sh
sudo systemctl enable jellyfish # enable the service to start of boot
```

```sh
sudo systemctl status jellyfish # verify that the service is running
```
