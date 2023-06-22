class RGVSystemConfig:
    def __init__(self, RGV_clean_time, RGV_movement_1_time, RGV_movement_2_time, RGV_movement_3_time):
        self.__RGV_clean_time = RGV_clean_time
        self.__RGV_movement_1_time = RGV_movement_1_time
        self.__RGV_movement_2_time = RGV_movement_2_time
        self.__RGV_movement_3_time = RGV_movement_3_time
    
    @property
    def RGV_clean_time(self):
        return self.__RGV_clean_time
    
    @property
    def RGV_movement_1_time(self):
        return self.__RGV_movement_1_time

    @property
    def RGV_movement_2_time(self):
        return self.__RGV_movement_2_time

    @property
    def RGV_movement_3_time(self):
        return self.__RGV_movement_3_time
