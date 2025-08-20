import random

class Personagem:
    def __init__(self, name, hp, stamina, mana, img):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_stamina = stamina
        self.stamina = stamina
        self.max_mana = mana
        self.mana = mana
        self.img = img
        self.alive = True

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def attack(self, target):
        cost = 10
        if self.stamina >= cost:
            damage = random.randint(10, 20)
            target.take_damage(damage)
            self.stamina -= cost
            return f"{self.name} atacou {target.name} causando {damage} de dano físico!"
        return f"{self.name} está exausto e não pode atacar!"

    def cast_fireball(self, target):
        cost = 15
        if self.mana >= cost:
            damage = random.randint(20, 30)
            target.take_damage(damage)
            self.mana -= cost
            return f"{self.name} lançou Bola de Fogo em {target.name} causando {damage} de dano mágico!"
        return f"{self.name} não tem mana suficiente!"

    def heal(self):
        cost = 10
        if self.mana >= cost:
            healed = random.randint(15, 25)
            self.hp = min(self.max_hp, self.hp + healed)
            self.mana -= cost
            return f"{self.name} se curou e recuperou {healed} de HP!"
        return f"{self.name} não tem mana suficiente!"

    def defend(self):
        self.stamina = min(self.max_stamina, self.stamina + 15)
        return f"{self.name} se defendeu e recuperou 15 de stamina!"
