import math

def model(agent, enemy, window_size):
    enemy.dx = enemy.speed * math.cos(math.radians(enemy.direction))
    enemy.dy = enemy.speed * math.sin(math.radians(enemy.direction))
    enemy.endx = enemy.x
    enemy.endy = enemy.y
    
    while enemy.endx < 0 or enemy.endx > window_size or enemy.endy < 0 or enemy.endy > window_size:
        enemy.endx += enemy.dx
        enemy.endy += enemy.dy
        
    dist_from_enemy_path = abs((enemy.endy - enemy.y) * agent.x - (enemy.endx - enemy.x) * agent.y + enemy.endx *
                              enemy.y - enemy.endy * enemy.x) / math.sqrt((enemy.endy - enemy.y)**2 + (enemy.endx - enemy.x)**2)
    
    if dist_from_enemy_path < enemy.radius + agent.radius:
        # agent.x += agent.speed * math.sin(math.radians(enemy.direction))
        # agent.y += agent.speed * math.cos(math.radians(enemy.direction))
        return (math.sin(math.radians(enemy.direction)), math.cos(math.radians(enemy.direction)))
    else:
        return (0, 0)
        
