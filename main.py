import random
import os
import math
import string

# Constants
AREA_SIZE = 5  # 5x5 grid of areas
SECTOR_SIZE = 8  # Each area is a 5x5 grid of sectors
ENTERPRISE = "E"
ENEMY_SHIP = "K"
EMPTY_SPACE = "."

# Game data
current_area = [0, 0]  # Start position in the 5x5 area grid
current_sector = [0, 0]  # Start position in the 5x5 sector grid
energy = 100
torpedoes = 25  # Start with 25 torpedoes
photons = 100  # Start with 100 photons
user_action_count = 0  # Track number of actions to trigger enemy counterattacks
remaining_enemies = 0  # Track how many enemies are still alive

# Each area has its own grid of sectors
areas = [[[[EMPTY_SPACE for _ in range(SECTOR_SIZE)] for _ in range(SECTOR_SIZE)] for _ in range(AREA_SIZE)] for _ in range(AREA_SIZE)]
enemies_in_areas = {}

# Place the Enterprise in the current sector
def update_enterprise_position():
    grid = areas[current_area[0]][current_area[1]]
    for row in range(SECTOR_SIZE):
        for col in range(SECTOR_SIZE):
            if grid[row][col] == ENTERPRISE:
                grid[row][col] = EMPTY_SPACE  # Clear previous position
    grid[current_sector[0]][current_sector[1]] = ENTERPRISE

# Create enemies for each sector in every area
def populate_areas():
    global areas, enemies_in_areas, remaining_enemies
    for i in range(AREA_SIZE):
        for j in range(AREA_SIZE):
            enemies_in_areas[(i, j)] = []
            num_enemies = random.randint(2, 4)  # Each sector has between 2 and 4 enemies
            remaining_enemies += num_enemies
            for _ in range(num_enemies):
                enemy_pos = [random.randint(0, SECTOR_SIZE-1), random.randint(0, SECTOR_SIZE-1)]
                areas[i][j][enemy_pos[0]][enemy_pos[1]] = ENEMY_SHIP
                enemies_in_areas[(i, j)].append(enemy_pos)

# Display the grid of the current sector using letters for columns
def display_sector_grid():
    os.system('clear')  # For Windows, use 'cls'
    grid = areas[current_area[0]][current_area[1]]
    update_enterprise_position()
    print(f"Area: {current_area}, Sector: {current_sector}")
    print(f"Energy: {energy} | Torpedoes: {torpedoes} | Photons: {photons}")
    print(f"Remaining enemies: {remaining_enemies}")
    
    # Use letters for the column labels
    col_labels = list(string.ascii_uppercase[:SECTOR_SIZE])
    print("   " + " ".join(col_labels))  # Column labels
    
    for idx, row in enumerate(grid):
        row_label = f"{idx}"  # Row labels (numbers)
        print(f"{row_label} " + " ".join(row))  # Row labels with grid data
    print()

# Short-range radar displaying adjacent sectors
def radar():
    print("\n--- Short-Range Radar (adjacent sectors) ---")
    adjacent_sectors = []
    for delta_row in [-1, 0, 1]:
        for delta_col in [-1, 0, 1]:
            if delta_row == 0 and delta_col == 0:
                continue  # Skip the current sector
            adj_row = (current_area[0] + delta_row) % AREA_SIZE
            adj_col = (current_area[1] + delta_col) % AREA_SIZE
            num_enemies = len(enemies_in_areas[(adj_row, adj_col)])
            adjacent_sectors.append(((adj_row, adj_col), num_enemies))
    
    for sector, enemies in adjacent_sectors:
        print(f"Area {sector}: {enemies} enemies detected")

    input("\nPress Enter to continue...")

# Long-range sensor to display a matrix of all areas with the number of enemies, marking the current sector with an asterisk (*)
def long_range_sensor():
    print("\n--- Long-Range Sensor Scan (all areas) ---")
    print("The number of enemies in each area is displayed, and the current area is marked with *.\n")
    
    # Iterate through each area and display the number of enemies
    for i in range(AREA_SIZE):
        row_display = []
        for j in range(AREA_SIZE):
            if [i, j] == current_area:
                row_display.append(f"*{len(enemies_in_areas[(i, j)])}")
            else:
                row_display.append(f" {len(enemies_in_areas[(i, j)])}")
        print(" | ".join(row_display))
    
    input("\nPress Enter to continue...")

