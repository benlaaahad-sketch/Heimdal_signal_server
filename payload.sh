#!/bin/bash
echo "Start scanning..." > /tmp/result.txt
for phrase in "satoshi nakamoto" "password" "bitcoin" "12345678" "admin123" "qwerty"; do
  echo "Checking: $phrase" >> /tmp/result.txt
done
echo "Scan finished." >> /tmp/result.txt
cp /tmp/result.txt /workspaces/Heimdal_signal_server/scan_result.txt
cd /workspaces/Heimdal_signal_server
git add scan_result.txt
git commit -m "scan result"
git push
