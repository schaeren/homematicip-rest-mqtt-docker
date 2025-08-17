# Create private key
openssl genrsa -out server.key 2048
# Create CSR certificate signing request
openssl req -new -key server.key -out server.csr -config server.cnf
# Create server certificate used for TLS/SSL, valid for 7300 days (20 years)
openssl x509 -req -in server.csr -CA ../ca/ca.crt -CAkey ../ca/ca.key -CAcreateserial \
    -out server.crt -days 7300 -extfile server.cnf -extensions v3_req

ls -l $PWD/server.*
