import torch
import json
import matplotlib.pyplot as plt
import networkx as nx
from agents.agent import Agent
from locations.locations import Locations
from utils.text_generation import summarize_simulation
from utils.user_input import inspire_agent

print("Using Pytorch version: " + torch.__version__)
print("CUDA available?: " + str(torch.cuda.is_available()))
print("CUDA version: {}".format(torch.version.cuda))
# print("Total GPU memory: " + str(torch.cuda.get_device_properties(device).total_memory))

# Set default value for prompt_meta if not defined elsewhere
prompt_meta = '### Instruction:\n{}\n### Response:'

# Initialize global time and simulation variables
global_day  = 0   # number of days since the simulation began
global_time = 7   # current hour of the day, 0-23
hours_of_simulation = 12

log_locations = True
log_actions = True
log_plans = True
log_ratings = True
log_memories = True

print_locations = True
print_actions = True
print_plans = True
print_ratings = True
print_memories = True

use_openai = False 

# Start simulation loop
whole_simulation_output = ""

# Load town areas and people from JSON file
with open('simulation_config.json', 'r') as f:
    town_data = json.load(f)

town_people = town_data['town_people']
town_areas = town_data['town_areas']

# Create world_graph
world_graph = nx.Graph()
last_town_area = None
for town_area in town_areas.keys():
    world_graph.add_node(town_area)
    world_graph.add_edge(town_area, town_area)  # Add an edge to itself
    if last_town_area is not None:
        world_graph.add_edge(town_area, last_town_area)
    last_town_area = town_area


# Add the edge between the first and the last town areas to complete the cycle
world_graph.add_edge(list(town_areas.keys())[0], last_town_area)

# Draw the graph
nx.draw(world_graph, with_labels=True, node_color='lightblue', edge_color='gray')

# Show the plot
plt.show()

# Initialize agents and locations
agents = []
locations = Locations()

for name, description in town_people.items():
    starting_location = description['starting_location']
    agents.append(Agent(name, description['description'], starting_location, world_graph, use_openai))

for name, description in town_areas.items():
    locations.add_location(name, description)

for game_hour in range(global_time, global_time+hours_of_simulation):

    log_output = ""

    # Show the map
    print(f"====================== REPEAT {game_hour} ======================\n")
    locations.show_map(print_locations, log_locations)
    
    # Prompt from user to a single agent. We call this inspiration
    agent_to_inspire = inspire_agent(agents)

    # Each agent plans actions
    for agent in agents:
        agent.plan(global_time, prompt_meta)
        agent.diary_entry("Plans", log_plans, print_plans)
    
    # Execute planned actions and update memories
    for agent in agents:

        # Execute action
        action = agent.execute_action(agents, locations.get_location(agent.location), global_time, town_areas, prompt_meta)
        agent.diary_entry("Action", log_actions, print_actions, action)

        # Update memories: all other agents remember what the agent does
        for other_agent in agents:
            if other_agent != agent:

                # other_agent.form_short_term_memory(global_day, global_time, agent, action )
                # other_agent.diary_entry("Memory", global_day, global_time, agent, action )

                memory = f'[Time: {global_time}. Person: {agent.name}. Memory: {action}]'
                other_agent.memories.append(memory)
                      
                if log_memories:
                    log_output += f"{other_agent.name} remembers: {memory}\n"
                    if print_memories:
                        print(f"{other_agent.name} remembers: {memory}\n")

        # Compress and rate memories for each agent
        for agent in agents:
            agent.compress_memories(global_time)
            agent.rate_memories(locations, global_time, prompt_meta)
            if log_ratings:
                log_output += f"{agent.name} memory ratings: {agent.memory_ratings}\n"
                if print_ratings:
                    print(f"{agent.name} memory ratings: {agent.memory_ratings}\n")

    # Rate locations and determine where agents will go next
    for agent in agents:
        place_ratings = agent.rate_locations(locations, global_time, prompt_meta)
        if log_ratings:
            log_output += f"=== UPDATED LOCATION RATINGS {global_time} FOR {agent.name}===\n"
            log_output += f"{agent.name} location ratings: {place_ratings}\n"
            if print_ratings:
                print(f"=== UPDATED LOCATION RATINGS {global_time} FOR {agent.name}===\n")
                print(f"{agent.name} location ratings: {place_ratings}\n")
        
        old_location = agent.location

        new_location_name = place_ratings[0][0]
        agent.move(new_location_name)

        if print_locations:
            log_output += f"=== UPDATED LOCATIONS AT TIME {global_time} FOR {agent.name}===\n"
            log_output += f"{agent.name} moved from {old_location} to {new_location_name}\n"
        if print_ratings:
            print(f"=== UPDATED LOCATIONS AT TIME {global_time} FOR {agent.name}===\n")
            print(f"{agent.name} moved from {old_location} to {new_location_name}\n")
   
    print(f"----------------------- SUMMARY FOR REPEAT {game_hour} -----------------------")

    print(summarize_simulation(log_output=log_output))

    whole_simulation_output += log_output

    # Increment time
    global_time += 1


# Write log output to file
with open('simulation_log.txt', 'w') as f:
    f.write(whole_simulation_output)