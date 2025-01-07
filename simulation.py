import pygame
import random
import time
import os
import math
import matplotlib.pyplot as plt

# Particle class for enzymes and substrates
class Particle:
    def __init__(self, x, y, molecule_name, diffusion_coefficient, radius, color):
        self.x = x
        self.y = y
        self.molecule_name = molecule_name  # Name of molecule (e.g., "Hexokinase", "Glucose")
        self.diffusion_coefficient = diffusion_coefficient  # μm²/s
        self.radius = radius  # Molecular size (in pixels)
        self.color = color
        self.dx = random.uniform(-1, 1) * math.sqrt(diffusion_coefficient)
        self.dy = random.uniform(-1, 1) * math.sqrt(diffusion_coefficient)

    def move(self):
        self.x = (self.x + self.dx) % 1200  # Wrap around screen width
        self.y = (self.y + self.dy) % 800  # Wrap around screen height

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


# Enzyme presets
enzyme_presets = {
    "Hexokinase": {
        "diffusion_coefficient": 300,  # μm²/s
        "radius": 10,  # nm converted to pixels
        "km": 100,  # μM
        "kcat": 100,  # Turnover rate (substrates/sec)
        "color": (0, 0, 255),
        "substrate": "Glucose"
    },
    "Catalase": {
        "diffusion_coefficient": 160,  # μm²/s
        "radius": 12,  # nm
        "km": 10,  # μM
        "kcat": 40000,  # Turnover rate (very high for catalase)
        "color": (255, 0, 0),
        "substrate": "Hydrogen Peroxide"
    },
    "DNA Polymerase": {
        "diffusion_coefficient": 20,  # μm²/s (slower because it's large)
        "radius": 15,  # nm
        "km": 0.1,  # μM (high affinity)
        "kcat": 1000,  # Turnover rate
        "color": (0, 255, 0),
        "substrate": "Nucleotides"
    }
}

# Calculate the reaction rate constant (Arrhenius equation)
def calculate_rate_constant(ea, temperature, pre_exp_factor):
    ea_joules = ea * 1000  # Convert from kJ/mol to J/mol
    R = 8.314  # J/(mol·K) (Gas constant)
    A = pre_exp_factor * 1e7  # Convert pre-exponential factor to scale (x 10⁷)
    return A * math.exp(-ea_joules / (R * temperature))


