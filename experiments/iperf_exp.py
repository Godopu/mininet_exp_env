from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import time
import os

class IperfExp(RandomFileExperiment):
    # APPNAME = "qcoap-uni"
    EXP = "simple"
    EXPTYPE = "iperf_exp"
    NAME = "iperf_exp"
    SERVER_0_LOG = "server-0-log.txt"
    SERVER_1_LOG = 'server-1-log.txt'
    CLIENT_0_LOG = "client-0-log.txt"
    CLIENT_1_LOG = "client-1-log.txt"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(IperfExp, self).__init__(experiment_parameter_filename, topo, topo_config)

        self.EXP = self.experiment_parameter.get("exp")

    def load_parameters(self):
        super(IperfExp, self).load_parameters()

    def prepare(self):
        super(IperfExp, self).prepare()
        self.topo.command_to(self.topo_config.clients[0], f'rm {IperfExp.CLIENT_0_LOG}')
        self.topo.command_to(self.topo_config.servers[0], f'rm {IperfExp.SERVER_0_LOG}')
        self.topo.command_to(self.topo_config.clients[1], f'rm {IperfExp.CLIENT_1_LOG}')
        self.topo.command_to(self.topo_config.servers[1], f'rm {IperfExp.SERVER_1_LOG}')

    def clean(self):
        super(IperfExp, self).clean()

    def checkNetwork(self, entity):
        self.topo.command_to(entity, "route -n > route.out")
        self.topo.command_to(entity, "ip addr >> route.out")

    def getServerCmd(self, log):
        s = f'iperf -s >> {log} &'

        return s

    def getClientCmd(self, dest, log):
        s = f"iperf -c {dest} -t 10 >> {log}"

        return s

    def run(self):
        self.topo.command_to(
            self.topo_config.servers[0],
            self.getServerCmd(self.SERVER_0_LOG),    
        )

        self.topo.command_to(
            self.topo_config.clients[0],
            self.getServerCmd(self.CLIENT_0_LOG),    
        )

        time.sleep(1)

        self.topo.command_to(
            self.topo_config.clients[1],
            self.getClientCmd(
                self.topo_config.get_client_ip(0, 0),
                self.CLIENT_1_LOG,
            ),
        )

        self.topo.command_to(
            self.topo_config.clients[1],
            self.getClientCmd(
                self.topo_config.get_server_ip(0, 0),
                self.CLIENT_1_LOG,
            ),
        )

        self.topo.command_to(
            self.topo_config.servers[1],
            self.getClientCmd(
                self.topo_config.get_server_ip(0, 0),
                self.SERVER_1_LOG,
            ),
        )

        self.topo.command_to(
            self.topo_config.servers[1],
            self.getClientCmd(
                self.topo_config.get_client_ip(0, 0),
                self.SERVER_1_LOG,
            ),
        )


