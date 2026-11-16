#!/bin/bash
ACTION=$1
USER=$2
IP=$3

# Olay anının zaman damgasıyla bir test dosyası üret
echo "[$(date)] Active Response tetiklendi! Suricata servisi ile ilgili olay yakalandı." >> /tmp/active_response_test.txt
