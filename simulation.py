import pygame
import time
import random
import os
import matplotlib.pyplot as plt
from math import exp

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (50, 150, 250)
BUTTON_HOVER_COLOR = (30, 100, 200)

# Particle class for enzymes and substrates
class Particle:
    def __init__(self, x, y, color, radius, speed_multiplier=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.speed_multiplier = speed_multiplier
        self.dx = random.choice([-2, -1, 1, 2]) * self.speed_multiplier
        self.dy = random.choice([-2, -1, 1, 2]) * self.speed_multiplier

    def move(self):
        self.x = (self.x + self.dx) % 1200  # WIDTH
        self.y = (self.y + self.dy) % 800  # HEIGHT

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Function to save reaction rate graph
def save_reaction_rate_graph(reaction_rates):
    plt.figure(figsize=(8, 6))
    plt.plot(reaction_rates, label="Reaction Rate", color="blue", linewidth=2)
    plt.title("Reaction Rate Over Time")
    plt.xlabel("Time Steps")
    plt.ylabel("Reaction Rate")
    plt.legend()
    plt.grid(True)
    graph_path = "reaction_rate_graph.png"
    plt.savefig(graph_path)
    plt.close()
    return graph_path

# Function to display results after simulation
def display_results(total_products, total_reactions, avg_reaction_rate, reaction_rates, vmax, km, screen):
    graph_path = save_reaction_rate_graph(reaction_rates)
    graph_image = pygame.image.load(graph_path)
    graph_image = pygame.transform.scale(graph_image, (600, 400))

    running = True
    while running:
        screen.fill(WHITE)
        result_font = pygame.font.Font(None, 35)
        result_lines = [
            "Simulation Complete!",
            f"Total Products Formed: {total_products}",
            f"Total Reactions: {total_reactions}",
            f"Average Reaction Rate: {avg_reaction_rate:.2f} reactions/sec",
            f"Vmax (Max Reaction Rate): {vmax:.2f}",
            f"Km (Michaelis Constant): {km:.2f}" if km else "Km: Not Determined",
            "Press ESC to exit or click to return to menu."
        ]

        for i, line in enumerate(result_lines):
            result_surface = result_font.render(line, True, TEXT_COLOR)
            screen.blit(result_surface, (50, 50 + i * 50))

        graph_x = (1200 - 600) // 2
        graph_y = 800 - 450
        screen.blit(graph_image, (graph_x, graph_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        pygame.display.flip()

    os.remove(graph_path)  # Clean up the saved graph image

# Analyze reaction rates to get Vmax and Km
def analyze_reaction_rates(reaction_rates):
    vmax = max(reaction_rates)
    half_vmax = vmax / 2
    km = next((i for i, rate in enumerate(reaction_rates) if rate >= half_vmax), None)
    return vmax, km

# Main simulation function
def run_simulation(params, screen):
    num_enzymes = params["num_enzymes"]
    num_substrates = params["num_substrates"]
    activation_energy = params["activation_energy"]
    temperature = params["temperature"]
    pre_exponential_factor = params["pre_exponential_factor"]
    km = params["km"]
    reaction_radius = params["reaction_radius"]
    simulation_time = params["simulation_time"]

    def michaelis_menten_rate(substrate_concentration, vmax, km):
        return (vmax * substrate_concentration) / (km + substrate_concentration)

    def calculate_rate_constant(ea, temperature, pre_exp_factor):
        R = 8.314  # Gas constant in J/(mol·K)
        ea_joules = ea * 1000  # Convert from kJ/mol to J/mol
        A = pre_exp_factor * 1e7  # Convert slider value to 10⁷ scale
        return A * exp(-ea_joules / (R * temperature))

    # Calculate rate constant and vmax
    k = calculate_rate_constant(activation_energy, temperature, pre_exponential_factor)
    vmax = k * num_enzymes

    enzymes = [Particle(random.randint(0, 1200), random.randint(0, 800), (0, 0, 255), 8) for _ in range(num_enzymes)]
    substrates = [Particle(random.randint(0, 1200), random.randint(0, 800), (0, 255, 0), 6) for _ in range(num_substrates)]
    products = []
    reaction_count = 0
    start_time = time.time()
    reaction_rates = []
    clock = pygame.time.Clock()
    running = True
    paused = False

    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused

        if paused:
            pygame.display.flip()
            clock.tick(10)
            continue

        current_time = time.time() - start_time
        if current_time >= simulation_time:
            running = False
            break

        # Display simulation info
        info_font = pygame.font.Font(None, 28)
        info_lines = [
            f"Time: {int(current_time)}s / {simulation_time}s",
            f"Number of Enzymes: {num_enzymes}",
            f"Number of Substrates Remaining: {len(substrates)}",
            f"Total Products Formed: {len(products)}",
            f"Reactions Count: {reaction_count}"
        ]

        for i, line in enumerate(info_lines):
            info_surface = info_font.render(line, True, TEXT_COLOR)
            screen.blit(info_surface, (10, 10 + i * 30))

        # Move and draw enzymes and substrates
        for enzyme in enzymes:
            enzyme.move()
            enzyme.draw(screen)

        new_substrates = []
        for substrate in substrates:
            substrate.move()
            substrate.draw(screen)
            reacted = False
            for enzyme in enzymes:
                distance = ((enzyme.x - substrate.x) ** 2 + (enzyme.y - substrate.y) ** 2) ** 0.5
                rate = michaelis_menten_rate(len(substrates), vmax, km)
                if distance < reaction_radius and random.random() < rate / vmax:
                    reacted = True
                    products.append(Particle(substrate.x, substrate.y, RED, 4))
                    reaction_count += 1
                    break

            if not reacted:
                new_substrates.append(substrate)
        substrates = new_substrates

        reaction_rates.append(reaction_count / (current_time + 1e-5))
        pygame.display.flip()
        clock.tick(60)

    vmax, km = analyze_reaction_rates(reaction_rates)
    display_results(len(products), reaction_count, sum(reaction_rates) / len(reaction_rates), reaction_rates, vmax, km, screen)
