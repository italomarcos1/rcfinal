#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink

def topology():

        net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )

        # Add hosts and switches

        host1 = net.addHost( 'host1', ip="10.0.1.10/24", mac="00:00:00:00:00:01" )
        host2 = net.addHost( 'host2', ip="10.0.2.10/24", mac="00:00:00:00:00:02" )
        host3 = net.addHost( 'host3', ip="10.0.1.20/24", mac="00:00:00:00:00:03" )
        host4 = net.addHost( 'host4', ip="10.0.2.20/24", mac="00:00:00:00:00:04" )
        
        roteador = net.addHost( 'roteador' ) # define o roteador
        switch1 = net.addSwitch( 'switch1' ) # define o switch
        switch2 = net.addSwitch( 'switch2' ) # define o switch

        c0 = net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6633 ) # define um controller que gerencia os switches

        net.addLink( roteador, switch1 ) # conecta o roteador ao switch 1
        net.addLink( roteador, switch2 ) # conecta o roteador ao switch 2

        net.addLink( host1, switch1 ) # conecta o host ao switch 1
        net.addLink( host3, switch1 ) # conecta o host ao switch 1
        net.addLink( host2, switch2 ) # conecta o host ao switch 2
        net.addLink( host4, switch2 ) # conecta o host ao switch 2

        net.build()

        c0.start() 

        switch1.start( [c0] ) # inicia o switch1
        switch2.start( [c0] ) # inicia o switch2

        roteador.cmd("ifconfig roteador-eth0 0") # define a interface de subrede 1
        roteador.cmd("ifconfig roteador-eth1 0") # define a interface de subrede 2
        roteador.cmd("ifconfig roteador-eth0 hw ether 00:00:00:00:01:01") # associa um endereço MAC à interface
        roteador.cmd("ifconfig roteador-eth1 hw ether 00:00:00:00:01:02") # associa um endereço MAC à interface
        roteador.cmd("ip addr add 10.0.1.1/24 brd + dev roteador-eth0") # define um endereço IP pra interface de subrede
        roteador.cmd("ip addr add 10.0.2.1/24 brd + dev roteador-eth1") # define um endereço IP pra interface de subrede
        roteador.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")

        host1.cmd("ip route add default via 10.0.1.1") # define um endereço IP pro host1
        host2.cmd("ip route add default via 10.0.2.1") # define um endereço IP pro host2
        host3.cmd("ip route add default via 10.0.1.1") # define um endereço IP pro host3
        host4.cmd("ip route add default via 10.0.2.1") # define um endereço IP pro hostr

        switch1.cmd("ovs-ofctl add-flow switch1 priority=1,arp,actions=flood") #o switch age efetuando flood
        switch1.cmd("ovs-ofctl add-flow switch1 priority=65535,ip,dl_dst=00:00:00:00:01:01,actions=output:1") # associa a interface de subrede ao switch
        switch1.cmd("ovs-ofctl add-flow switch1 priority=10,ip,nw_dst=10.0.1.10,actions=output:2") # associa o host1 ao switch
        switch1.cmd("ovs-ofctl add-flow switch1 priority=10,ip,nw_dst=10.0.1.20,actions=output:3") # associa o host3 ao switch

        switch2.cmd("ovs-ofctl add-flow switch2 priority=1,arp,actions=flood")
        switch2.cmd("ovs-ofctl add-flow switch2 priority=65535,ip,dl_dst=00:00:00:00:01:02,actions=output:1")
        switch2.cmd("ovs-ofctl add-flow switch2 priority=10,ip,nw_dst=10.0.2.10,actions=output:2") # associa o host2 ao switch
        switch2.cmd("ovs-ofctl add-flow switch2 priority=10,ip,nw_dst=10.0.2.20,actions=output:3") # associa o host4 ao switch

        CLI( net )

        net.stop()

      

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()  