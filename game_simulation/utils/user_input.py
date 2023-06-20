def inspire_agent(agents):
    for index, agent in enumerate(agents):
        print(f"{index}: {agent.name}")
    agent = input("Who do you want to inspire? ")
    if agent == 'None':
        return None
    else:
        agent = agents[int(agent)]
        agent.inspiration = input("What do want this agent to do? ")
        return agent
    