# Create private key
openssl genrsa -out client.key 2048
# Create CSR certificate signing request
openssl req -new -key client.key -out client.csr -config client.cnf
# Create client certificate, valid for 7300 days (20 years)
openssl x509 -req -in client.csr -CA ../ca/ca.crt -CAkey ../ca/ca.key -CAcreateserial \
    -out client.crt -days 7300 -extfile client.cnf -extensions v3_req

ls -l $PWD/client.*
