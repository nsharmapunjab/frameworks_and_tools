const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const { ReflectionService } = require('@grpc/reflection');



const packageDefinition = protoLoader.loadSync('product.proto', {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});
const productProto = grpc.loadPackageDefinition(packageDefinition).product;

const reflection = new ReflectionService(packageDefinition);

const products = [];

function addProduct(call, callback) {
  const { name, description, price } = call.request;

  if (!name || !description || price == null || !price.toString().trim()) {
    return callback({
      code: grpc.status.INVALID_ARGUMENT,
      message: 'Name, description, and price are required'
    });
  }

  const product = {
    product_id: products.length + 1,
    name,
    description,
    price
  };
  products.push(product);
  callback(null, { product_id: product.product_id, message: 'Product added successfully', code: grpc.status.OK });
}

function getProduct(call, callback) {
  const product = products.find(p => p.product_id === call.request.product_id);
  if (product) {
    callback(null, { ...product, code: grpc.status.OK });
  } else {
    callback({
      code: grpc.status.NOT_FOUND,
      message: 'Product not found'
    });
  }
}

function listProducts(call, callback) {
  callback(null, { products, code: grpc.status.OK });
}

function main() {
  const server = new grpc.Server();
  server.addService(productProto.ProductService.service, {
    addProduct,
    getProduct,
    listProducts
  });

  reflection.addToServer(server);

  server.bindAsync('127.0.0.1:50051', grpc.ServerCredentials.createInsecure(), () => {
    console.log('Server running at http://127.0.0.1:50051');
    server.start();
  });
}

main();
