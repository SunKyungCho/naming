
def extractIntent(line):
    intent_char = ' \t'
    pos = 0
    for ch in line:
        if ch not in intent_char:
            break
        pos = pos + (4 if ch == '\t' else 1)
    return pos


def main():
	a = "\tlkjsdf\tlkjsdf"
	print extractIntent(a)

if __name__ == '__main__':
	main()