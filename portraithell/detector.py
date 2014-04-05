class Detector(object):
    def detect(self, images):
        score = sum(map(self.check_image, images))
        return score >= 0.5 * len(images)

    def check_image(self, image):
        img_w, img_h = image.size
        check_ratios = (3. / 4., 9. / 16.)
        for check_ratio in check_ratios:
            potential_gap = int(0.5 * img_h * check_ratio) - 1  # minus fudge
            bounds = (
                (0, 0, potential_gap, img_h),
                (img_w - potential_gap, 0, img_w, img_h)
            )
            both_black = True
            for box in bounds:
                both_black = both_black and self.is_all_black(image.crop(box))
            if both_black:
                return True
        return False

    def is_all_black(self, image):
        extrema = image.getextrema()
        return extrema == ((0, 0), (0, 0), (0, 0))
