# Create key
openssl genrsa -out ca.key 4096
# Create certificate using congiguration file, validity: 7300 days (20 years)
openssl req -x509 -new -days 7300 -key ca.key -out ca.crt -config ca.cnf -extensions v3_ca

ls -l $PWD/ca.*
