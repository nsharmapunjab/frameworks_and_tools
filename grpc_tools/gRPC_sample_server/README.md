# gRPC Sample Server

This is a simple gRPC server for managing products. Main purpose of this sample server is to run it locally to learn testing gRPC APIs

## Prerequisites

- Node.js
- npm

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/uppadhyayraj/gRPC-sample-server.git
    ```
2. Navigate to the project directory:
    ```sh
    cd grpc-server
    ```
3. Install the dependencies:
    ```sh
    npm install
    ```

## Running the Server

To start the gRPC server, run:
```sh
node server.js
```

The server will be running at http://127.0.0.1:50051
### Note
We will not be able to connect and see the above URL in Browser. For this either we have to use a supported tool, and the easiest way is using postman.
https://learning.postman.com/docs/sending-requests/grpc/first-grpc-request/ 

## APIs included in the sample server

### addProduct
- Request
```json
{
  "name": "string",
  "description": "string",
  "price": "number"
}
```
- Response
```json
{
  "product_id": "number",
  "message": "string"
}
```

### getProduct
- Request
```json
{
  "product_id": "number"
}
```
- Response
```json
{
  "product_id": "number",
  "name": "string",
  "description": "string",
  "price": "number"
}
```

### listProducts
- Request
```json
{}
```
- Response
```json
{
  "products": [
    {
      "product_id": "number",
      "name": "string",
      "description": "string",
      "price": "number"
    }
  ]
}
```
