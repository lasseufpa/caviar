import subprocess

class nats:
    def __init__(self):
        subprocess.Popen(
            ["nats-server", "-DV"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def send_message(self):
        nats.send(self.url, self.subject, self.message)
