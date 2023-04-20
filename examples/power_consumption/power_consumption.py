import airsim
from time import sleep

# Get rotor Thrust, torque and speed 
def getRotorStates(rotor_number):
    return client.getRotorStates().rotors[rotor_number]

# Power = Thrust * torque * speed
def getPowerRotor(rotor_number):
    speed = client.getRotorStates().rotors[rotor_number]['speed']
    thrust = speed = client.getRotorStates().rotors[rotor_number]['thrust']
    torque = abs(client.getRotorStates().rotors[rotor_number]['torque_scaler'])

    Pi = speed * thrust * torque #Instantaneous power
    return Pi

if __name__ == '__main__':
    client = airsim.MultirotorClient() 
    client.confirmConnection()
    Pt = 0 # Total consumed power
    while 1:
        Pi = [0, 0, 0, 0]
        for rotor_number in range(4):
            Pi[rotor_number] = (getPowerRotor(rotor_number))
        print("Pi = {}\n".format(Pi))
        Pt = Pt + sum(Pi)
        print("Pt = {}\n".format(Pt))

