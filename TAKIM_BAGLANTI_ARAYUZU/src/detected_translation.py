class DetectedTranslation:
    def __init__(self,
                 translation_x: float,
                 translation_y: float,

                 ):

        self.translation_x = translation_x
        self.translation_y = translation_y

    def create_payload(self):
        return {
                'translation_x': str(self.translation_x),
                'translation_y': str(self.translation_y)
                }