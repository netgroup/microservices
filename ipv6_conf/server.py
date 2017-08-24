#!/usr/bin/python

from concurrent import futures
import time
import os
import grpc
import ipset_pb2
import ipset_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
MODE_ADDR = 1;
MODE_ROUTES = 2;
MODE_ADDR_ROUTES = 3;

class GiveMe(ipset_pb2_grpc.IpSetServicer):

	def Set(self, request, context):
		if request.mode == MODE_ADDR:
			set_addrs(request.ipv6, request.subnet, request.iface)
			return ipset_pb2.Reply(message='I have set {} on subnet /{} and interface {}'
										.format(request.ipv6,request.subnet,request.iface))

		elif request.mode == MODE_ROUTES:
			set_routes(request.r_subnets, request.routes, request.r_devs)
			return ipset_pb2.Reply(message='I have set the routes')

		elif request.mode == MODE_ADDR_ROUTES:
			set_addrs(request.ipv6, request.subnet, request.iface)
			set_routes(request.r_subnets, request.routes, request.r_devs)
			return ipset_pb2.Reply(message='I have set {} on subnet /{} and interface {} and set the routes'
										.format(request.ipv6,request.subnet,request.iface))

		else:
			return ipset_pb2.Reply(message="Unrecognized mode")


def set_addrs(ipv6, subnet, iface):
	for i in range(len(ipv6)):
		print "Command: sudo ip -6 addr add "+ipv6[i]+"/"+subnet+" dev "+iface[i]
		os.system("sudo ip -6 addr add "+ipv6[i]+"/"+subnet+" dev "+iface[i])

def set_routes(r_subnets, routes, r_devs):
	os.system('sudo sysctl -w net.ipv6.conf.all.forwarding=1')
	for i in range(len(r_subnets)):
		print "Command: sudo ip -6 r add "+r_subnets[i]+" via "+routes[i]+" dev "+r_devs[i]
		os.system("sudo ip -6 r add "+r_subnets[i]+" via "+routes[i]+" dev "+r_devs[i])

def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
	ipset_pb2_grpc.add_IpSetServicer_to_server(GiveMe(), server)
	server.add_insecure_port('[::]:50001')
	server.start()
	try:
		while True:
			time.sleep(_ONE_DAY_IN_SECONDS)
	except KeyboardInterrupt:
		server.stop(0)

if __name__ == '__main__':
	serve()
