import pygame
from ui import adjust_parameters  # Import UI-related functions from ui.py
from simulation import run_simulation  # Import simulation functions from simulation.py

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enzyme-Substrate Interaction Simulation")

# Main function
def main():
    # Display the parameter adjustment screen and get parameters
    params = adjust_parameters(screen)
    # Run the simulation with the collected parameters
    run_simulation(params, screen)

# Program entry point
if __name__ == "__main__":
    main()
