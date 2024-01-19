# How to connect to a jarvis server using vnc

## On the jarvis server

```bash
apt update
apt install -y tigervnc-standalone-server tigervnc-common xvfb icewm
vncserver  # a select a password
```


## On the mac, run a ssh tunnel

Copy the ssh access command from jarvis, for example:
```
# ssh -o StrictHostKeyChecking=no -p 11214 root@ssha.jarvislabs.ai
```

Modify it and run
```bash
ssh -L 5901:localhost:5901 -o StrictHostKeyChecking=no -p 11214 -N root@ssha.jarvislabs.ai
```

## Launch the vnc client on the mac to localhost:5901
