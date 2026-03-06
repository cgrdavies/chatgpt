from wrapper import ChatGPT

proxies = [line.strip() for line in open('proxies.txt') if line.strip()]
print(ChatGPT(proxy_pool=proxies).ask_question("What is the best budget wireless mouse to buy in March 2026?", search=True))
