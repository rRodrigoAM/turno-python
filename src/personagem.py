import random
from math import ceil, floor

class Personagem:
    ATTACK_COST = 12
    FIREBALL_COST = 16
    HEAL_COST = 13
    DEFEND_STAMINA = 24
    DEFEND_MANA = 10
    GUARD_REDUCTION = 0.4

    def __init__(
        self,
        name,
        hp,
        stamina,
        mana,
        img,
        attack_damage=(14, 20),
        damage_taken_multipliers=None,
        is_poisoned=False,
        damage_dealt_multiplier=1.0,
        attack_cost=None,
        is_boss=False,
    ):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_stamina = stamina
        self.stamina = stamina
        self.max_mana = mana
        self.mana = mana
        self.img = img
        self.attack_damage = attack_damage
        self.attack_cost = self.ATTACK_COST if attack_cost is None else attack_cost
        self.damage_taken_multipliers = dict(damage_taken_multipliers or {})
        self.is_poisoned = is_poisoned
        self.is_boss = is_boss
        self.damage_dealt_multiplier = damage_dealt_multiplier
        self.alive = True
        self.is_guarding = False

    def take_damage(self, damage, damage_type="physical"):
        multiplier = self.damage_taken_multipliers.get(damage_type, 1.0)
        damage = max(1, floor(damage * multiplier + 0.5))
        if self.is_guarding:
            damage = max(1, ceil(damage * (1 - self.GUARD_REDUCTION)))
            self.is_guarding = False

        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return damage

    def scale_outgoing_damage(self, damage):
        return max(1, floor(damage * self.damage_dealt_multiplier + 0.5))

    def attack(self, target):
        if self.stamina < self.attack_cost:
            return f"{self.name} está sem stamina para atacar.", False

        raw_damage = self.scale_outgoing_damage(random.randint(*self.attack_damage))
        was_guarding = target.is_guarding
        damage = target.take_damage(raw_damage, damage_type="physical")
        self.stamina -= self.attack_cost
        notes = []
        if target.damage_taken_multipliers.get("physical", 1.0) > 1.0:
            notes.append("fraqueza explorada")
        if was_guarding:
            notes.append("bloqueio parcial")
        suffix = f" ({'; '.join(notes)})" if notes else ""
        return f"{self.name} causou {damage} de dano físico em {target.name}{suffix}.", True

    def cast_fireball(self, target):
        if self.mana < self.FIREBALL_COST:
            return f"{self.name} não tem mana suficiente para a Bola de Fogo.", False

        raw_damage = self.scale_outgoing_damage(random.randint(26, 34))
        was_guarding = target.is_guarding
        damage = target.take_damage(raw_damage, damage_type="magic")
        self.mana -= self.FIREBALL_COST
        notes = []
        if target.damage_taken_multipliers.get("magic", 1.0) > 1.0:
            notes.append("fraqueza mágica explorada")
        if was_guarding:
            notes.append("bloqueio parcial")
        suffix = f" ({'; '.join(notes)})" if notes else ""
        return f"{self.name} lançou Bola de Fogo: {damage} de dano em {target.name}{suffix}.", True

    def heal(self):
        if self.hp >= self.max_hp:
            return f"{self.name} já está com o HP cheio.", False
        if self.mana < self.HEAL_COST:
            return f"{self.name} não tem mana suficiente para se curar.", False

        healed = random.randint(26, 34)
        actual_healing = min(healed, self.max_hp - self.hp)
        self.hp += actual_healing
        self.mana -= self.HEAL_COST
        return f"{self.name} recuperou {actual_healing} de HP.", True

    def defend(self):
        stamina_gained = min(self.DEFEND_STAMINA, self.max_stamina - self.stamina)
        mana_gained = min(self.DEFEND_MANA, self.max_mana - self.mana)
        self.stamina += stamina_gained
        self.mana += mana_gained
        self.is_guarding = True
        return (
            f"{self.name}: guarda (-40% no próximo golpe, "
            f"+{stamina_gained} ST, +{mana_gained} MP).",
            True,
        )
