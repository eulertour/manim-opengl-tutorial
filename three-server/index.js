THREE = require('three')
var grpc = require("@grpc/grpc-js");
var protoLoader = require("@grpc/proto-loader");
var packageDefinition = protoLoader.loadSync("service.proto", {
  keepCase: true,
  longs: Number,
  enums: String,
  defaults: true,
  oneofs: true,
});
var testservice = grpc.loadPackageDefinition(packageDefinition).testservice;

const perspectiveCamera = new THREE.PerspectiveCamera(45, 1, 0.1, 100)
const orthographicCamera = new THREE.OrthographicCamera(-7.1, 7.1, 4, -4, 1, 21)
perspectiveCamera.position.z = 11;
orthographicCamera.position.z = 11;
const scene = new THREE.Scene()

function getServer() {
  var server = new grpc.Server();
  server.addService(testservice.GeometryService.service, {
    boxGeometry: boxGeometry,
    sphereGeometry: sphereGeometry,
    torusKnotGeometry: torusKnotGeometry,
    icosahedronGeometry: icosahedronGeometry,
    tetrahedronGeometry: tetrahedronGeometry,
    cylinderGeometry: cylinderGeometry,
    coneGeometry: coneGeometry,
    circleGeometry: circleGeometry,
    planeGeometry: planeGeometry,
    extrudeGeometry: extrudeGeometry,
  });
  server.addService(testservice.MaterialService.service, {
    basicMaterial: basicMaterial,
    phongMaterial: phongMaterial,
    standardMaterial: standardMaterial,
  });
  return server;
}

function standardMaterial(call, callback) {
	const scene = new THREE.Scene()
	const material = new THREE.MeshStandardMaterial({});
	const object = new THREE.Mesh(geo, material);
	scene.add(object);

	const pointLight = new THREE.PointLight(0xffffff, 5, 100);
	pointLight.position.set(0, 0, 0);
	scene.add(pointLight);

	const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x000000, 1);
	scene.add(hemisphereLight);

	renderer.render(scene, orthographicCamera);

	callback(null, {
		vertex_shader: renderer.lastProgram.vertexGlsl,
		fragment_shader: renderer.lastProgram.fragmentGlsl,
	});
}

function phongMaterial(call, callback) {
	const scene = new THREE.Scene()
	const material = new THREE.MeshPhongMaterial({});
	const object = new THREE.Mesh(geo, material);
	scene.add(object);

	const pointLight = new THREE.PointLight(0xffffff, 5, 100);
	pointLight.position.set(0, 0, 0);
	scene.add(pointLight);

	const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x000000, 1);
	scene.add(hemisphereLight);

	renderer.render(scene, orthographicCamera);

	callback(null, {
		vertex_shader: renderer.lastProgram.vertexGlsl,
		fragment_shader: renderer.lastProgram.fragmentGlsl,
	});
}

function basicMaterial(call, callback) {
	const scene = new THREE.Scene()
	const material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
	const object = new THREE.Mesh(geo, material);

	scene.add(object);
	renderer.render(scene, perspectiveCamera);

	callback(null, {
		vertex_shader: renderer.lastProgram.vertexGlsl,
		fragment_shader: renderer.lastProgram.fragmentGlsl,
	});
}

