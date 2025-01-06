import pygame

# Colors for the UI
WHITE = (255, 255, 255)
BUTTON_COLOR = (50, 150, 250)
BUTTON_HOVER_COLOR = (30, 100, 200)
TEXT_COLOR = (0, 0, 0)
HEADING_COLOR = (20, 20, 20)
pygame.font.init()
# Font
font = pygame.font.Font(None, 30)

# Slider class for parameters
class Slider:
    def __init__(self, x, y, min_val, max_val, initial, label):
        self.x = x
        self.y = y
        self.width = 200
        self.height = 10
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.label = label
        self.slider_x = x + int((initial - min_val) / (max_val - min_val) * self.width)

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), (self.x, self.y, self.width, self.height))
        pygame.draw.circle(surface, (0, 0, 0), (self.slider_x, self.y + self.height // 2), 8)
        label_surface = font.render(f"{self.label}: {self.value}", True, TEXT_COLOR)
        surface.blit(label_surface, (self.x, self.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            if self.x <= mouse_x <= self.x + self.width and self.y - 10 <= mouse_y <= self.y + self.height + 10:
                self.slider_x = mouse_x
                self.value = int(self.min_val + (mouse_x - self.x) / self.width * (self.max_val - self.min_val))

# Function to display parameter adjustment screen
def adjust_parameters(screen):
    # Initialize sliders
    num_enzymes_slider = Slider(50, 100, 10, 50, 20, "Number of Enzymes")
    num_substrates_slider = Slider(50, 200, 10, 100, 50, "Number of Substrates")
    activation_energy_slider = Slider(50, 300, 40, 100, 60, "Activation Energy (kJ/mol)")
    temperature_slider = Slider(50, 400, 273, 373, 298, "Temperature (K)")
    pre_exponential_factor_slider = Slider(50, 500, 1, 10, 7, "Pre-exponential Factor (x 10⁷)")
    km_slider = Slider(50, 600, 10, 100, 30, "Km (Michaelis Constant)")
    simulation_time_slider = Slider(50, 700, 30, 300, 90, "Simulation Time (seconds)")

    # Start button
    start_button = pygame.Rect(500, 750, 200, 40)

    sliders = [
        num_enzymes_slider,
        num_substrates_slider,
        activation_energy_slider,
        temperature_slider,
        pre_exponential_factor_slider,
        km_slider,
        simulation_time_slider
    ]

    running = True
    while running:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    return {
                        "num_enzymes": num_enzymes_slider.value,
                        "num_substrates": num_substrates_slider.value,
                        "activation_energy": activation_energy_slider.value,
                        "temperature": temperature_slider.value,
                        "pre_exponential_factor": pre_exponential_factor_slider.value,
                        "km": km_slider.value,
                        "reaction_radius": 10,
                        "simulation_time": simulation_time_slider.value,
                    }

            for slider in sliders:
                slider.handle_event(event)

        # Draw heading
        heading_font = pygame.font.Font(None, 50)
        heading_surface = heading_font.render("Enzyme-Substrate Interaction Settings", True, HEADING_COLOR)
        screen.blit(heading_surface, ((1200 - heading_surface.get_width()) // 2, 20))

        # Draw sliders
        for slider in sliders:
            slider.draw(screen)

        # Draw start button
        if start_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, start_button)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, start_button)
        start_label = font.render("Start Simulation", True, WHITE)
        screen.blit(start_label, (start_button.x + (start_button.width - start_label.get_width()) // 2, start_button.y + 10))

        pygame.display.flip()
