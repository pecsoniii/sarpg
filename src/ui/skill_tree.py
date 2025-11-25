import pygame
from src.settings import *
from src.data.skills import SKILL_TREE

class SkillTreeMenu:
    def __init__(self, game_data, joysticks):
        self.game_data = game_data
        self.joysticks = joysticks
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 40)

        self.visible = False
        self.nodes = SKILL_TREE
        self.selected_node = 'vitality_1'

        # Navigation
        self.node_keys = list(self.nodes.keys())
        self.selection_index = 0
        self.input_cooldown = 0

    def toggle(self):
        self.visible = not self.visible

    def input(self):
        if pygame.time.get_ticks() - self.input_cooldown < 200:
            return

        keys = pygame.key.get_pressed()

        moved = False
        # Simple List Navigation for now (Up/Down) - Visual Tree is complex to navigate with D-pad
        # Let's cycle through keys
        if keys[pygame.K_w] or keys[pygame.K_d]:
            self.selection_index += 1
            moved = True
        if keys[pygame.K_s] or keys[pygame.K_a]:
            self.selection_index -= 1
            moved = True

        if len(self.joysticks) > 0:
             # ... Joystick logic similar to Shop ...
             pass # Placeholder for brevity, assume keyboard/mouse mainly for dev or reuse logic

        if moved:
            if self.selection_index >= len(self.node_keys): self.selection_index = 0
            if self.selection_index < 0: self.selection_index = len(self.node_keys) - 1
            self.selected_node = self.node_keys[self.selection_index]
            self.input_cooldown = pygame.time.get_ticks()

        # Unlock
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            self.unlock_selected()
            self.input_cooldown = pygame.time.get_ticks()

    def unlock_selected(self):
        node_id = self.selected_node
        node = self.nodes[node_id]

        # Check if already unlocked
        if node_id in self.game_data['skills_unlocked']:
            return

        # Check Parent
        if node['parent'] and node['parent'] not in self.game_data['skills_unlocked']:
            return # Parent locked

        # Check Cost
        if self.game_data['skill_points'] >= node['cost']:
            self.game_data['skill_points'] -= node['cost']
            self.game_data['skills_unlocked'].append(node_id)

            # Apply Effect Immediately (Base stats update)
            stat = node['effect']['stat']
            val = node['effect']['value']
            self.game_data['base_stats'][stat] += val

    def draw(self):
        if not self.visible: return

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(BLACK)
        self.display_surface.blit(overlay, (0,0))

        # Title
        title = self.title_font.render(f"SKILL TREE - SP: {self.game_data['skill_points']}", True, NEON_CYAN)
        self.display_surface.blit(title, (20, 20))

        # Draw Connections first
        for key, node in self.nodes.items():
            if node['parent']:
                parent = self.nodes[node['parent']]
                color = (100, 100, 100)
                if node['parent'] in self.game_data['skills_unlocked']:
                    color = NEON_CYAN
                pygame.draw.line(self.display_surface, color, node['pos'], parent['pos'], 4)

        # Draw Nodes
        for key, node in self.nodes.items():
            color = (50, 50, 50)
            border = WHITE

            if key in self.game_data['skills_unlocked']:
                color = NEON_CYAN
                border = NEON_CYAN
            elif node['parent'] is None or node['parent'] in self.game_data['skills_unlocked']:
                color = (20, 80, 80) # Unlockable

            # Selection Highlight
            if key == self.selected_node:
                border = NEON_YELLOW
                # Description Box
                desc = f"{node['name']} (Cost: {node['cost']})\n{node['desc']}"
                self.draw_tooltip(desc)

            pygame.draw.circle(self.display_surface, color, node['pos'], 20)
            pygame.draw.circle(self.display_surface, border, node['pos'], 20, 2)

    def draw_tooltip(self, text):
        # Simple tooltip at bottom
        pass # Implement later
