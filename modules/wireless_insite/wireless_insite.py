from kernel.module import module
from Caviar_WI import main



print("Definindo classe wireless_insite")
class wireless_insite(module):
    """
    This class is used to control the wireless_insite module.
    """

    def _do_init(self):
        pass

    async def _execute_step(self):
        '''
        Look, you can only this shit if you have a WI license. So, please, check the wireless.json
        And fill this
        
        '''
        data = self.buffer.get()
        
        airsim_data = data[0][1]['fakedrone']
        position = [airsim_data['x-pos'], airsim_data['y-pos'], airsim_data['z-pos']]
        orientation = [airsim_data['orientation']['x-ori'], airsim_data['orientation']['y-ori'], airsim_data['orientation']['z-ori']]
        run = int(airsim_data['run'])

        main(positions=position, rotations=orientation, step=run)

        print(len(self.buffer))

