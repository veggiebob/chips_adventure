#version 330
// no, this isn't python
varying vec2 pixel;
uniform float time;
uniform float game_time;
uniform vec2 mouse;
uniform vec2 camera;
uniform float zoom;
uniform float TELEPORT_DISTANCE;
uniform float lamplight;
uniform float health;
uniform float portal_gut;
uniform bool in_menu;
uniform float dead;
uniform bool won;

uniform sampler2D color_layer;
uniform sampler2D opacity_layer;
uniform sampler2D noise_texture;
uniform sampler2D background;
uniform sampler2D enemy_layer;
uniform sampler2D ui_background;
uniform sampler2D texter;
uniform sampler2D white_noise;

const float TILE_SIZE = 1./12.;
const float march_steps = 128.;
const vec3 lamp_color = vec3(1.0, 1.0, 0.);
const vec3 health_color = vec3(1.0, 0., 0.);
const vec3 coin_color = vec3(0., 0., 1.);
const float button_radius = 0.01;

//text messages
const vec4 t_you_died = vec4(0.5, 0.9609, 0.48, 0.048);
const vec4 t_loading = vec4(0.5, 0.6455, 0.48, 0.048);
const vec4 t_you_won = vec4(0.48, 0.75, 0.34, 0.049);
const vec4 numbers_box = vec4(0.3906, 1.-0.95605, 0.3906, 0.04394);
const vec2 digit_size = vec2(0.078125, 0.088890625);

