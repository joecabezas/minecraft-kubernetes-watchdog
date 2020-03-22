from datetime import timedelta
from pprint import pprint

from environs import Env
from mcstatus import MinecraftServer
from timeloop import Timeloop

from cluster import Cluster


class Main:
    def __init__(self):
        self.env = Env()
        self.env.read_env()

        self.MINUTES_WITH_NO_PLAYERS = self.env.int('MINUTES_WITH_NO_PLAYERS')
        self.MINECRAFT_SERVER_HOST = self.env('MINECRAFT_SERVER_HOST')
        self.MINECRAFT_SERVER_PORT = self.env('MINECRAFT_SERVER_PORT')

        self.minutes_count = 0

        self.cluster = Cluster()

    def get_server(self):
        return MinecraftServer.lookup("{}:{}".format(
            self.MINECRAFT_SERVER_HOST, self.MINECRAFT_SERVER_PORT))

    def get_players_online(self):
        return self.get_server().status().players.online

    def run(self):
        if not self.cluster.get_deployment_scale().spec.replicas:
            # server has no replicas, nothing to do
            return

        players = self.get_server().status().players.online

        if players:
            self.minutes_count = 0
            return

        self.minutes_count += 1

        if (self.minutes_count >= self.MINUTES_WITH_NO_PLAYERS):
            print('stopping server')
            self.cluster.set_deployment_scale(0)
        pprint(self.minutes_count)


tl = Timeloop()
main = Main()


@tl.job(interval=timedelta(seconds=1))
def job():
    main.run()


if __name__ == '__main__':
    tl.start(block=True)
