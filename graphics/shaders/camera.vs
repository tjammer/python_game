#version 130
out vec4 col;
uniform mat4 mvp;

void main(){
    col = gl_Color;
    gl_Position = mvp * gl_Vertex;
}
