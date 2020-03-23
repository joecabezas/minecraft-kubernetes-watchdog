import logging
from datetime import timedelta

from environs import Env
from mcstatus import MinecraftServer
from timeloop import Timeloop

from cluster import Cluster

env = Env()
env.read_env()

LOG_LEVEL = env('LOG_LEVEL')

EMPTY_SERVER_CHECK_PERIOD = env.int('EMPTY_SERVER_CHECK_PERIOD')
EMPTY_SERVER_CHECK_CYCLES = env.int('EMPTY_SERVER_CHECK_CYCLES')
MINECRAFT_SERVER_HOST = env('MINECRAFT_SERVER_HOST')
MINECRAFT_SERVER_PORT = env('MINECRAFT_SERVER_PORT')

logging.basicConfig(
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    level=getattr(logging, LOG_LEVEL, None))


class Main:
    def __init__(self):
        self.cluster = Cluster()
        self.empty_server_check_count = 0
        self.minecraft_server = self.get_minecraft_server()

    def get_minecraft_server(self):
        return MinecraftServer.lookup("{}:{}".format(MINECRAFT_SERVER_HOST,
                                                     MINECRAFT_SERVER_PORT))

    def get_players_online(self):
        try:
            return self.minecraft_server.status().players.online
        except Exception:
            logging.error("Connection to minecraft server (%s:%s) failed",
                          MINECRAFT_SERVER_HOST, MINECRAFT_SERVER_PORT)
            raise

    def check(self):
        if not self.cluster.get_deployment_status().status.ready_replicas:
            # server has no replicas ready, nothing to do
            return

        players = self.get_players_online()

        if players:
            self.empty_server_check_count = 0
            return

        self.empty_server_check_count += 1

        logging.info("cycles passed with no players: {}".format(
            self.empty_server_check_count))

        if (self.empty_server_check_count >= EMPTY_SERVER_CHECK_CYCLES):
            logging.info('stopping server')
            self.cluster.set_deployment_scale(0)
            self.empty_server_check_count = 0


tl = Timeloop()
main = Main()


@tl.job(interval=timedelta(seconds=EMPTY_SERVER_CHECK_PERIOD))
def job():
    main.check()


if __name__ == '__main__':
    tl.start(block=True)
