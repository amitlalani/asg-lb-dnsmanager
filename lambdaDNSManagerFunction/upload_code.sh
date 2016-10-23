set -e
set -u

BUCKET=lamba-dnsmanager
zip code-$1.zip autoscalingDNSManager.py
aws s3 cp code-$1.zip s3://$BUCKET/
