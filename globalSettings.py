#place where global variables and methods are sored

def initPlayer():

    #defines witch direction the player is facing (0 = right, 1 = left)
    global direction
    direction = 0

    #variables to handle jumping
    global jumpDelay
    jumpDelay = False
    global jumpForce
    jumpForce = 100

    #variables to handle gravity
    global grounded
    grounded = True
    global gravForce
    gravForce = 1