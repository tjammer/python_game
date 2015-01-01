#version 330
uniform mat4 mvp;
uniform vec4 quats[33];
uniform vec4 vecs[33];
uniform float scale;
layout(location = 0) in vec4 vert;
layout(location = 1) in vec4 norm;
layout(location = 2) in vec4 o_col;
layout(location = 3) in vec4 weights;
layout(location = 4) in int count;
layout(location = 5) in vec4 bone_ids;
out vec4 col;
out vec4 new_pos;
out vec4 new_norm;

vec4 transform(in vec4 quat, in vec4 vec, in float scale, in vec4 o_pos){
    vec3 pos = vec3(o_pos.xyz);
    vec3 r = vec3(quat.xyz);
    vec3 new = pos + cross(2 * r, (cross(r, pos) + quat.w * pos));
    return vec4(new.xyz, 1) + scale * vec;
}

void main(){
    col = o_col;
    int ct = count;
    ivec4 indices = ivec4(bone_ids);
    new_pos = transform(
        quats[indices.x], vecs[indices.x], scale, vert) * weights.x;
    new_norm = transform(
        quats[indices.x], vecs[indices.x], 0, norm) * weights.x;
    ct = ct - 1;
    if (ct > 0){
        new_pos += transform(
            quats[indices.y], vecs[indices.y], scale, vert) * weights.y;
        new_norm += transform(
            quats[indices.y], vecs[indices.y], 0, norm) * weights.y;
        ct = ct - 1;
    }
    if (ct > 0){
        new_pos += transform(
            quats[indices.z], vecs[indices.z], scale, vert) * weights.z;
        new_norm += transform(
            quats[indices.z], vecs[indices.z], 0, norm) * weights.z;
        ct = ct - 1;
    }
    if (ct > 0){
        new_pos += transform(
            quats[indices.w], vecs[indices.w], scale, vert) * weights.w;
        new_norm += transform(
            quats[indices.w], vecs[indices.w], 0, norm) * weights.w;
    }
    new_pos.w = 1;
    new_norm.w = 1;
    gl_Position = mvp * new_pos;
}
