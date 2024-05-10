# Mininet 환경 설정

## `mininet` 설치 

```bash
sudo apt install mininet
# 설치 확인
mn --version
```

## mininet 필수 유틸리티 설치 

```bash
git clone https://github.com/mininet/mininet.git
bash mininet/util/install.sh -fw 
```

## `python3-pip` 및 `iperf` 설치 

```bash
sudo apt install python3-pip iperf3
```

## mininet python 모듈 설치 

```bash
sudo su
pip install mininet
```

## IP Forwarding 활성화 

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

<br/>

# How to merge pcap files
```bash
mergecap router.pcap client.pcap server.pcap -w output.pcap
rm router.pcap client.pcap server.pcap
```

# Activate `pcap`
- move to line 161 in `core/experiment.py` 

# How to run simulation

```bash
sudo python runner.py -t config/topo/topo-15_1000_100_0 -x config/xp/iperf_exp-simple-no
```