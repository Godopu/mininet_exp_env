from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import time
import os

class PingExp(RandomFileExperiment):
    # APPNAME = "qcoap-uni"
    EXP = "simple"
    DEVS = "1"
    EXPTYPE = "ping_exp"
    NAME = "ping_exp"
    SERVER_0_LOG = "server-0-log.txt"
    SERVER_1_LOG = 'server-1-log.txt'
    CLIENT_0_LOG = "client-0-log.txt"
    CLIENT_1_LOG = "client-1-log.txt"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(PingExp, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.EXP = self.experiment_parameter.get("exp")

    def load_parameters(self):
        super(PingExp, self).load_parameters()

    # Delete the existing log files
    def prepare(self):
        super(PingExp, self).prepare()
        self.topo.command_to(self.topo_config.clients[0], f'rm {PingExp.CLIENT_0_LOG}')
        self.topo.command_to(self.topo_config.servers[0], f'rm {PingExp.SERVER_0_LOG}')
        self.topo.command_to(self.topo_config.clients[1], f'rm {PingExp.CLIENT_1_LOG}')
        self.topo.command_to(self.topo_config.servers[1], f'rm {PingExp.SERVER_1_LOG}')

    def clean(self):
        super(PingExp, self).clean()

    def checkNetwork(self, entity):
        self.topo.command_to(entity, "route -n > route.out")
        self.topo.command_to(entity, "ip addr >> route.out")

    def get_ping_command(self, dest, log):
        s = "ping -c 5 {} >> {}".format(dest, log)

        return s

    def run(self):
        # client 0 to server 0 on path 0
        self.topo.command_to(
            self.topo_config.clients[0],
            self.get_ping_command(
                self.topo_config.get_server_ip(0, 0),
                self.CLIENT_0_LOG,
            ),
        )

        # server 0 to server 1 on path 1
        self.topo.command_to(
            self.topo_config.servers[0],
            self.get_ping_command(
                self.topo_config.get_server_ip(1, 1),
                self.SERVER_0_LOG,
            ),
        )

        # server 1 to client 1 on path 0
        self.topo.command_to(
            self.topo_config.servers[1],
            self.get_ping_command(
                self.topo_config.get_client_ip(0, 1),
                self.SERVER_1_LOG,
            ),
        )

        # client 1 to client 0 on path 1
        self.topo.command_to(
            self.topo_config.clients[1],
            self.get_ping_command(
                self.topo_config.get_client_ip(1, 0),
                self.CLIENT_1_LOG,
            ),
        )