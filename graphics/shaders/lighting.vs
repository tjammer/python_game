#version 330
layout(location = 0) in vec4 vert;
layout(location = 1) in vec2 txcoord;
uniform mat4 mvp;
out vec2 tx_coord;

void main(){
    tx_coord = txcoord;
    gl_Position = mvp * vert;
}
