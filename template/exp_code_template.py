from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import time
import os
exp_code = '''from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import time
import os

class {}(RandomFileExperiment):
    # APPNAME = "qcoap-uni"
    EXP = "simple"
    DEVS = "1"
    EXPTYPE = "{}"
    NAME = "{}"
    SERVER_LOG = "server-log.txt"
    CLIENT_LOG = "client-log.txt"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super({}, self).__init__(experiment_parameter_filename, topo, topo_config)

        self.EXP = self.experiment_parameter.get("exp")
        self.DEVS = self.experiment_parameter.get("devs")

    def load_parameters(self):
        super({}, self).load_parameters()

    def prepare(self):
        super({}, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " +
                             {}.CLIENT_LOG)

    def clean(self):
        super({}, self).clean()

    def checkNetwork(self, entity):
        self.topo.command_to(entity, "route -n > route.out")
        self.topo.command_to(entity, "ip addr >> route.out")

    def getServerCmd(self, log):
        s = "enter server command"

        return s

    def getClientCmd(self, dest, log):
        s = "enter client command"

        return s

    def run(self):
        self.topo.command_to(
            self.topo_config.servers[1],
            "ip addr > ip.txt",    
        )
        self.topo.command_to(
            self.topo_config.servers[1],
            self.getServerCmd(self.SERVER_LOG),    
        )
        time.sleep(1)

        self.topo.command_to(
            self.topo_config.clients[0],
            self.getClientCmd(
                self.topo_config.get_server_ip(1),
                self.CLIENT_LOG,
            ),
        )'''
        
def getExpCode(className, expName):
    return exp_code.format(className, expName, expName, className, className, className, className, className)
