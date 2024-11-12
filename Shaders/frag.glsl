#version 330 core

out vec4 FragColor;

in vec3 Normal;
in vec3 FragPos;
in vec3 Color;
in float visibility;
in float id;

uniform vec3 lightColor;
uniform float ambientStrength;
uniform float opacity;

layout(location = 0) out vec4 ColorOutput;
layout(location = 1) out ivec4 DataOutput;

void main(){
    if (visibility <= 0.01) {
        ColorOutput = vec4(int(id), 0.0, 0.0, 0.0);
	    return;
    }

    vec3 lightDir = normalize(vec3(0.1, -0.5, 0.3));

	// Ambient
    vec3 ambient = ambientStrength * lightColor;

	// Diffuse
	vec3 norm = normalize(Normal);
	float diff = max(dot(norm, -lightDir), 0.0);
	vec3 diffuse = diff * lightColor;

    float vi = visibility;
    float op = opacity;
    if (visibility < 0.69 && visibility < op) {
        op = visibility;
        vi = 0.69;
    }

	vec3 ret = (ambient + diffuse) * Color * vi;

	ColorOutput = vec4(ret, op);
	DataOutput = ivec4(int(id), 0, 0, 0);
}