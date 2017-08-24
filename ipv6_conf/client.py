import grpc
import ipset_pb2
import ipset_pb2_grpc
import time

MODE_ADDR = 1;
MODE_ROUTES = 2;
MODE_ADDR_ROUTES = 3;

def run(remote_ipv4,ipv6,subnet,iface,r_subnets,routes,r_devs,mode):
    ok = False
    while not ok:
        try:
            channel = grpc.insecure_channel(remote_ipv4+":50001")
            stub = ipset_pb2_grpc.IpSetStub(channel)
            response = stub.Set(ipset_pb2.Request(ipv6=ipv6,subnet=subnet,iface=iface,
                                                  r_subnets=r_subnets, routes=routes, r_devs=r_devs,
                                                  mode=mode))
        except grpc._channel._Rendezvous as e:
            print e
            time.sleep(1)
            print "Retrying..."
        else:
            print "Server at {} says: {}".format(remote_ipv4,response.message)
            ok = True


if __name__ == '__main__':
    remote_ipv4_cro3 = "10.0.2.1" # used to contact a node
    ipv6_cro3 = ["fd3c:9f20:5d73:03::01","fd3c:9f20:5d73:05::02","fd3c:9f20:5d73:06::02","fd3c:9f20:5d73:07::01","fd3c:9f20:5d73:0b::02"]
    subnet_cro3 = "64"
    iface_cro3 = ["vi1","vi2","vi3","vi4","vi5"]
    r_subnets_cro3 = ["default","fd3c:9f20:5d73:01::/64","fd3c:9f20:5d73:0a::/64"]
    routes_cro3 = ["fd3c:9f20:5d73:03::02","fd3c:9f20:5d73:05::01","fd3c:9f20:5d73:06::01"]
    r_devs_cro3 = ["vi1","vi2","vi3"]

    remote_ipv4_cro4 = "10.0.1.1" # used to contact a node
    ipv6_cro4 = ["fd3c:9f20:5d73:02::02","fd3c:9f20:5d73:07::02","fd3c:9f20:5d73:08::02"]
    subnet_cro4 = "64"
    iface_cro4 = ["vi1","vi2","vi3"]
    r_subnets_cro4 = ["default","fd3c:9f20:5d73:04::/64","fd3c:9f20:5d73:01::/64","fd3c:9f20:5d73:0b::/64"]
    routes_cro4 = ["fd3c:9f20:5d73:08::01","fd3c:9f20:5d73:02::01","fd3c:9f20:5d73:02::01","fd3c:9f20:5d73:07::01"]
    r_devs_cro4 = ["vi3","vi1","vi1","vi2"]
    
    remote_ipv4_cro5 = "10.0.2.2" # used to contact a node
    ipv6_cro5 = ["fd3c:9f20:5d73:03::02","fd3c:9f20:5d73:04::02","fd3c:9f20:5d73:09::02"]
    subnet_cro5 = "64"
    iface_cro5 = ["vi1","vi2","vi3"]
    r_subnets_cro5 = ["default", "fd3c:9f20:5d73:01::/64", "fd3c:9f20:5d73:0a::/64", "fd3c:9f20:5d73:02::/64", "fd3c:9f20:5d73:08::/64"]
    routes_cro5 = ["fd3c:9f20:5d73:03::01", "fd3c:9f20:5d73:04::01", "fd3c:9f20:5d73:09::01", "fd3c:9f20:5d73:04::01","fd3c:9f20:5d73:09::01"]
    r_devs_cro5 = ["vi1","vi2", "vi3", "vi2", "vi3"]

    remote_ipv4_peo2 = "10.0.0.2" # used to contact a node
    ipv6_peo2 = ["fd3c:9f20:5d73:01::01","fd3c:9f20:5d73:02::01","fd3c:9f20:5d73:04::01","fd3c:9f20:5d73:05::01"]
    subnet_peo2 = "64"
    iface_peo2 = ["vi1","vi2","vi3","vi4"]
    r_subnets_peo2 = ["default","fd3c:9f20:5d73:0b::/64"]
    routes_peo2 = ["fd3c:9f20:5d73:04::02","fd3c:9f20:5d73:05::02"]
    r_devs_peo2 = ["vi1","vi2","vi3","vi2","vi3"]

    remote_ipv4_peo6 = "10.0.5.1" # used to contact a node
    ipv6_peo6 = ["fd3c:9f20:5d73:06::01","fd3c:9f20:5d73:08::01","fd3c:9f20:5d73:09::01","fd3c:9f20:5d73:0a::01"]
    subnet_peo6 = "64"
    iface_peo6 = ["vi1","vi2","vi3","vi4"]
    r_subnets_peo6 = ["default","fd3c:9f20:5d73:0b::/64"]
    routes_peo6 = ["fd3c:9f20:5d73:09::02","fd3c:9f20:5d73:06::02"]
    r_devs_peo6 = ["vi3","vi1"]

    remote_ipv4_cer1 = "10.0.0.1" # used to contact a node
    ipv6_cer1 = ["fd3c:9f20:5d73:01::02"]
    subnet_cer1 = "64"
    iface_cer1 = ["cer1-eth1"]
    r_subnets_cer1 = ["default"]
    routes_cer1 = ["fd3c:9f20:5d73:01::01"]
    r_devs_cer1 = ["cer1-eth1"]

    remote_ipv4_cer7 = "10.0.9.1" # used to contact a node
    ipv6_cer7 = ["fd3c:9f20:5d73:0a::02"]
    subnet_cer7 = "64"
    iface_cer7 = ["cer7-eth1"]
    r_subnets_cer7 = ["default"]
    routes_cer7 = ["fd3c:9f20:5d73:0a::01"]
    r_devs_cer7 = ["cer7-eth1"]

    print "Trying with cro3"
    run(remote_ipv4_cro3,ipv6_cro3,subnet_cro3,iface_cro3,r_subnets_cro3,routes_cro3,r_devs_cro3, MODE_ADDR_ROUTES)
    print "Trying with cro4"
    run(remote_ipv4_cro4,ipv6_cro4,subnet_cro4,iface_cro4,r_subnets_cro4,routes_cro4,r_devs_cro4, MODE_ADDR_ROUTES)
    print "Trying with cro5"
    run(remote_ipv4_cro5,ipv6_cro5,subnet_cro5,iface_cro5,r_subnets_cro5,routes_cro5,r_devs_cro5, MODE_ADDR_ROUTES)
    print "Trying with peo2"
    run(remote_ipv4_peo2,ipv6_peo2,subnet_peo2,iface_peo2,r_subnets_peo2,routes_peo2,r_devs_peo2, MODE_ADDR_ROUTES)
    print "Trying with peo6"
    run(remote_ipv4_peo6,ipv6_peo6,subnet_peo6,iface_peo6,r_subnets_peo6,routes_peo6,r_devs_peo6, MODE_ADDR_ROUTES)
    print "Trying with cer1"
    run(remote_ipv4_cer1,ipv6_cer1,subnet_cer1,iface_cer1,r_subnets_cer1,routes_cer1,r_devs_cer1, MODE_ADDR_ROUTES)
    print "Trying with cer7"
    run(remote_ipv4_cer7,ipv6_cer7,subnet_cer7,iface_cer7,r_subnets_cer7,routes_cer7,r_devs_cer7, MODE_ADDR_ROUTES)
