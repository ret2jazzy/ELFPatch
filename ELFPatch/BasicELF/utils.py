
def page_start(address):
    return (address & -0x1000)

def page_end(address):
    return (address & -0x1000)+0x1000
