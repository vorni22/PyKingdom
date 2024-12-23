#version 330 core
#extension GL_ARB_explicit_uniform_location : enable

#define ID_MASK 4095
#define SIDE_MASK 7
#define PLAYER_MASK 7

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

uniform float isPlayer;
uniform float isWall;

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

uniform mat4 side_mat[6];
uniform vec3 player_color[8];

vec4 real_pos_calc(float id, float h) {
    float id_x = floor(id / size_y);
    float id_y = id - size_y * id_x;

    float x_offset = 0;
    if ((int(id_y) & 1) != 0)
        x_offset = len_x + 0.5 * dR;

    return vec4(x_offset + (2 * len_x + dR) * id_x, h, (len_y + R + dR * sqrt(3.0) / 2.0) * id_y, 0.0);
}

void main() {
    if (resourceId >= 0) {
        ivec2 pos = ivec2(gl_InstanceID, resourceId);
        float extract = texelFetch(uResourcesTexture, pos, 0).r;
        float h = texelFetch(uResourcesTexture, pos, 0).g;
        float player_id = texelFetch(uResourcesTexture, pos, 0).b;
        float tmp_id = round(extract);

        if (isWall > 0) {
            int wall_id = int(tmp_id);
            id = (wall_id & ID_MASK);
            int side = (wall_id >> 12) & SIDE_MASK;
            int Player = (wall_id >> 15) & PLAYER_MASK;

            vec4 real_pos = side_mat[side] * model * vec4(aPos, 1.0);

            real_pos += real_pos_calc(id, h);

            gl_Position = projection * view * real_pos;
            Color = player_color[Player];
        } else {
            vec4 real_pos = model * vec4(aPos, 1.0);

            if (isPlayer > 0) {
                int key = int(round(player_id));
                Color = player_color[key];
            }

            id = tmp_id;

            real_pos += real_pos_calc(id, h);

            gl_Position = projection * view * real_pos;
        }
    } else {
        id = round(aData.y);
        gl_Position = projection * view * model * vec4(aPos, 1.0);
    }

    if (id >= 0.0) {
        int key = int(id);
        visibility = texelFetch(uVisibilityTexture, key, 0).r;
    } else {
        visibility = 1.0;
    }

    if (isPlayer > 0 && abs(visibility - 0.7) <= 0.1) {
        visibility = 0.0;
    }

	FragPos = vec3(model * vec4(aPos, 1.0));
	Normal = normMatrix * aNormalVector;

	//Color = color_palet[int(aData.x)];
    if (isWall <= 0 && isPlayer <= 0) {
        int key = int(aData.x);
	    Color = texelFetch(color_palette_t, key, 0).rgb;
	}
}
