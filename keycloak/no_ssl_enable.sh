/opt/keycloak/bin/kcadm.sh config credentials --server http://0.0.0.0:8080 --realm master --user admin --password admin
/opt/keycloak/bin/kcadm.sh update realms/master -s sslRequired=NONE
/opt/keycloak/bin/kcadm.sh update realms/reports-realm -s sslRequired=NONE
