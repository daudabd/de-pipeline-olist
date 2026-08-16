#!/usr/bin/env bash
set -euo pipefail
SG=sg-0502a674da04c236d
REGION=us-west-2
DB=olist-db

IP=$(curl -s https://checkip.amazonaws.com)
echo "Current IP: $IP"

STATUS=$(aws rds describe-db-instances --region "$REGION" \
  --db-instance-identifier "$DB" \
  --query 'DBInstances[0].DBInstanceStatus' --output text)
echo "RDS status: $STATUS"
if [ "$STATUS" = "stopped" ]; then
  aws rds start-db-instance --region "$REGION" --db-instance-identifier "$DB" >/dev/null
  echo "Starting instance — wait 5-10 min."
fi

if aws ec2 authorize-security-group-ingress --region "$REGION" \
     --group-id "$SG" --protocol tcp --port 5432 --cidr "$IP/32" >/dev/null 2>&1; then
  echo "Ingress rule added for $IP/32"
else
  echo "Rule already present for $IP/32"
fi

timeout 10 bash -c "cat </dev/null >/dev/tcp/${DB}.cdeowug6ialz.${REGION}.rds.amazonaws.com/5432" \
  && echo "RDS 5432 OPEN" || echo "RDS 5432 STILL BLOCKED"
