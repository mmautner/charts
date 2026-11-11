#!/bin/sh
# Source documents into raw/ (not committed). Every figure in data/estimates.csv cites one of these.
mkdir -p raw && cd raw
curl -sL -o mtc-phase1.pdf "https://mtc.ca.gov/sites/default/files/documents/2026-05/Final%20Phase%20One%20Financial%20Efficiency%20Review%20Report_20260527.pdf"
for id in 35113 35950 36128 36143 36364 36796 37000 37001 37123 37136 37536; do
  curl -sL -o "caltrain-$id.pdf" "https://www.caltrain.com/media/$id/download"
done
