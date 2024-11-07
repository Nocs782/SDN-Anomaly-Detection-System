from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

class CustomSingleTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        
        s1 = self.addSwitch('s1', cls=OVSSwitch, protocols='OpenFlow13')
        
        self.addLink(h1, s1)
        self.addLink(h2, s1)

def run_topology():
    topo = CustomSingleTopo()
    net = Mininet(topo=topo, controller=None)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    net.start()
    
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_topology()