# Enzyme selection screen
def choose_enzyme(screen):
    pygame.font.init()
    font = pygame.font.Font(None, 40)
    running = True
    selected_enzyme = None

    while running:
        screen.fill((255, 255, 255))
        title_surface = font.render("Choose an Enzyme to Simulate:", True, (0, 0, 0))
        screen.blit(title_surface, ((1200 - title_surface.get_width()) // 2, 100))

        # Draw enzyme options
        enzyme_buttons = {}
        y_offset = 200
        for enzyme_name, attributes in enzyme_presets.items():
            button_rect = pygame.Rect(450, y_offset, 300, 50)
            enzyme_buttons[enzyme_name] = button_rect
            pygame.draw.rect(screen, attributes["color"], button_rect)
            text_surface = font.render(enzyme_name, True, (255, 255, 255))
            screen.blit(text_surface, (button_rect.x + 50, button_rect.y + 10))
            y_offset += 100

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for enzyme_name, button_rect in enzyme_buttons.items():
                    if button_rect.collidepoint(event.pos):
                        selected_enzyme = enzyme_name
                        running = False

        pygame.display.flip()

    return selected_enzyme


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


def display_results(total_products, total_reactions, avg_reaction_rate, reaction_rates, vmax, km, screen):
    graph_path = save_reaction_rate_graph(reaction_rates)
    graph_image = pygame.image.load(graph_path)
    graph_image = pygame.transform.scale(graph_image, (600, 400))

    running = True
    while running:
        screen.fill((255, 255, 255))
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
            result_surface = result_font.render(line, True, (0, 0, 0))
            screen.blit(result_surface, (50, 50 + i * 50))

        graph_x = (1200 - 600) // 2
        graph_y = 800 - 450
        screen.blit(graph_image, (graph_x, graph_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        pygame.display.flip()

    os.remove(graph_path)  # Clean up the saved graph image


def analyze_reaction_rates(reaction_rates):
    vmax = max(reaction_rates) if reaction_rates else 0
    half_vmax = vmax / 2 if vmax > 0 else 0
    km = next((i for i, rate in enumerate(reaction_rates) if rate >= half_vmax), None)
    return vmax, km


def run_simulation(params, screen):
    # Ask the user to choose an enzyme
    selected_enzyme = choose_enzyme(screen)
    enzyme_params = enzyme_presets[selected_enzyme]

    # Set enzyme parameters
    diffusion_coefficient_enzyme = enzyme_params["diffusion_coefficient"]
    radius_enzyme = enzyme_params["radius"]
    km = enzyme_params["km"]
    kcat = enzyme_params["kcat"]
    enzyme_color = enzyme_params["color"]
    substrate_name = enzyme_params["substrate"]

    num_enzymes = params["num_enzymes"]
    num_substrates = params["num_substrates"]
    activation_energy = params["activation_energy"]
    temperature = params["temperature"]
    pre_exponential_factor = params["pre_exponential_factor"]

    # Calculate rate constant using Arrhenius equation
    k = calculate_rate_constant(activation_energy, temperature, pre_exponential_factor)
    vmax = k * num_enzymes  # Maximum reaction rate

    diffusion_coefficient_substrate = 300  # Substrate diffusion rate (μm²/s)
    radius_substrate = 5  # Substrate size in pixels
    reaction_radius = params["reaction_radius"]
    simulation_time = params["simulation_time"]

    # Create enzyme and substrate particles
    enzymes = [Particle(random.randint(0, 1200), random.randint(0, 800), selected_enzyme, diffusion_coefficient_enzyme, radius_enzyme, enzyme_color) for _ in range(num_enzymes)]
    substrates = [Particle(random.randint(0, 1200), random.randint(0, 800), substrate_name, diffusion_coefficient_substrate, radius_substrate, (0, 255, 0)) for _ in range(num_substrates)]

    products = []  # List to store orange products
    reaction_count = 0
    start_time = time.time()
    reaction_rates = []
    clock = pygame.time.Clock()
    running = True
    paused = False

    while running:
        screen.fill((255, 255, 255))
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

        # Calculate binding probability using the correct formula
        binding_probability = len(substrates) / (km + len(substrates))  # Correct Michaelis-Menten probability
        binding_percentage = binding_probability * 100  # Convert to percentage for display


        # Simulation information
        info_font = pygame.font.Font(None, 28)
        info_lines = [
            f"Time: {int(current_time)}s / {simulation_time}s",
            f"Number of Enzymes: {num_enzymes}",
            f"Number of Substrates Remaining: {len(substrates)}",
            f"Total Products Formed: {len(products)}",
            f"Reactions Count: {reaction_count}",
            f"Binding Probability: {binding_percentage:.2f}%"
        ]

        for i, line in enumerate(info_lines):
            info_surface = info_font.render(line, True, (0, 0, 0))
            screen.blit(info_surface, (10, 10 + i * 30))

        # Enzyme and substrate motion and interaction
        for enzyme in enzymes:
            enzyme.move()
            enzyme.draw(screen)

        new_substrates = []
        for substrate in substrates:
            substrate.move()
            substrate.draw(screen)

            reacted = False
            for enzyme in enzymes:
                distance = math.sqrt((enzyme.x - substrate.x) ** 2 + (enzyme.y - substrate.y) ** 2)
                rate = (vmax * len(substrates)) / (km + len(substrates))  # Michaelis-Menten rate

                # Create orange product particle when a reaction happens
                if distance <= reaction_radius and random.random() < rate / vmax:
                    reacted = True
                    # Add orange product dot to the list
                    products.append(Particle(substrate.x, substrate.y, "Product", diffusion_coefficient_substrate, radius_substrate, (255, 165, 0)))
                    reaction_count += 1
                    break

            if not reacted:
                new_substrates.append(substrate)
        substrates = new_substrates

        # Draw orange product particles
        for product in products:
            product.draw(screen)

        reaction_rates.append(reaction_count / (current_time + 1e-5))
        pygame.display.flip()
        clock.tick(60)

    vmax, km = analyze_reaction_rates(reaction_rates)
    display_results(len(products), reaction_count, sum(reaction_rates) / len(reaction_rates), reaction_rates, vmax, km, screen)
