from core.topo import Topo, TopoConfig, TopoParameter
import logging


class MultiInterfaceMultiClientsTopo(Topo):
    NAME = "MultiInterfaceMultiClients"

    def __init__(self, topo_builder, parameterFile):
        logging.info("Initializing MultiInterfaceMultiClientsTopo...")
        super(MultiInterfaceMultiClientsTopo, self).__init__(

            topo_builder, parameterFile)
        self.router = self.add_router()

        # For each client-router, add a client
        print(len(self.get_client_to_router_links()))
        c2r_link_characteristics = self.get_client_to_router_links()

        client = self.add_client()
        self.c2r_links = [] 
        for l in c2r_link_characteristics:
            self.c2r_links.append(self.add_bottleneck_link(
                client, self.router, link_characteristics=l))

        for _ in range(1, self.topo_parameter.clients):
            self.add_client_with_link()

        # For each server-router, add a server
        r2s_link_characteristics = self.get_router_to_server_links()

        server = self.add_server()
        self.r2s_links = [] 
        for l in r2s_link_characteristics:
            self.r2s_links.append(self.add_bottleneck_link(
                server, self.router, link_characteristics=l))

        for _ in range(1, self.topo_parameter.servers):
            self.add_server_with_link()

    def add_client_with_link(self):
        client = self.add_client()
        for l in self.c2r_links:
            self.add_link(client, l.get_left())

    def add_server_with_link(self):
        server = self.add_server()
        for l in self.r2s_links:
            self.add_link(server, l.get_left())

        
    def get_client_to_router_links(self):
        return [l for l in self.topo_parameter.link_characteristics if l.link_type == "c2r"]
    
    def get_router_to_server_links(self):
        return [l for l in self.topo_parameter.link_characteristics if l.link_type == "r2s"]
    
    def __str__(self):
        s = "Multiple interface topology with several clients and servers\n"
        return s