float rangle (vec2 v) {
    return atan(v.y, v.x);
}
float dangle (float a, float b) {
    float d = abs(a-b);
    return d > 3.14159 ? d - 3.14159 * 2. : d;
}
float sq (float x) {
    return x * x;
}
vec2 max_value (vec2 a, vec2 b) {
    return length(a)>length(b)?a:b;
}
float smooth_mirror (float lb, float ub, float v) {
    return smoothstep(lb, ub, v) + smoothstep(-lb, -ub, -v);
}
vec3 march (vec2 o, vec2 trans) {
    // return vec3 (opacity, newx, newy)
    float br = 1.0;
    float dist = length(o);
    float step_size = dist/march_steps;
    vec2 d = -normalize(o)*step_size;
    vec2 displacement = vec2(0.);

    float wall_time = 0.;
    float portal_time = 0.;
    for (int i = 0; i<int(march_steps); i++) {
        vec3 ct = texture2D(opacity_layer, o - camera + trans).rgb;
        float brc = ct.r*0.12 * dist / zoom;
        br -= brc;
        if (brc > 0.01)
            wall_time = max(wall_time, float(i/march_steps));
        vec2 disp = (ct.gb - 0.50) * 2. * TELEPORT_DISTANCE * zoom;
        o += d;
        displacement = max_value(disp, displacement);
        portal_time = max(portal_time, float(i/march_steps)*smoothstep(0.0, 1.0, length(disp)));
        if (abs(disp.x) > 0.13 || abs(disp.y) > 0.13)
            portal_time = max(portal_time, float(i/march_steps));
    }
    portal_time -= portal_gut;
    float portal_effect = smoothstep(0., 0.1, portal_time - wall_time);
    return vec3(br + (1.-br) * portal_effect, displacement);
}
vec3 distort (vec2 pa, vec2 pb, vec2 uv) {
    //float amount = max(smoothstep(0., 0.2, length(pb-pa)-0.3), portal_gut);
    //vec3 mcolor = texture2D(color_layer, pa).rgb;
    float amount = smoothstep(0.001, 0.05, length(pb-pa));
    float noise = texture2D(noise_texture, pb - time * 0.01).r-0.5;
    vec3 ncolor = texture2D(color_layer, pb + noise * 0.01 * portal_gut).rgb;
    vec2 next_spot = pa + (texture2D(opacity_layer, vec2(pa-uv*zoom)).gb-0.5)*2.*TELEPORT_DISTANCE*zoom;
    vec3 real_next = texture2D(color_layer, next_spot + noise * 0.01 * amount).rgb;
    vec3 scari_monster = texture2D(enemy_layer, next_spot).rgb;
    ncolor += scari_monster;
    if (dot(ncolor, ncolor) < 0.02)
        ncolor = texture2D(background, pb * 5. / zoom + noise * 0.01 * portal_gut).rgb * 0.5;
    return mix(ncolor, real_next, sqrt(portal_gut))-portal_gut;
}
float near0 (float x) {
    return pow(2.7, - x * x);
}
float line (vec2 start, vec2 end, vec2 p) {
    vec2 pa = p-start;
    vec2 ba = end-start;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0., 1.);
    return length(pa - ba * h);
}
float bar (float a, float b, float y, vec2 p, float sharpness) {
    return near0(line(vec2(a, y), vec2(b, y), p) * sharpness);
}
//from https://www.iquilezles.org/www/articles/smin/smin.htm
float smin( float a, float b, float k )
{
    float h = clamp( 0.5+0.5*(b-a)/k, 0.0, 1.0 );
    return mix( b, a, h ) - k*h*(1.0-h);
}
//from https://www.desmos.com/calculator/a1uny6zrtf (sm0(a,b,k))
float smax (float a, float b, float k) {
    return -log(exp(-k*a)+exp(-k*b)) / k;
}
//from https://www.iquilezles.org/www/articles/distfunctions2d/distfunctions2d.htm
float sdBox( in vec2 p, in vec2 b )
{
    vec2 d = abs(p)-b;
    return length(max(d,vec2(0))) + min(max(d.x,d.y),0.0);
}
float button (vec2 uv, vec4 b) {
    return sdBox(uv-b.xy, b.zw) - button_radius;
}
int getDigits (int n) {
    return int(round((log(max(float(n), 1.))/log(10.))));
}
float getText (vec2 p, vec4 b, vec4 d) {
    // p is the point being examined in texture space (uv)
    // b is the bounding box of the image being gotten in image space
    // d is the place to be displayed in texture space (uv)
    b.xy -= b.zw / 2.;
    d.xy -= d.zw / 2.;
    vec2 rel = (p.xy - d.xy) / d.zw;
    rel = clamp(rel, vec2(-0.5), vec2(1.5));
    vec2 pos = b.zw * rel + b.xy;
    return 1.-texture2D(texter, pos).r;
}
//from 0 to 673, 0 to 1024 - 927
//from 0 to 0.65722, 0 to 0.09473
//width of numbers 0.078125‬
float getNumber (vec2 p, vec4 d, int n) {
    //p is the position in texture space (uv)
    //d is the place to be displayed in texture space, for the entire number (uv)
    //n is the number
    int digits = getDigits(n);
    float dw = 2. * d.z / float(digits); // width of a digit in display space
    float br = 0.;
    for (int i = 0; i<digits; i++) {
        int digit = int(mod(n/pow(10., float(digits-i-1.)), 10.));
        float x = (float(digit)+0.5)*digit_size.x; // center x for bounding box
        vec4 digit_box = vec4(x, numbers_box.y, digit_size.xy/2.);
        float dx = (float(i)+0.5)*dw+d.x-d.z; // center of digit in display area
        vec4 display_box = vec4(dx, d.y, dw, d.w) * vec4(1., 1., digit_size.x/digit_size.y, 1.);
        br = max(br, getText(p, digit_box, display_box));
    }
    return br;
}
void main()
{
    float Time = time / 60.;
    vec2 uv = (pixel + 1.)/2.-0.5;
    vec2 tuv = (uv * 2. + 1.) / 2.;
    float luv = length(uv);
    vec2 m = mouse-0.5;

    if (in_menu) {
        vec2 puv = tuv;
        vec2 distort1 = vec2(cos(Time + puv.y * 5.) * 0.05 - cos(Time) * 0.1, -Time*0.3);
        vec2 distort2 = vec2(sin(Time + puv.y * 2.) * 0.025 - cos(Time) * 0.1, -Time*0.5);
        float spark1 = texture2D(white_noise, puv + distort1).r;
        float spark2 = texture2D(white_noise, puv + distort2).r;
        float brightness = 10. - dead * 2.;
        float spark = (pow(spark1, brightness) + pow(spark2, brightness)) * exp(-dot(puv-0.5, puv-0.5) * 2.);
        vec3 spark_accent = spark * vec3(1.0, spark, spark);
        vec3 spark_col = vec3(1.0, 0.7, 0.3) * spark_accent;

        float fire = texture2D(noise_texture, tuv * vec2(5.0, 1.0) - vec2(0., time * 0.001)).r;
        if (dead < 0.5) tuv += (fire-0.5) * 0.02;
        float b = getText(tuv, t_you_died, vec4(0.5, 0.5, 0.5, 0.5 * t_you_died.w / t_you_died.z));
        vec3 accent = sqrt(fire) * vec3(1.0, fire, fire);
        if (won) {
            b = getText(tuv, t_you_won, vec4(0.5, 0.5, 0.5, 0.5 * t_you_won.w / t_you_won.z));
            spark_col = spark_accent * vec3(1.0, 1.0, 0.0);
        }
        b = max(b, getNumber(
            tuv,
            vec4(0.5, 0.3, 0.05 * float(getDigits(int(game_time))), 0.05),
            int(game_time)
        ));
        vec3 col = accent * vec3(1.0, 0.7, 0.3) * b * (1.-dead);
        if (won)
            col = vec3(0., 0.5, 1.0) * b * (1.-dead);
        col += spark_col;
        if (dead > 1.0 && dead < 3.0) { // dead == 2.0 indicates loading phase
            col = vec3(getText(tuv, t_loading, vec4(0.5, 0.5, 0.5, 0.5 * t_loading.w / t_loading.z)));
        }
        if (won)
            col = max(vec3(0.15 * (1.-dead)), col);
        gl_FragColor = vec4(col, 1.0);
    } else {
        float mangle = rangle(m);
        float pangle = rangle(uv);

        float lightness = smoothstep(0.0, 0.1, lamplight);
        float fov = 0.5 * lightness;
        float range = 0.8;
        //get static light value from texture here
        float static_light = 0.0;
        float aura = smoothstep(0.1, 0.06, luv);
        float inAngle = smoothstep(fov, fov/2.5, sq(
            dangle(pangle, mangle)
        )) * sq(smoothstep(range, 0.2, luv)) * lightness;
        inAngle = max(inAngle, aura);

        vec2 muv = uv * zoom;
        vec2 cam_pos = muv - camera;
        vec3 mar = march(muv, vec2(0.));
        float op = mar.x;
        vec2 np = mar.yz;
        float far = smoothstep(0., 0.1, length(np));
        if (far > 0.95) {
            vec3 mar2 = march(muv, np);
            op = min(op, mar2.x);
            //if (op > mar2.x)
            //    op = 3.-mar2.x;
        }

        vec3 fcolor = vec3(1.0, 1.0, 1.0);
        vec3 mcolor = distort(cam_pos, cam_pos + np, uv);
        //op = smoothstep(0.0, 0.4, op);//if you want sharper shadows
        vec3 col =
            fcolor
            * op
            * max(inAngle, static_light)
            * mcolor
        ;

        // ui

        //energy levels
        float lamp_amount = smoothstep(0.1, 0.8, bar(0.3, 0.3 + 0.4 * lamplight, 0.03, tuv, 60.));
        float health_amount = smoothstep(0.1, 0.8, bar(0.1, 0.1 + 0.3 * health, 0.97, tuv, 60.));
        if (lamp_amount > 0.)
            col = mix(vec3(0.), lamp_color, lamp_amount);
        if (health_amount > 0.)
            col = mix(vec3(0.), health_color, health_amount);
        //frame
        vec3 ui_back = texture2D(ui_background, tuv).rgb;
        if (dot(ui_back, ui_back) > 0.)
            col = ui_back;


        // player
        float n = texture2D(
            noise_texture,
            vec2(
                texture2D(noise_texture, uv * 10. + time * 0.01).r,
                texture2D(noise_texture, tuv * 10.).g
            )
        ).r;
        float affect = smoothstep(0.03, 0.02, luv);
        affect = min(affect + n * 0.1, 1.);
        vec3 pcol = vec3(n);
        col = mix(col, pcol, affect);

        gl_FragColor = vec4(col,1.0);
    }
}