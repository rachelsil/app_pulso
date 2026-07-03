from pygame import *

# --- CLASES ---

class GameSprite(sprite.Sprite):
    def __init__(self, imagen_jugador, pos_x, pos_y, ancho, alto):
        super().__init__()
        self.image = transform.scale(image.load(imagen_jugador), (ancho, alto))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def dibujar(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, imagen, x, y, ancho, alto, vel_x, vel_y):
        super().__init__(imagen, x, y, ancho, alto)
        self.vel_x = vel_x
        self.vel_y = vel_y

    def actualizar(self):
        # Movimiento Horizontal y bordes
        self.rect.x += self.vel_x
        if self.rect.x < 0: self.rect.x = 0
        elif self.rect.x > ancho_ventana - 80: self.rect.x = ancho_ventana - 80
        
        # Colisión horizontal con paredes
        choque_paredes = sprite.spritecollide(self, barreras, False)
        for p in choque_paredes:
            if self.vel_x > 0: self.rect.right = p.rect.left
            elif self.vel_x < 0: self.rect.left = p.rect.right

        # Movimiento Vertical y bordes
        self.rect.y += self.vel_y
        if self.rect.y < 0: self.rect.y = 0
        elif self.rect.y > alto_ventana - 80: self.rect.y = alto_ventana - 80
            
        # Colisión vertical con paredes
        choque_paredes = sprite.spritecollide(self, barreras, False)
        for p in choque_paredes:
            if self.vel_y > 0: self.rect.bottom = p.rect.top
            elif self.vel_y < 0: self.rect.top = p.rect.bottom

    def disparar(self):
        # Creamos una bala en la posición actual del jugador
        bala = Bala('bullet.png', self.rect.right, self.rect.centery, 15, 20, 15)
        balas.add(bala)

class Enemigo(GameSprite):
    def __init__(self, imagen, x, y, ancho, alto, velocidad):
        super().__init__(imagen, x, y, ancho, alto)
        self.velocidad = velocidad
        self.direccion = "izquierda"

    def update(self):
        # Patrullaje simple
        if self.rect.x <= 420:
            self.direccion = "derecha"
        if self.rect.x >= ancho_ventana - 85:
            self.direccion = "izquierda"
        
        if self.direccion == "izquierda":
            self.rect.x -= self.velocidad
        else:
            self.rect.x += self.velocidad

class Bala(GameSprite):
    def __init__(self, imagen, x, y, ancho, alto, velocidad):
        super().__init__(imagen, x, y, ancho, alto)
        self.velocidad = velocidad

    def update(self):
        self.rect.x += self.velocidad
        # Si sale de la pantalla, se elimina para no gastar memoria
        if self.rect.x > ancho_ventana + 10:
            self.kill()

# --- CONFIGURACIÓN ---
ancho_ventana, alto_ventana = 700, 500
window = display.set_mode((ancho_ventana, alto_ventana))
display.set_caption("Laberinto: Modo Combate")
color_fondo = (119, 210, 223)

# Grupos
barreras = sprite.Group()
balas = sprite.Group()
monstruos = sprite.Group()

# Crear Objetos
pared1 = GameSprite('pared2.png', ancho_ventana / 2 - ancho_ventana / 3, alto_ventana / 2, 300, 50)
pared2 = GameSprite('pared1.png', 370, 100, 50, 400)
barreras.add(pared1, pared2)

packman = Player('hero.png', 5, alto_ventana - 80, 80, 80, 0, 0)
meta = GameSprite('pac-1.png', ancho_ventana - 85, alto_ventana - 100, 80, 80)

monstruos.add(Enemigo('cyborg.png', ancho_ventana - 80, 150, 80, 80, 5))
monstruos.add(Enemigo('cyborg.png', ancho_ventana - 80, 230, 80, 80, 5))

# Imágenes de final
img_pierde = image.load('game-over_1.png')
img_gana = image.load('thumb.jpg')

ejecutando, terminado = True, False

# --- BUCLE PRINCIPAL ---
while ejecutando:
    time.delay(50)
    for evento in event.get():
        if evento.type == QUIT:
            ejecutando = False
        elif evento.type == KEYDOWN:
            if evento.key == K_LEFT: packman.vel_x = -5
            elif evento.key == K_RIGHT: packman.vel_x = 5
            elif evento.key == K_UP: packman.vel_y = -5
            elif evento.key == K_DOWN: packman.vel_y = 5
            elif evento.key == K_SPACE: packman.disparar() # DISPARO
        elif evento.type == KEYUP:
            if evento.key in [K_LEFT, K_RIGHT]: packman.vel_x = 0
            if evento.key in [K_UP, K_DOWN]: packman.vel_y = 0

    if not terminado:
        window.fill(color_fondo)
        
        # Actualizaciones
        packman.actualizar()
        balas.update()
        monstruos.update()

        # Colisiones de combate
        # Si una bala toca un monstruo, ambos desaparecen (True, True)
        sprite.groupcollide(monstruos, balas, True, True)
        # Si una bala toca una pared, la bala desaparece (True, False)
        sprite.groupcollide(balas, barreras, True, False)

        # Dibujo
        barreras.draw(window)
        balas.draw(window)
        monstruos.draw(window)
        meta.dibujar()
        packman.dibujar()

        # Colisión Jugador vs Monstruo
        if sprite.spritecollide(packman, monstruos, False):
            terminado = True
            window.fill((255, 255, 255))
            window.blit(transform.scale(img_pierde, (ancho_ventana, alto_ventana)), (0, 0))

        # Colisión Jugador vs Meta
        if sprite.collide_rect(packman, meta):
            terminado = True
            window.fill((255, 255, 255))
            window.blit(transform.scale(img_gana, (ancho_ventana, alto_ventana)), (0, 0))

    display.update()