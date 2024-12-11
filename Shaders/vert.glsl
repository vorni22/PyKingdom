#version 330 core
#extension GL_ARB_explicit_uniform_location : enable

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormalVector;
layout (location = 2) in vec3 aData;

uniform mat4 model;
uniform mat3 normMatrix;
uniform mat4 view;
uniform mat4 projection;

layout (location = 0) uniform sampler1D uVisibilityTexture; // 0
layout (location = 1) uniform sampler1D color_palette_t; // 1
layout (location = 2) uniform sampler2D uResourcesTexture; // 2

uniform float resourceId;

uniform float size_x;
uniform float size_y;
uniform float len_x;
uniform float len_y;
uniform float R;
uniform float dR;

out vec3 Normal;
out vec3 FragPos;
out vec3 Color;
out float visibility;
out float id;

void main() {
    if (resourceId >= 0) {
        vec4 real_pos = model * vec4(aPos, 1.0);

        ivec2 pos = ivec2(gl_InstanceID, resourceId);
        float extract = texelFetch(uResourcesTexture, pos, 0).r;
        float h = texelFetch(uResourcesTexture, pos, 0).g;
        id = round(extract);

        // find real position
        float id_x = floor(id / size_y);
        float id_y = id - size_y * id_x;

        float x_offset = 0;
        if ((int(id_y) & 1) != 0)
            x_offset = len_x + 0.5 * dR;
        real_pos.x += x_offset + (2 * len_x + dR) * id_x;
        real_pos.z += (len_y + R + dR * sqrt(3.0) / 2.0) * id_y;
        real_pos.y += h;

        gl_Position = projection * view * real_pos;
    } else {
        id = int(round(aData.y));
        gl_Position = projection * view * model * vec4(aPos, 1.0);
    }

    if (id >= 0) {
        visibility = texelFetch(uVisibilityTexture, int(round(id)), 0).r;
    } else {
        visibility = 1.0;
    }

	FragPos = vec3(model * vec4(aPos, 1.0));
	Normal = normMatrix * aNormalVector;

	//Color = color_palet[int(aData.x)];
	Color = texelFetch(color_palette_t, int(aData.x), 0).rgb;
}
