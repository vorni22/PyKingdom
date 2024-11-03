#version 330 core

out vec4 FragColor;

in vec3 Normal;
in vec3 FragPos;
in vec3 Color;

uniform vec3 lightColor;
uniform float ambientStrength;
uniform float opacity;

void main(){
    vec3 lightDir = normalize(vec3(0.1, -0.5, 0.3));

	// Ambient
    vec3 ambient = ambientStrength * lightColor;

	// Diffuse
	vec3 norm = normalize(Normal);
	float diff = max(dot(norm, -lightDir), 0.0);
	vec3 diffuse = diff * lightColor;

	vec3 ret = (ambient + diffuse) * Color;

	FragColor = vec4(ret, opacity);
}