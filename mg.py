from ursina import *
from ursina.shaders import basic_lighting_shader as lit
from ursina.shaders import unlit_shader as unlit
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise

app = Ursina()
physics_entities=[]

assets_folder = './assets/'
window.asset_folder = assets_folder

def update():
    for e in physics_entities:
        if e.intersects():
            e.velocity = lerp(e.velocity, Vec3(0), time.dt*10)
            continue
        e.velocity = lerp(e.velocity, Vec3(0), time.dt)
        e.velocity += Vec3(0,-1,0) * time.dt * 5
        e.position += (e.velocity + Vec3(0,-4,0)) * time.dt

class Block(Button):
    def __init__(self, **kwargs):
        super().__init__(model='cube', scale=1, collider='box', **kwargs)
        self.entype="block"
        self.highlight_color = color.light_gray
        if 'grass' in str(self.texture) :
            self.highlight_color = self.color * 0.9
        self.parent = scene

def input(key):
    global CURRENT_BLOCK, BLOCKS
    if key == 'escape':
        quit()
    if mouse.hovered_entity:
        mouse.hovered_entity.shader = lit
        if key == 'right mouse down':
            hit_info = mouse.hovered_entity.intersects()
            if hit_info.hit and mouse.hovered_entity.entype == 'block':
                position = (mouse.normal + mouse.hovered_entity.position)
                block = Button(model='cube', texture=BLOCKS[CURRENT_BLOCK], scale=1, position=position, collider='box')
                if CURRENT_BLOCK == 3 or CURRENT_BLOCK == 5:
                    block.velocity = Vec3(0)
                    physics_entities.append(block)
                block.entype="block"
                block.highlight_color = color.light_gray
                block.color = color.white
                block.parent = scene
        if key == 'left mouse down':
            if mouse.hovered_entity.entype=="block":
                if mouse.hovered_entity in physics_entities:
                    physics_entities.remove(mouse.hovered_entity)
                destroy(mouse.hovered_entity)
    if key.isdigit():
        CURRENT_BLOCK = int(key)-1
        selection.texture = BLOCKS[CURRENT_BLOCK]
    if key == 'r':
        for e in scene.entities:
            if e.entype == 'block':
                destroy(e)
        generate_terrain()
    if key == 'k':
        player.position = (0,0,0)
        player.rotation = (0,0,0)

CURRENT_BLOCK = 0
BLOCKS = ["dirt", "stone", "cobblestone", "sand", "glass", "gravel", "oak_planks", "oak_log", "obsidian"]

mouse.locked = True
Entity.default_shader = lit
Entity.entype="none"

Sky(texture='sky_sunset')

def generate_terrain():
    noise = PerlinNoise(octaves=6, seed=random.randint(0,10000))
    for e in scene.entities:
        if e.entype == 'block':
            destroy(e)
    for z in range(25):
        for x in range(25):
            y = floor(noise([x/100, z/100])*3)
            Block(position=(x,-2,z), texture=BLOCKS[2], color=color.white, shader = unlit)
            block_type = floor(noise([10+x/10, 10+z/10])*5)%3
            Block(position=(x,-1,z), texture=BLOCKS[block_type], color=color.white, shader = lit)
            for i in range(0,y+1):
                Block(position=(x,i,z),texture='grass_block_top', color=rgb(100,200,100))

generate_terrain()

player = FirstPersonController(
 jumping=True,
 gravity=0.8, 
 speed=5,
 jump_height=1.5, 
 mouse_sensitivity=Vec2(100, 100),
 model='sphere',
 shader=unlit,
 color=color.black,
 alpha=0.5
)

selection = Entity(parent=camera.ui, model='cube', texture=BLOCKS[CURRENT_BLOCK], scale=0.2, rotation=Vec3(150,-10,0), position=Vec3(0.6,-0.5,-0.5), color=color.light_gray, shader=lit)
for i in range(len(BLOCKS)):
    Entity(parent=camera.ui, model='quad', texture=BLOCKS[i], scale=0.05, position=(-0.25 + i*0.06, -0.4), shader=unlit)
    Text(text=str(i+1), origin=(0,0), scale=1, position=(-0.25 + i*0.06, -0.4))

light = DirectionalLight(color=rgb(220,200,200)).look_at((0,-0.4,1))

window.title = "MineMine"
window.fullscreen = True
app.run()