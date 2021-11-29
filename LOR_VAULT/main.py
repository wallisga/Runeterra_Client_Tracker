from sys import exit
from mem import App_Memory
from window import Window

def main():
	running = True

	memory = App_Memory()
	window = Window()
	window.display_state(memory.state_check(), memory)
	while running:
		state = memory.state_check()
		if state:
			window.display_state(state, memory)
		window.update()

if __name__ == '__main__':
	exit(main())