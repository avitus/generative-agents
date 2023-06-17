def inspire_agent(agents):
    for index, agent in enumerate(agents):
        print(f"{index}: {agent.name}")
    agent = input("Who do you want to inspire?")
    return agent
    