#version 330
//diffuse = 0, verts = 1, norms = 2
uniform sampler2D texs[3];
uniform vec3 lightPos;
in vec2 tx_coord;

void main(){
    vec4 col = texture2D(texs[0], tx_coord);
    vec4 norm = texture2D(texs[2], tx_coord);
    float intensity;
    vec4 new_col;
    intensity = dot(normalize(lightPos), normalize(norm.xyz));

    if (intensity > 0.95)
        new_col = col * 2.;
    else if (intensity > 0.5)
        new_col = col * 1.5;
    else
        new_col = col * 1.;
    gl_FragColor = new_col;
}
