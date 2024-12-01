#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormalVector;
layout (location = 2) in vec3 aData;

uniform mat4 model;
uniform mat3 normMatrix;
uniform mat4 view;
uniform mat4 projection;

uniform sampler1D uVisibilityTexture;

uniform float resourceId;
uniform sampler2D uResourcesTexture;

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
    if (resourceId >= 0) {
        vec4 real_pos = model * vec4(aPos, 1.0);

        ivec2 pos = ivec2(gl_InstanceID, resourceId);
        float extract = texelFetch(uResourcesTexture, pos, 0).r;
        float h = texelFetch(uResourcesTexture, pos, 0).g;
        id = int(extract);

        // find real position
        int id_x = int(id) / 40;
        int id_y = int(mod(int(id), 40));

        float R = 1;
        float dR = 0.3;
        float len_x = R * cos(0.523599);
        float len_y = R * sin(0.523599);

        float x_offset = 0;
        if ((int(id_y) & 1) != 0)
            x_offset = len_x + 0.5 * dR;
        float x_pos = x_offset + (2 * len_x + dR) * id_x;
        float y_pos = (len_y + R + dR * sqrt(3.0) / 2.0) * id_y;
        real_pos.x += x_pos;
        real_pos.z += y_pos;
        real_pos.y += h;

        gl_Position = projection * view * real_pos;
    } else {
        id = aData.y;
        gl_Position = projection * view * model * vec4(aPos, 1.0);
    }

    if (id >= 0) {
        visibility = texelFetch(uVisibilityTexture, int(id), 0).r;
    } else {
        visibility = 1.0;
    }

	FragPos = vec3(model * vec4(aPos, 1.0));
	Normal = normMatrix * aNormalVector;

	//Color = color_palet[int(aData.x)];
	Color = texelFetch(color_palette_t, int(aData.x), 0).rgb;
}