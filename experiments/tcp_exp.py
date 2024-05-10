from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import time
import os

class TcpExp(RandomFileExperiment):
    # APPNAME = "qcoap-uni"
    EXP = "simple"
    DEVS = "1"
    EXPTYPE = "tcp_exp"
    NAME = "tcp_exp"
    SERVER_LOG = "server-log.txt"
    CLIENT_LOG = "client-log.txt"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(TcpExp, self).__init__(experiment_parameter_filename, topo, topo_config)

        self.EXP = self.experiment_parameter.get("exp")
        self.DEVS = self.experiment_parameter.get("devs")

    def load_parameters(self):
        super(TcpExp, self).load_parameters()

    def prepare(self):
        super(TcpExp, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " +
                             TcpExp.CLIENT_LOG)

    def clean(self):
        super(TcpExp, self).clean()

    def checkNetwork(self, entity):
        self.topo.command_to(entity, "route -n > route.out")
        self.topo.command_to(entity, "ip addr >> route.out")

    def getServerCmd(self, log):
        s = '{}/../utils/tcp_pa -s >> {} &'.format(
            os.path.dirname(os.path.abspath(__file__)),
            log,
        )

        return s

    def getClientCmd(self, dest, log):
        s = '{}/../utils/tcp_pa {} >> {}'.format(
            os.path.dirname(os.path.abspath(__file__)),
            dest,
            log,
        )

        return s

    def run(self):
        serverCmd = self.getServerCmd(self.SERVER_LOG)
        clientCmd = self.getClientCmd('{}:8080'.format(self.topo_config.get_server_ip(0)), self.CLIENT_LOG)
        self.topo.command_to(
            self.topo_config.servers[0],
            serverCmd,
        )
        time.sleep(1)

        self.topo.command_to(
            self.topo_config.clients[1],
            clientCmd,
        )