class MultiInterfaceMultiClientsConfig(TopoConfig):
    NAME = "MultiInterfaceMultiClients"


    def __init__(self, topo, param):
        super(MultiInterfaceMultiClientsConfig, self).__init__(topo, param)
        
    # configure_routing 함수를 오버라이딩
    # 각각의 라우터에 대한 라우팅 테이블을 설정
    def configure_routing(self):
        for client_index, client in enumerate(self.clients):
            for i, _ in enumerate(self.topo.c2r_links):
                cmd = self.add_table_route_command(
                    from_ip = self.get_client_ip(i, client_index), 
                    id = i,
                )
                self.topo.command_to(client, cmd)

                # 아래 주석 제거 시 같은 네트워크에 있는 클라이언트 경우에는 router를 경유하지 않고 바로 연결
                # cmd = self.add_link_scope_route_command (
                #     network = self.get_client_subnet(i),
                #     interface_name = self.get_client_interface(client_index, i), 
                #     id = i,
                # )
                # self.topo.command_to(client, cmd)

                cmd = self.add_table_default_route_command(
                    via = self.get_router_ip_to_client_switch(i),
                    id = i,
                )
                self.topo.command_to(client, cmd)

        for server_index, server in enumerate(self.servers):
            for i, _ in enumerate(self.topo.r2s_links):
                cmd = self.add_table_route_command(
                    from_ip = self.get_server_ip(i, server_index), 
                    id = i,
                )
                self.topo.command_to(server, cmd)

                # 아래 주석 제거 시 같은 네트워크에 있는 클라이언트 경우에는 router를 경유하지 않고 바로 연결
                # cmd = self.add_link_scope_route_command(
                #     network = self.get_server_subnet(i),
                #     interface_name = self.get_server_interface(server_index, i), 
                #     id = i,
                # )
                # self.topo.command_to(server, cmd)

                cmd = self.add_table_default_route_command(
                    via = self.get_router_ip_to_server_switch(i),
                    id = i, 
                )
                self.topo.command_to(server, cmd)

        for client_index, client in enumerate(self.clients):
            cmd = self.add_global_default_route_command(
                    self.get_router_ip_to_client_switch(0),
                    self.get_client_interface(client_index = client_index, interface_index = 0),
                )
            self.topo.command_to(client, cmd)

        for server in self.topo.servers:
            # Routing for the congestion server
            cmd = self.add_simple_default_route_command(
                via = self.get_router_ip_to_server_switch(0),
            )
            self.topo.command_to(server, cmd)

    def configure_interfaces(self):
        logging.info(
            "Configure interfaces using MultiInterfaceMultiClients...")
        super(MultiInterfaceMultiClientsConfig, self).configure_interfaces()
        self.clients = [self.topo.get_client(
            i) for i in range(0, self.topo.client_count())]
        self.client = self.clients[0]
        self.router = self.topo.get_router(0)

        self.servers = [self.topo.get_server(
            i) for i in range(0, self.topo.server_count())]
        self.server = self.servers[0]

        netmask = "255.255.255.0"

        # configurations for clients to router links
        for client_index, client in enumerate(self.clients):
            for i, _ in enumerate(self.topo.c2r_links):
                # Make up the client interface and configure client IP
                cmd = self.interface_up_command(
                    interface_name = self.get_client_interface(client_index, i), 
                    ip = self.get_client_ip(i, client_index), 
                    subnet = netmask,
                )
                self.topo.command_to(client, cmd)
                
                # configure client MAC
                client_interface_mac = client.intf(
                    self.get_client_interface(client_index, i)).MAC()
                # configure ARP table of router
                self.topo.command_to(
                    self.router, f"arp -s {self.get_client_ip(i, client_index)} {client_interface_mac}",
                )

                if self.topo.get_client_to_router_links()[i].backup:
                    cmd = self.interface_backup_command(
                        self.get_client_interface(client_index, i))
                    self.topo.command_to(client, cmd)

        # configurations for router to client links
        for i, _ in enumerate(self.topo.c2r_links):
            # Make up the router interface and configure router IP
            cmd = self.interface_up_command(
                interface_name = self.get_router_interface_to_client_switch(i),
                ip = self.get_router_ip_to_client_switch(i), 
                subnet = netmask,
            )
            self.topo.command_to(self.router, cmd)

            # configure router MAC
            router_interface_mac = self.router.intf(
                self.get_router_interface_to_client_switch(i)).MAC()
            # configure ARP table of client

            for client in self.clients:
                self.topo.command_to(client, f"arp -s {self.get_router_ip_to_client_switch(i)} {router_interface_mac}")
        
        if len(self.topo.r2s_links) == 0:
            # Add default route to router
            cmd = self.interface_up_command(
                interface_name = self.get_router_interface_to_server_switch(0),
                ip = self.get_router_ip_to_server_switch(0), 
                subnet = netmask, 
            )
            self.topo.command_to(self.router, cmd)

            router_interface_mac = self.router.intf(
                self.get_router_interface_to_server_switch(i)).MAC()
            for server in self.servers:
                self.topo.command_to(server, "arp -s {} {}".format(
                    self.get_router_ip_to_server_switch(i), router_interface_mac))

            # Add default route to server
            for server_index, server in enumerate(self.servers):
                cmd = self.interface_up_command(
                    interface_name = self.get_server_interface(server_index, 0), 
                    ip = self.get_server_ip(0, server_index), 
                    subnet = netmask,
                )
                self.topo.command_to(server, cmd)

                server_interface_mac = server.intf(
                    self.get_server_interface(server_index, 0)).MAC()
                self.topo.command_to(self.router, "arp -s {} {}".format(
                    self.get_server_ip(0, server_index), server_interface_mac))
        else:
            # Add default route to server
            for server_index, server in enumerate(self.servers):
                for i, _ in enumerate(self.topo.r2s_links):
                    cmd = self.interface_up_command(
                        interface_name = self.get_server_interface(server_index, i), 
                        ip = self.get_server_ip(i, server_index), 
                        subnet = netmask,
                    )
                    self.topo.command_to(server, cmd)

                    server_interface_mac = server.intf(
                        self.get_server_interface(server_index, i)).MAC()
                    self.topo.command_to(self.router, "arp -s {} {}".format(
                        self.get_server_ip(i, server_index), server_interface_mac))
                    
            # Add default route to router
            for i, _ in enumerate(self.topo.r2s_links):
                cmd = self.interface_up_command(
                    interface_name = self.get_router_interface_to_server_switch(i),
                    ip = self.get_router_ip_to_server_switch(i), 
                    subnet = netmask, 
                )
                self.topo.command_to(self.router, cmd)

                router_interface_mac = self.router.intf(
                    self.get_router_interface_to_server_switch(i)).MAC()
                for server in self.servers:
                    self.topo.command_to(server, "arp -s {} {}".format(
                        self.get_router_ip_to_server_switch(i), router_interface_mac))

    def get_client_ip(self, interface_index = 0, client_index = 0):
        # example: 
        # if leftSubnet is 192.168.
        # if interface_index is 5
        # if client_index is 0
        # then return value is 192.168.5.2
        return f"{self.param.get(TopoParameter.LEFT_SUBNET)}{interface_index}.{client_index+2}"
    
    def get_client_subnet(self, interface_index):
        # example: 
        # if leftSubnet is 192.168.
        # if interface_index is 5
        # then return value is 192.168.5.0/24
        return f"{self.param.get(TopoParameter.LEFT_SUBNET)}{interface_index}.0/24"
    
    def get_server_ip(self, interface_index = 0, server_index = 0 ):
        # example: 
        # if rightSubnet is 10.10.
        # if interface_index is 5
        # if servef_index is 0
        # then return value is 10.10.5.2
        return f"{self.param.get(TopoParameter.RIGHT_SUBNET)}{interface_index}.{server_index+2}"
    
    def get_server_subnet(self, interface_index):
        return f"{self.param.get(TopoParameter.RIGHT_SUBNET)}{interface_index}.0/24"

    def get_router_ip_to_client_switch(self, switch_index):
        return "{}{}.1".format(self.param.get(TopoParameter.LEFT_SUBNET), switch_index)
    
    def get_router_ip_to_server_switch(self, switch_index):
        return f"{self.param.get(TopoParameter.RIGHT_SUBNET)}{switch_index}.1"

    def client_interface_count(self):
        return max(len(self.topo.c2r_links), 1)

    def server_interface_count(self):
        return max(len(self.topo.r2s_links), 1)
    
    def get_router_interface_to_server_switch(self, switch_index):
        return self.get_router_interface_to_client_switch(len(self.topo.c2r_links) + switch_index)

    def get_client_interface(self, client_index, interface_index):
        return "{}-eth{}".format(self.topo.get_client_name(client_index), interface_index)

    def get_router_interface_to_client_switch(self, interface_index):
        return "{}-eth{}".format(self.topo.get_router_name(0), interface_index)

    def get_server_interface(self, server_index, interface_index):
        return "{}-eth{}".format(self.topo.get_server_name(server_index), interface_index)