function icosahedronGeometry(call, callback) {
	const geometry = new THREE.IcosahedronGeometry(
		call.request.raius || 1,
		call.request.detail || 0,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function torusKnotGeometry(call, callback) {
	const geometry = new THREE.TorusKnotGeometry(
		call.request.torus_radius || 1,
		call.request.tube_radius || 0.4,
		call.request.tubular_segments || 64,
		call.request.radial_segments || 8,
		call.request.p || 2,
		call.request.q || 3,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function boxGeometry(call, callback) {
	const geometry = new THREE.BoxGeometry(
		call.request.width || 1,
		call.request.height || 1,
		call.request.depth || 1,
		call.request.width_segments || 1,
		call.request.height_segments || 1,
		call.request.depth_segments || 1,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function sphereGeometry(call, callback) {
	const geometry = new THREE.SphereGeometry(
		call.request.radius || 1,
		call.request.width_segments || 8,
		call.request.height_segments || 6,
		call.request.phi_start || 0,
		call.request.phi_length || 2 * Math.PI,
		call.request.theta_start || 0,
		call.request.theta_length || Math.PI,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function tetrahedronGeometry(call, callback) {
	const geometry = new THREE.TetrahedronGeometry(
		call.request.radius || 1,
		call.request.detail || 0,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function cylinderGeometry(call, callback) {
	const geometry = new THREE.CylinderGeometry(
		call.request.radius_top || 1,
		call.request.radius_bottom || 1,
		call.request.height || 1,
		call.request.radial_segments || 8,
		call.request.height_segments || 1,
		call.request.open_ended || false,
		call.request.theta_start || 0,
		call.request.theta_length || 2 * Math.PI,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function coneGeometry(call, callback) {
	const geometry = new THREE.ConeGeometry(
    call.request.radius || 1,
    call.request.height || 1,
    call.request.radial_segments || 8,
    call.request.height_segments || 1,
    call.request.open_ended || false,
    call.request.theta_start || 0,
    call.request.theta_length || 2 * Math.PI,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function circleGeometry(call, callback) {
	const geometry = new THREE.CircleGeometry(
    call.request.radius || 1,
    call.request.segments || 8,
    call.request.theta_start || 0,
    call.request.theta_length || 2 * Math.PI,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function planeGeometry(call, callback) {
	const geometry = new THREE.PlaneGeometry(
    call.request.width || 1,
    call.request.height || 1,
    call.request.width_segments || 1,
    call.request.height_segments || 1,
	);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function extrudeGeometry(call, callback) {
  let points = call.request.points;
  let pathIndices = call.request.path_indices;
  
  // Group individual points into groups of three.
  let groupedPoints = [];
  for(let i = 0; i < points.length; i+=3) {
    groupedPoints.push(points.slice(i, i+3));
  }

  // Divide the points into subpaths.
  pathIndices.push(points.length / 3);
  let shapePoints = [];
  for (let i = 0; i < pathIndices.length - 1; i++) {
    shapePoints.push(groupedPoints.slice(pathIndices[i], pathIndices[i+1]));
  }

  function pointInsidePolygon(point, vs) {
    // ray-casting algorithm based on
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html/pnpoly.html
    var x = point[0], y = point[1];
    var inside = false;
    for (var i = 0, j = vs.length - 1; i < vs.length; j = i++) {
        var xi = vs[i][0], yi = vs[i][1];
        var xj = vs[j][0], yj = vs[j][1];
        var intersect = ((yi > y) != (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
  }

  // Assume a path is a hole if its first point is inside the previous shape. Assumes each shape
  // is followed by all of its holes.
  let shapes = [];
  let holes = [];
  for (let i = 0; i < shapePoints.length; i++) {
    let isHole = (shapes.length > 0 && pointInsidePolygon(shapePoints[i][0], shapes[shapes.length-1]));
    if (isHole) {
      holes.push(shapePoints[i]);
    } else {
      shapes.push(shapePoints[i]);
    }
  }

  // Construct the final shape.
  let shape = new THREE.Shape();
  for (let i = 0; i < shapes.length; i++) {
    /**
      [p00, p01, p02]
      [p10, p11, p12]
      [p20, p21, p22]
    **/
    for (let j = 0; j < shapes[i].length; j+=3) {
      if (j == 0) {
        shape.moveTo(shapes[i][j][0], shapes[i][j][1]);
      }
      shape.quadraticCurveTo(shapes[i][j+1][0], shapes[i][j+1][1], shapes[i][j+2][0], shapes[i][j+2][1]);
    }
  }

  for (let i = 0; i < holes.length; i++) {
    let hole = new THREE.Path();
    for (let j = 0; j < holes[i].length; j+=3) {
      if (j == 0) {
        hole.moveTo(holes[i][j][0], holes[i][j][1]);
      }
      hole.quadraticCurveTo(holes[i][j+1][0], holes[i][j+1][1], holes[i][j+2][0], holes[i][j+2][1]);
    }
    shape.holes.push(hole);
  }

  const extrudeSettings = {
    steps: call.request.steps || 1,
    depth: call.request.depth || 1,
    bevelEnabled: call.request.bevel_enabled || false,
    bevelThickness: call.request.bevel_thickness || 0.1,
    bevelSize: call.request.bevel_size || 0.1,
    bevelOffset: call.request.bevel_offset || 0,
    bevelSegments: call.request.bevel_segments || 8
  };

  const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
	callback(null, serializeGeometry(geometry, wireframe=call.request.wireframe));
}

function serializeGeometry(geometry, wireframe=false) {
	let response;
	if (wireframe) {
		let wireframe = new THREE.WireframeGeometry(geometry);
		response = {
			position: Array.from(wireframe.attributes.position.array),
		}
  } else {
		response = {
			position: Array.from(geometry.attributes.position.array),
			normal: Array.from(geometry.attributes.normal.array),
			uv: Array.from(geometry.attributes.uv.array),
		};
		if (geometry.index !== null) {
			response.index = Array.from(geometry.index.array);
		}
	}
	return response;
}

function geometry(call, callback) {
	const geo = new THREE.OctahedronGeometry();
	let resp = {
		position: Array.from(geo.attributes.position.array),
	};
	if (geo.index !== null) {
		resp.index = Array.from(geo.index.array);
	}
	callback(null, resp);
}

global.MockBrowser = require('mock-browser').mocks.MockBrowser;
var mock = new MockBrowser();
global.document = MockBrowser.createDocument();
global.window = MockBrowser.createWindow();

const gl = require("gl")(200, 200);
gl.canvas = new Object()
gl.canvas.width = 200;
gl.canvas.height = 200;
let renderer = new THREE.WebGLRenderer({
    context: gl     // Use the headless-gl context for drawing offscreen
})

const geo = new THREE.BoxGeometry();
// const material = new THREE.MeshBasicMaterial({color: 0x00ff00});
const material = new THREE.MeshPhongMaterial({color: 0x00ff00, specular: 0x555555, shininess: 10});
const obj = new THREE.Mesh(geo, material);
scene.add(obj);

const light = new THREE.PointLight(0xffffff, 5, 100);
light.position.set(5, 5, 5);
scene.add(light);

// const light2 = new THREE.AmbientLight(0x404040); // soft white light
// scene.add(light2);

renderer.render(scene, orthographicCamera);

var testServer = getServer();
testServer.bindAsync('0.0.0.0:50051', grpc.ServerCredentials.createInsecure(), () => {
  testServer.start();
});
