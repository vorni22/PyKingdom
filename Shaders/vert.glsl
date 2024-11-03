#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormalVector;
layout (location = 2) in vec3 aColor;

uniform mat4 model;
uniform mat3 normMatrix;
uniform mat4 view;
uniform mat4 projection;

out vec3 Normal;
out vec3 FragPos;
out vec3 Color;

void main() {
    //mat3 normMatrix = mat3(transpose(inverse(model)));

	gl_Position = projection * view * model * vec4(aPos, 1.0);

	FragPos = vec3(view * model * vec4(aPos, 1.0));
	Normal = normMatrix * aNormalVector;
	Color = aColor;
}