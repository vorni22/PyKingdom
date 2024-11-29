#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormalVector;
layout (location = 2) in vec3 aData;

uniform mat4 model;
uniform mat3 normMatrix;
uniform mat4 view;
uniform mat4 projection;

uniform sampler1D uVisibilityTexture;

out vec3 Normal;
out vec3 FragPos;
out vec3 Color;
out float visibility;
out float id;

uniform sampler1D color_palette_t;
/*
uniform vec3 color_palet[] = vec3[](
    vec3(0.41, 0.74, 0.06),     // Plains
    vec3(0.06, 0.74, 0.1),      // Grassland
    vec3(0.74, 0.74, 0.32),     // Shallow Water (floor)
    vec3(0.47, 0.47, 0.33),     // Ocean (floor)
    vec3(0.4, 0.43, 0.43),      // Mountain
    vec3(0.63, 0.78, 0.76),     // Peaks
    vec3(0.0, 0.2, 0.5)         // Water
);
*/

void main() {
    //mat3 normMatrix = mat3(transpose(inverse(model)));

	gl_Position = projection * view * model * vec4(aPos, 1.0);

    id = aData.y;
    visibility = texelFetch(uVisibilityTexture, int(id), 0).r;

	FragPos = vec3(model * vec4(aPos, 1.0));
	Normal = normMatrix * aNormalVector;

	//Color = color_palet[int(aData.x)];
	Color = texelFetch(color_palette_t, int(aData.x), 0).rgb;
}