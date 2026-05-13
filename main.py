import math
import time
import random
global msec    # m seconds
global g    # acceleration

####################################
# 这个文件里的所有代码都是人工手写的，没有使用任何AI生成
#

def generateGauss(center, deviation):
    raw = random.gauss(center, deviation)
    return round(raw, 5)

class Entity:
    def __init__(self, id):
        self.id = id
        self.energy = 100
        self.endpointV = []
        self.radicals = []
        self.omega = []
        self.theta = []
        self.protein = 50
        self.x = 0
        self.y = 50     # 给一个初始高度，至少高于一条腿的高度，否则会卡住吧
        self.v_x = 0
        self.v_y = 0
        self.msec = 0
        self.endpoint1 = [0, 0]
        self.endpoint2 = [0, 0]
        self.endpoint3 = [0, 0]
        for i in range(1, 4):
            # 随机生成三个参数，θ，ω，R，构成三角函数
            self.omega.append(round(random.uniform(0, 10 * math.pi), 5))
            self.theta.append(round(random.uniform(0, 2 * math.pi), 5))
            fit = False
            # 三条腿腿总长度有限制
            while not fit:
                radical = round(random.uniform(0, 10), 1)
                if (self.protein - radical) >= 0:
                    fit = True
                    self.radicals.append(radical)
        ## 更新腿部endpoint位置
        # 首先计算三个函数在t = 0s时的值
        # TODO: 通过y = R * sin(ωt + θ), x = R * cos(ωt + θ);
        # lowest = min(y)
        # 计算出最低endpoint的(x,y)坐标，如果两者都高于(0, 50)，那么说明可怜的entity肚子朝下。如果此时撞击，应该按照vy反向、vx不变。
        #low_x, low_y = self.get_lowest()
        
        
        
    def reset(self):
        self.x = 0
        self.y = 30
        self.v_x = 0
        self.v_y = 0
        self.energy = 2000
        self.msec = 0

    def regen_entity(self, center_list, deviation, attr_name):
        target_list = getattr(self, attr_name)
        for i in range(0, 3):
            target_list[i] = generateGauss(center_list[i], deviation)
            # ensure positive
            while target_list[i] < 0:
                target_list[i] = generateGauss(center_list[i], deviation)

    def update_entity(self):

        ## UPDATE POSITION
        self.x += self.v_x * 0.01
        self.y += self.v_y * 0.01        # 0.01秒一个单位
        # TODO: update endpoint positions
        self.endpoint1[0] = self.x + self.radicals[0] * math.sin(self.omega[0] * self.msec * 0.01 + self.theta[0]) 
        self.endpoint1[1] = self.y + self.radicals[0] * math.cos(self.omega[0] * self.msec * 0.01 + self.theta[0])

        self.endpoint2[0] = self.x + self.radicals[1] * math.sin(self.omega[1] * self.msec * 0.01 + self.theta[1]) 
        self.endpoint2[1] = self.y + self.radicals[1] * math.cos(self.omega[1] * self.msec * 0.01 + self.theta[1])

        self.endpoint3[0] = self.x + self.radicals[2] * math.sin(self.omega[2] * self.msec * 0.01 + self.theta[2]) 
        self.endpoint3[1] = self.y + self.radicals[2] * math.cos(self.omega[2] * self.msec * 0.01 + self.theta[2])
        

        # TODO: update vy based on gravitational acceleration
        low_x, low_y, l_omega, r = self.get_lowest()
        if low_y > 0:
            self.v_y -= g * 0.01

        ## DETECT BUMP
        if low_y <= 0:
            self.handle_bump(low_x, low_y, l_omega, r)

        ## UPDATE energy
        for i in range(0, 3):
            self.energy -= self.radicals[i] * self.omega[i] * 0.01

        self.msec += 0.01
        #time.sleep(0.01)        

    def handle_bump(self, low_x, low_y, omega, r):
        # body takes the lowest position:
        if low_x == self.x and low_y == self.y:
            self.v_y = - self.v_y
            return
        # an endpoint takes the lowest:
        if r == 0:
            return
        end_v = r * omega

        #self.v_x += 0.05 * abs((end_v * (self.y - low_y)/r))
        #self.v_y += 0.05 * abs((end_v * (self.x - low_x)/ r ))
        # 更温和的碰撞响应
        impulse = 3.0 + abs(math.sin(omega * self.msec)) * 2.0
        self.v_y = max(self.v_y, impulse)          # 向上弹起
        self.v_x += (self.x - low_x) * 0.8         # 简单水平推力
        
    def get_lowest(self):
        x = 0
        y = 0
        l_omega = -1
        r = -1
        y = min(self.endpoint1[1], self.endpoint2[1], self.endpoint3[1], self.y)
        if y == self.endpoint1[1]:
            x = self.endpoint1[0]
            l_omega = self.omega[0]
            r = self.radicals[0]
        elif y == self.endpoint2[1]:
            x = self.endpoint2[0]
            l_omega = self.omega[1]
            r = self.radicals[1]
        elif y == self.endpoint3[1]:
            x = self.endpoint3[0]
            r = self.radicals[2]
            l_omega = self.omega[2]
        else:
            x = self.x
            y = self.y

        return (x, y, l_omega, r)
    
    def ent_main(self):
        while self.energy >= 0:
            self.update_entity()
        self.msec = 0
        return (self.id, self.x)

def main():
    ent_list = []
    ## generate some entities
    for i in range(0, 1000):
        ent = Entity(i)
        ent_list.append(ent)

    # Evolution loop: 1000 generations
    for gen in range(1000):
        far_x = 0
        far_id = -1
        print(f"Generation {gen}:")
        
        # Run simulation for all entities
        for i in range(0, 1000):
            ent_list[i].reset()
            id, x = ent_list[i].ent_main()
            if x > far_x:
                far_x = x
                far_id = id
        
        print(f"  Farthest: id={far_id}, x={far_x}")
        print(f"  omega={ent_list[far_id].omega}")
        print(f"  theta={ent_list[far_id].theta}")
        print(f"  radical={ent_list[far_id].radicals}")

        # Regenerate all entities based on the farest one
        for i in range(0, 1000):
            ent_list[i].regen_entity(ent_list[far_id].omega, 0.5, 'omega')
            ent_list[i].regen_entity(ent_list[far_id].theta, 0.5, 'theta')
            ent_list[i].regen_entity(ent_list[far_id].radicals, 0.5, 'radicals')
g = 9.98
msec = 0

if __name__ == '__main__':
    main()
