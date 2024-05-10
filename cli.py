# python runner.py -t config/topo/low-delay -x config/xp/low-tcp
import os
import sys
import template

if len(sys.argv) < 2:
    print("enter cli type (run or clean)")
    exit(-1)


def experiment(xpType, exp, pcap, nc, ps, protocol, delay, queueSize, bandwidth, loss):
    # make experimentation and topology config file at config/xp and config/topo respectively.
    xpTmpl = template.xp_template.xp
    topoTmpl = template.topology_template.topo

    # create xpFile
    xpFile = './config/xp/{}-{}-{}-{}-{}-{}'.format(
        xpType, exp, pcap, nc, ps, protocol)
    if not os.path.exists(xpFile):
        f = open(
            xpFile,
            'w+',
        )
        f.write(xpTmpl.format(xpType, exp, pcap, nc, ps, protocol))
        f.close()
    else:
        print('file is already exist')

    # create topoFile
    topoFile = './config/topo/topo-{}_{}_{}_{}'.format(
        delay, queueSize, bandwidth, loss)

    if not os.path.exists(topoFile):
        f = open(topoFile, 'w+')
        f.write(topoTmpl.format(5, delay, queueSize, bandwidth, loss))
        f.close()
    else:
        print('file is already exist')

    # run experimentation
    cmd = 'python runner.py -t {} -x {}'.format(topoFile, xpFile)
    os.system(cmd)
    # os.system('mv avg {}-avg-nc:{}'.format(protocol, nc))
    with open('./avg', 'r') as stream:
        for line in stream:
            print(line)
            os.system("echo {} >> {}-atd-nc:{}".format(line, protocol, nc))

    with open('./packets', 'r') as stream:
        for line in stream:
            print(line)
            os.system("echo {} >> {}-packets-nc:{}".format(line, protocol, nc))

    with open('./netstat_router_after', 'r') as stream:
        for line in stream:
            if line.startswith('    InNoECTPkts: '):
                l = line[len('    InNoECTPkts: '):].rstrip()
                os.system("echo {} >> {}-netstat-nc:{}".format(l, protocol, nc))

            if line.startswith('    InOctets: '):
                l = line[len('    InOctets: '):].rstrip()
                os.system("echo {} >> {}-netstat-inoctets-nc:{}".format(l, protocol, nc))

def runIperf(xpType, exp, pcap, delay, queueSize, bandwidth, loss):
    xpTmpl = template.xp_template.xp
    topoTmpl = template.topology_template.topo

    # create xpFile
    xpFile = './config/xp/{}-{}-{}'.format(
        xpType, exp, pcap)
    if not os.path.exists(xpFile):
        f = open(
            xpFile,
            'w+',
        )
        f.write(xpTmpl.format(xpType, exp, pcap, 0, 0, 0))
        f.close()
    else:
        print('file is already exist')

    # create topoFile
    topoFile = './config/topo/topo-{}_{}_{}_{}'.format(
        delay, queueSize, bandwidth, loss)

    if not os.path.exists(topoFile):
        f = open(topoFile, 'w+')
        f.write(topoTmpl.format(5, delay, queueSize, bandwidth, loss))
        f.close()
    else:
        print('file is already exist')

    # run experimentation
    cmd = 'python runner.py -t {} -x {}'.format(topoFile, xpFile)
    os.system(cmd)
    # os.system('mv avg {}-avg-nc:{}'.format(protocol, nc))



if sys.argv[1] == 'merge':
    if len(sys.argv) < 3:
        print('please enter file name to write')
        exit(0)

    os.system(
        'mergecap client-0.pcap client-1.pcap client-2.pcap client-3.pcap client-4.pcap router.pcap server-0.pcap server-1.pcap server-2.pcap -w {}'.format(sys.argv[2]))

if sys.argv[1] == 'run':
    # protocols = ['udp', 'tcp', 'quic']
    protocols = ['quic']

    for i in range (1):
        for nc in range(1):
            for protocol in protocols:
                experiment(
                    xpType='performance-analysis', 
                    exp='simple',
                    pcap='no',
                    nc=10*nc,
                    ps=400,
                    protocol=protocol,
                    delay=15,
                    queueSize=1000,
                    bandwidth=1000,
                    loss=1,
                )

if sys.argv[1] == 'iperf':
    for i in range (1):
        runIperf(
            xpType='iperf_exp', 
            exp='simple',
            pcap='no',
            delay=15,
            queueSize=1000,
            bandwidth=100,
            loss=0,
        )

elif sys.argv[1] == 'clean':
    def deleteRecursively(fname):
        for root, _, files in os.walk('.'):
            if root[:3] == "./.":
                continue
            for f in files:
                if f == fname:
                    os.remove(os.path.join(root, f))
                    # print(os.listdir('.'))

    os.system('rm netstat*')
    os.system('rm *.pcap')
    os.system('rm server-log.txt')
    os.system('rm client-log.txt')
    os.system('rm *.log')
    os.system('rm *.out')
    os.system('rm -r config/topo/*')
    os.system('rm -r config/xp/*')
    deleteRecursively('ssl-key.log')

elif sys.argv[1] == 'mkexp':
    if len(sys.argv) != 4:
        print("usage python cli.py mkexp ${className} ${expName}")
        exit(-1)
    
    expCode = './experiments/{}.py'.format(sys.argv[3])
    if not os.path.exists(expCode):
        f = open(
            expCode,
            'w+',
        )
        f.write(template.exp_code_template.getExpCode(sys.argv[2], sys.argv[3]))
        f.close()
