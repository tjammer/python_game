#version 330
in vec4 col;
in vec4 new_pos;
in vec4 new_norm;

void main(){
    gl_FragData[0] = col;
    gl_FragData[1] = new_pos;
    gl_FragData[2] = new_norm;
}
