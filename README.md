Code for the tutorial is located in opengl_tutorial/.

three-server/ contains a JavaScript gRPC server which serves
geometries and materials from
[eulertour/three.js](https://github.com/eulertour/three.js).

In order to run the server, run:
```
cd three-server
git clone https://github.com/eulertour/three.js
npm install
node index.js
```
