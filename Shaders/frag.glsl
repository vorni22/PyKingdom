#version 330 core

in vec3 Normal;
in vec3 FragPos;
in vec3 Color;
in float visibility;
in float id;

uniform vec3 lightColor;
uniform float ambientStrength;
uniform float opacity;

uniform float highlight_id;

layout(location = 0) out vec4 ColorOutput;
layout(location = 1) out ivec4 DataOutput;

void main(){
    if (visibility <= 0.01) {
        ColorOutput = vec4(0.0, 0.0, 0.0, 0.0);
        DataOutput = ivec4(floatBitsToInt(id), 0, 0, 0);
	    return;
    }

    vec3 lightDir = normalize(vec3(0.1, -0.5, 0.3));

	// Ambient
    vec3 ambient = ambientStrength * lightColor;

	// Diffuse
	vec3 norm = normalize(Normal);
	float diff = max(dot(norm, -lightDir), 0.0);
	vec3 diffuse = diff * lightColor;

    float hgh = 1.0;
    if (abs(highlight_id - id) <= 0.001 && id >= 0.0) {
        hgh = 0.5;
    }

    float vi = visibility;
    float op = opacity;
    if (visibility < 0.69 && visibility < op && id >= 0.0) {
        op = visibility;
        vi = 0.69;
    }

    vec3 col = Color;
    if (abs(visibility - 0.8) <= 0.01 && id >= 0.0) {
        col = vec3(0.1, 0.965, 1.0);
        vi = 1.0;
    }

	vec3 ret = (ambient + diffuse) * col * vi * hgh;

	ColorOutput = vec4(ret, op);
	DataOutput = ivec4(floatBitsToInt(id), 0, 0, 0);
}