# Move the Enterprise within the sector
def move_in_sector(direction):
    global energy, user_action_count
    if energy <= 0:
        print("You are out of energy!")
        return
    new_pos = current_sector.copy()
    
    if direction == "w" and current_sector[1] > 0:
        new_pos[1] -= 1
    elif direction == "s" and current_sector[0] < SECTOR_SIZE - 1:
        new_pos[0] += 1
    elif direction == "a" and current_sector[1] > 0:
        new_pos[1] -= 1
    elif direction == "d" and current_sector[1] < SECTOR_SIZE - 1:
        new_pos[1] += 1
    else:
        print("Invalid move!")
        return
    
    current_sector[0], current_sector[1] = new_pos
    recharge_energy(percentage=5)  # Recharging energy after each movement
    user_action_count += 1
    check_enemy_counterattack()

# Handle crossing area boundaries
def handle_boundary_crossing():
    global current_area, current_sector
    
    if current_sector[0] < 0:
        current_sector[0] = SECTOR_SIZE - 1
        current_area[0] = (current_area[0] - 1) % AREA_SIZE
    elif current_sector[0] >= SECTOR_SIZE:
        current_sector[0] = 0
        current_area[0] = (current_area[0] + 1) % AREA_SIZE
    
    if current_sector[1] < 0:
        current_sector[1] = SECTOR_SIZE - 1
        current_area[1] = (current_area[1] - 1) % AREA_SIZE
    elif current_sector[1] >= SECTOR_SIZE:
        current_sector[1] = 0
        current_area[1] = (current_area[1] + 1) % AREA_SIZE

# Warp movement across multiple areas based on power (1-10) and angle (0-360 degrees)
def warp_to_area():
    global energy, user_action_count
    if energy < 20:
        print("Not enough energy for warp speed!")
        return

    print("Warp directions (using angles):")
    print("90°: North (up), 180°: East (right), 270°: South (down), 360°: West (left)")

    angle = float(input("Enter warp direction (0-360 degrees): "))
    power = int(input("Enter warp power (1-10): "))
    if power < 1 or power > 10:
        print("Invalid warp power! Choose a value between 1 and 10.")
        return

    radian = math.radians(angle)

    # Calculate warp direction based on angle
    direction_x = math.cos(radian)
    direction_y = -math.sin(radian)  # Inverted y-axis because grid goes downwards

    warp_distance = power  # The warp distance is determined by the power level
    pos = current_sector.copy()

    # Move according to warp distance
    for _ in range(warp_distance):
        pos[0] += int(round(direction_y))
        pos[1] += int(round(direction_x))

        # Handle boundary crossing between sectors and areas
        if pos[0] < 0 or pos[0] >= SECTOR_SIZE or pos[1] < 0 or pos[1] >= SECTOR_SIZE:
            current_sector[0], current_sector[1] = pos[0], pos[1]
            handle_boundary_crossing()
            break
        else:
            current_sector[0], current_sector[1] = pos[0], pos[1]

    # If power is high enough (8-10), move across areas
    if power >= 8:
        handle_boundary_crossing()

    # Energy cost depends on warp power (higher power, more energy used)
    energy -= power * 2  # Deduct energy based on power level (2 energy per power level)
    
    if power >= 8:
        recharge_energy(percentage=15)  # Recharge 15% energy when moving to another area
    else:
        recharge_energy(percentage=5)  # Recharge 5% energy if within the same area

    user_action_count += 1
    print(f"Warped with power {power} to position ({current_sector[0]}, {current_sector[1]}) in area ({current_area[0]}, {current_area[1]})")
    input("\nPress Enter to continue...")
    check_enemy_counterattack()

# Fire torpedoes at specific coordinates (display trajectory)
def fire_torpedo():
    global torpedoes, energy, user_action_count, remaining_enemies
    if torpedoes <= 0:
        print("Out of torpedoes!")
        return False
    if energy < 15:
        print("Not enough energy to fire torpedoes!")
        return False

    # Energy cost is 5% of current energy
    torpedo_energy_cost = max(1, int(energy * 0.05))

    target_row = int(input(f"Enter target row (0-{SECTOR_SIZE-1}): "))
    target_col = input(f"Enter target column (A-{string.ascii_uppercase[SECTOR_SIZE-1]}): ").upper()
    target_col = string.ascii_uppercase.index(target_col)

    print("\nTorpedo trajectory:")
    current_pos = current_sector.copy()

    # Simulate the torpedo moving towards the target row and column
    while current_pos != [target_row, target_col]:
        if current_pos[0] < target_row:
            current_pos[0] += 1
        elif current_pos[0] > target_row:
            current_pos[0] -= 1

        if current_pos[1] < target_col:
            current_pos[1] += 1
        elif current_pos[1] > target_col:
            current_pos[1] -= 1

        print(f"Torpedo moving to ({current_pos[0]}, {string.ascii_uppercase[current_pos[1]]})")

        # Check if the torpedo hits an enemy
        if current_pos in enemies_in_areas[tuple(current_area)]:
            enemies_in_areas[tuple(current_area)].remove(current_pos)
            areas[current_area[0]][current_area[1]][current_pos[0]][current_pos[1]] = EMPTY_SPACE
            remaining_enemies -= 1
            print(f"Torpedo hit an enemy at {current_pos}!")
            break
    else:
        print("Torpedo missed!")

    torpedoes -= 1
    energy -= torpedo_energy_cost
    input("\nPress Enter to continue...")
    user_action_count += 1
    check_enemy_counterattack()

