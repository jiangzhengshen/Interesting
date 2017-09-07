// Play with these
var shapeVertexNum = 5; // 3 → 100...
var gridResolution = 5; // 1 → 30
var diffusionConstant = 0.1; // 0.01 → 0.3
var concIncRate = 1.0; // 0.01 → 1.0
var shapeMinDist = 50; // 5 → 200
var shapeDifVel = 0.7; // 0.1 → 0.9

var cons = []; // Grid conscentrations
var grads = [];
var s;
var nX, nY;
var D;
var pg;
var fla;

function setup() {
  createCanvas(600, 600);
  
  pg = createGraphics(width,height);

  // Parameters setup
  s = gridResolution; // Defines the resolution of the simulation [1, width]
  nX = width/s;
  nY = height/s;
  D = diffusionConstant; // Diffusion constant 
  
  // Initial conscentrations
  for(var i=0; i<nX; i++){
    for(var j=0; j<nY; j++){
      cons[idxC(i,j)] = 0.0;
      grads[idxC(i,j)] = createVector(0.0);
    }
  }
  
  fla = new Flake();
  for(let a=0; a<TAU; a+=TAU/shapeVertexNum){
    fla.addPos(width/2+50*cos(a),height/2+50*sin(a));
  }
  
  fla.display();
  
  background(30);
} 

function draw() {
  //background(200,220,255);
  
  pg.loadPixels();
  for(var i=1; i<nX-1; i++){
    for(var j=1; j<nY-1; j++){
      grads[idxC(i,j)].set(cons[idxC(i+1,j)]-cons[idxC(i,j)],
                           cons[idxC(i,j+1)]-cons[idxC(i,j)]);
      // Diffusion: c(t+1) = c(t) + D*Laplacian(c(t))
      // Laplacian(c(t)) calculated with a 5 point stencil 2D
      cons[idxC(i,j)] += D*(cons[idxC(i-1,j)]+cons[idxC(i+1,j)]+
                            cons[idxC(i,j-1)]+cons[idxC(i,j+1)]-
                            4*cons[idxC(i,j)]);
      let pb = pg.pixels[idxP(i*s,j*s)]/255;
      if(pb>0.95){
        cons[idxC(i,j)] = concIncRate; 
      }
    }
  }
  //pg.updatePixels();
  
  pg.background(0);
  
  fla.display();
  fla.grow();
  
  // print(frameRate());
}

// Get the index of the cell from x, y position 
function idxC(x, y){
  return ((x + y*nX)<<0);
}

// Get the index of the pixel red channel from x, y position 
function idxP(x, y){
  return ((4*(x + y*width))<<0);
}

var Flake = function(){
  this.pos = [];
}
Flake.prototype = {
  addPos: function(x,y){
    this.pos.push(createVector(x,y));
  },
  display: function(){
    pg.fill(255,0,0);
    pg.noStroke();
    pg.beginShape();
    for(p of this.pos){
      pg.curveVertex(p.x,p.y);
    }
    pg.endShape(CLOSE);
    
    stroke(100,255,255,20);
    noFill();
       
    beginShape();
    for(p of this.pos){
      curveVertex(p.x,p.y); // vertex() → no bug
    }
    endShape(CLOSE);
  },
  grow: function(){
    for(p of this.pos){
      let u = grads[idxC(((p.x/s)<<0),((p.y/s)<<0))].mult(-shapeDifVel);
      p.add(u);
    }
    // Subdivision
    for(let i=0; i<this.pos.length; i++){
      let ip = i>0? (i-1) : (this.pos.length-1);
      let dsq = (this.pos[ip].x-this.pos[i].x)*(this.pos[ip].x-this.pos[i].x)+
                (this.pos[ip].y-this.pos[i].y)*(this.pos[ip].y-this.pos[i].y);
      if(dsq>shapeMinDist){
        let mid = p5.Vector.add(this.pos[i],this.pos[ip]).mult(0.5);
        this.pos.splice(i,0,mid);
      }
    }
  }
}