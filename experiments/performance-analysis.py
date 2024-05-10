from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import time
import os


class PerformanceAnalysisExp(RandomFileExperiment):
    # APPNAME = "qcoap-uni"
    EXP = "simple"
    NC = "10"
    PS = "100"
    PROTOCOL = "udp"
    EXPTYPE = "performance-analysis"
    NAME = "performance-analysis"
    SERVER_LOG = "server-log.txt"
    CLIENT_LOG = "client-log.txt"
    GATEWAY_LOG = "gateway-log.txt"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        # Just rely on RandomFileExperiment
        super(PerformanceAnalysisExp, self).__init__(
            experiment_parameter_filename, topo, topo_config)

        self.EXP = self.experiment_parameter.get("exp")
        self.NC = self.experiment_parameter.get("nc")
        self.PS = self.experiment_parameter.get("ps")
        self.PROTOCOL = self.experiment_parameter.get("protocol")

    def load_parameters(self):
        # Just rely on RandomFileExperiment
        super(PerformanceAnalysisExp, self).load_parameters()

    def prepare(self):
        super(PerformanceAnalysisExp, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " +
                             PerformanceAnalysisExp.CLIENT_LOG)

    def clean(self):
        super(PerformanceAnalysisExp, self).clean()

    def checkNetwork(self, entity):
        self.topo.command_to(entity,
                             "route -n > route.out")
        self.topo.command_to(entity,
                             "ip addr > ipaddr.out")

    def getServerCmd(self, log):
        s = '{}/../utils/pa -p {} -nc {} -ps {} -s > {} &'.format(
            os.path.dirname(os.path.abspath(__file__)),
            self.PROTOCOL,
            self.NC,
            self.PS,
            log,
        )

        return s

    def getGatewayCmd(self, dest, log):
        s = '{}/../utils/pa -p {} -nc {} -ps {} -gw {} > {} &'.format(
            os.path.dirname(os.path.abspath(__file__)),
            self.PROTOCOL,
            self.NC,
            self.PS,
            dest,
            log,
        )

        return s

    def getClientCmd(self, dest, log):
        s = '{}/../utils/pa -p {} -nc {} -ps {} {} > {}'.format(
            os.path.dirname(os.path.abspath(__file__)),
            self.PROTOCOL,
            self.NC,
            self.PS,
            dest,
            log,
        )

        return s

    def run(self):
        self.topo.command_to(self.topo_config.router,
                             "netstat -sn > netstat_router_before")

        serverCmd = self.getServerCmd(self.SERVER_LOG)
        print(serverCmd)
        

        
        clientCmd = self.getClientCmd('{}:5683'.format(self.topo_config.get_client_ip(1, 1)), self.CLIENT_LOG)
        # clientCmd = self.getClientCmd('[fe80::986c:cdff:fe1c:360f]:5683', self.CLIENT_LOG)
        if self.PROTOCOL == 'udpc':
            clientCmd = self.getClientCmd('{}:5684'.format(self.topo_config.get_server_ip(0)), self.CLIENT_LOG)
            # clientCmd = self.getClientCmd('[fe80::986c:cdff:fe1c:360f]:5684', self.CLIENT_LOG)
        print(clientCmd)
        
        # gatewayCmd = self.getGatewayCmd('{}:9999'.format(self.topo_config.get_server_ip(0)), self.GATEWAY_LOG)
        gatewayCmd = self.getGatewayCmd('{}:5684'.format(self.topo_config.get_server_ip(0)), self.GATEWAY_LOG)
        print(gatewayCmd)

        self.topo.command_to(self.topo_config.servers[0], serverCmd)
        time.sleep(1)
        self.topo.command_to(self.topo_config.clients[1], gatewayCmd)

        for i in range(5):
            print('.')
            time.sleep(1)
            
        self.topo.command_to(self.topo_config.clients[0], clientCmd)
        time.sleep(1)

        self.topo.command_to(self.topo_config.router,
                             "netstat -sn > netstat_router_after")
        self.topo.command_to(self.topo_config.servers[0],
                             "pkill -f pa")
        self.topo.command_to(self.topo_config.clients[1],
                             "pkill -f pa")