# Fire photons based on any angle (0-360), showing trajectory
def fire_photon():
    global photons, energy, user_action_count, remaining_enemies
    if photons <= 0:
        print("Out of photons!")
        return False
    if energy < 2:
        print("Not enough energy to fire photons!")
        return False

    print("Photon firing directions (using angles):")
    print("90°: North (up), 180°: East (right), 270°: South (down), 360°: West (left)")

    angle = float(input("Enter angle to fire photons (0-360): "))
    radian = math.radians(angle)

    # Calculate direction vector based on angle
    direction_x = round(math.cos(radian))  # Column movement (East-West)
    direction_y = -round(math.sin(radian))  # Row movement (North-South, inverted Y-axis)

    max_photon_range = 3  # Maximum photon range
    pos = current_sector.copy()  # Start photon from the Enterprise's position
    
    print("\nPhoton trajectory:")
    for step in range(max_photon_range):
        # Update position based on direction
        pos[0] += direction_y  # Adjust for row (North-South)
        pos[1] += direction_x  # Adjust for column (East-West)

        # Check if photon goes out of bounds
        if pos[0] < 0 or pos[0] >= SECTOR_SIZE or pos[1] < 0 or pos[1] >= SECTOR_SIZE:
            print("Photon went out of bounds!")
            break

        print(f"Photon at position ({pos[0]}, {string.ascii_uppercase[pos[1]]})")

        # Check if the photon hits an enemy
        if pos in enemies_in_areas[tuple(current_area)]:
            enemies_in_areas[tuple(current_area)].remove(pos)
            areas[current_area[0]][current_area[1]][pos[0]][pos[1]] = EMPTY_SPACE
            remaining_enemies -= 1
            print(f"Photon hit an enemy at position ({pos[0]}, {string.ascii_uppercase[pos[1]]})!")
            break
    else:
        print("Photon missed!")

    photons -= 1
    energy -= 2
    input("\nPress Enter to continue...")
    user_action_count += 1
    check_enemy_counterattack()

# Recover energy gradually after each turn
def recharge_energy(percentage):
    global energy
    recharge_amount = int(energy * (percentage / 100))
    energy = min(energy + recharge_amount, 100)  # Cap at 100
    print(f"Recharging {percentage}% energy...")

# Enemy counterattack every 2 user actions
def check_enemy_counterattack():
    global user_action_count, energy
    if user_action_count >= 2:
        print("\nAn enemy ship fires back!")
        damage = random.randint(5, 15)
        energy -= damage
        print(f"You've been hit! Lost {damage} energy. Current energy: {energy}")
        user_action_count = 0  # Reset counter
        input("\nPress Enter to continue...")

# Check if all enemies in all areas are destroyed
def check_victory():
    return remaining_enemies == 0

# Main game loop
def game_loop():
    global energy
    populate_areas()
    
    while energy > 0 and (torpedoes > 0 or photons > 0):
        display_sector_grid()
        
        if check_victory():
            print("Congratulations! You destroyed all enemies in all areas.")
            break
        
        print("Move with 'w', 'a', 's', 'd', fire torpedo with 'f', fire photon with 'p' (angle), warp speed with 'warp', radar scan with 'radar', long-range sensor with 'sensor', or exit with 'exit':")
        action = input("Action: ").lower()
        
        if action in ['w', 'a', 's', 'd']:
            move_in_sector(action)
        elif action == 'f':
            fire_torpedo()
        elif action == 'p':
            fire_photon()
        elif action == 'warp':
            warp_to_area()
        elif action == 'radar':
            radar()
        elif action == 'sensor':
            long_range_sensor()
        elif action == 'exit':
            print("Exiting game. Goodbye!")
            break
        else:
            print("Invalid action!")

        # Recharge energy after each action
        recharge_energy(percentage=5)
        
        if energy <= 0:
            print("You have run out of energy. Game Over!")
            break
        elif torpedoes <= 0 and photons <= 0:
            print("You have run out of weapons. Game Over!")
            break

# Start the game
if __name__ == "__main__":
    print("Welcome to the Star Trek ASCII Game!")
    game_loop()
