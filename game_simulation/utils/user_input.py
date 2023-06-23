from inputimeout import inputimeout, TimeoutOccurred

def inspire_agent(agents):

    # List all the agents
    for index, agent in enumerate(agents):
        print(f"{index}: {agent.name}")

    # Who needs inspiration? Allow 4 seconds for a selection
    try:
        agent = inputimeout(prompt='Who do you want to inspire? : ', timeout=4)
    except TimeoutOccurred:
        return None

    # Give specific inspiration
    agent = agents[int(agent)]
    agent.inspiration = input("What do want this agent to do? : ")
    return agent


    